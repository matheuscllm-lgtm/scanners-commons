#!/usr/bin/env python3
"""
doubleholo_signals.py  —  PIPELINE consolidado (2026-06-27)

Lado PYTHON da integração DoubleHolo. Faz a "cola" entre:
  - o DOM-scraper JS (`~/doubleholo-scraper/doubleholo_scraper.js`) = LEITOR premium
    canônico (lê o DOM logado, SEM token), e
  - a frota de scanners (Python).

>>> Preço de referência = TCGplayer (não aqui). Este lado só lida com SINAIS. <<<
>>> Leitura premium = DOM-scraper JS. Aqui NÃO se chama a API com token         <<<
>>> (harvest de token é bloqueado de propósito; DOM-scrape não precisa).         <<<

Ver: ~/scanners-commons/HANDOFF-DOUBLEHOLO.md  e  ~/doubleholo-scraper/HANDOFF.md

--------------------------------------------------------------------------------
DUAS FUNÇÕES (o que sobrou após a reconciliação das 2 sessões)
--------------------------------------------------------------------------------
  1. DISCOVER  — descobre card_id por set no marketplace público (Firecrawl),
                 headless, sem navegador. (numero -> card_id/url)
  2. INGEST    — lê o JSON cru que o DOM-scraper baixa e normaliza pro SCHEMA
                 CANÔNICO que os caminhos 2 (outlook) e 1 (2ª análise) consomem.

SCHEMA CANÔNICO (1 registro por carta):
  {
    "source":"doubleholo", "card_id", "name", "set", "number",
    "market_price_usd": float|None, "price_change_pct": float|None,
    "offer_url", "reference_url",                # reference_url = TCGplayer
    "signals": {
        "psa10_pop": int|None, "total_pop": int|None,
        "gem_rate": float|None,                  # FRAÇÃO 0-1  -> psa-arbitrage --psa10-prob
        "gem_rate_pct": float|None,              # % p/ exibição
        "best_roi_pct": float|None,
        "forecast": str|None, "forecast_dir": "buy"|"sell"|"neutral",
        "ai_grade": str|None, "ai_signal": str|None,
        "pop_mismatch": bool
    },
    "flags": [..]
  }

USO:
  python doubleholo_signals.py discover --set "Ascended Heroes" --numbers 276,284
  python doubleholo_signals.py ingest dh_card_1513.json            # 1 arquivo
  python doubleholo_signals.py ingest doubleholo_5cards.json --json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request

# Console Windows é cp1252 e quebra em ⚠/→ (ver memória windows_python_setup).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

FIRECRAWL_ENDPOINT = "https://api.firecrawl.dev/v2/scrape"
SITE = "https://doubleholo.com"
DEFAULT_MAX_AGE_MS = 6 * 60 * 60 * 1000


# --------------------------------------------------------------------------- #
# 1) DISCOVER — card_id por set (marketplace público via Firecrawl)
# --------------------------------------------------------------------------- #
def firecrawl_markdown(url: str, *, wait_ms: int = 5000) -> str:
    key = os.environ.get("FIRECRAWL_API_KEY")
    if not key:
        raise RuntimeError("FIRECRAWL_API_KEY não setada (precisa pra descobrir card_id).")
    payload = {"url": url, "formats": ["markdown"], "onlyMainContent": True,
               "waitFor": wait_ms, "maxAge": DEFAULT_MAX_AGE_MS}
    req = urllib.request.Request(
        FIRECRAWL_ENDPOINT, data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST")
    with urllib.request.urlopen(req, timeout=90) as resp:
        body = json.loads(resp.read().decode())
    if not body.get("success"):
        raise RuntimeError(f"Firecrawl falhou em {url}: {body.get('error') or body}")
    md = (body.get("data") or {}).get("markdown")
    if not md:
        raise RuntimeError(f"Firecrawl sem markdown em {url}")
    return md


_CARD_LINK_RE = re.compile(r"https://doubleholo\.com/card/(\d+)/([a-z0-9\-]+)")
_NUM_TAIL_RE = re.compile(r"-(\d+)$")


def discover_set(set_name: str, max_pages: int = 2) -> dict:
    index = {}
    for page in range(1, max_pages + 1):
        params = {"sets": f"Pokemon {set_name}"}
        if page > 1:
            params["page"] = str(page)
        md = firecrawl_markdown(f"{SITE}/marketplace?{urllib.parse.urlencode(params)}")
        before = len(index)
        for m in _CARD_LINK_RE.finditer(md):
            cid, slug = m.group(1), m.group(2)
            num_m = _NUM_TAIL_RE.search(slug)
            if not num_m:
                continue
            ctx = md[max(0, m.start() - 600): m.start()]
            name_m = re.findall(r"\*\*(.+?)\*\*", ctx)
            index.setdefault(num_m.group(1), {
                "card_id": cid, "number": num_m.group(1),
                "name": name_m[-1].strip() if name_m else None,
                "url": f"{SITE}/card/{cid}/{slug}",
            })
        if len(index) == before:
            break
    return index


# --------------------------------------------------------------------------- #
# 2) INGEST — normaliza o JSON do DOM-scraper pro schema canônico
# --------------------------------------------------------------------------- #
def _money(s):
    if s is None:
        return None
    m = re.search(r"-?\$?([\d,]+\.?\d*)", str(s))
    return float(m.group(1).replace(",", "")) if m else None


def _pct(s):
    if s is None:
        return None
    m = re.search(r"([+-]?\d[\d,]*\.?\d*)\s*%", str(s))
    return float(m.group(1).replace(",", "")) if m else None


def _percentish(s):
    """Percentual tolerante: aceita "12%"/"+12.5%" E número puro (12, 12.5).

    Para os campos que o schema do scraper define como percentuais (bestROI,
    gemRate, priceChangePct). Se um dia o scraper deixar de pôr o '%', o sinal
    NÃO some calado (follow-up #3) — é parseado igual. Um valor com cifrão é
    rejeitado (None) pra nunca cruzar com o campo de preço (esse vai por _money).
    """
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return float(s)
    p = _pct(s)
    if p is not None:
        return p
    t = str(s).strip()
    if "$" in t:
        return None
    m = re.search(r"[+-]?\d[\d,]*\.?\d*", t)
    return float(m.group(0).replace(",", "")) if m else None


def _int(s):
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return int(s)
    d = re.sub(r"[^\d]", "", str(s))  # tira separador de milhar "." ou ","
    return int(d) if d else None


def _tcg_product_id(reference_url):
    """productId do TCGPlayer a partir do reference_url do DoubleHolo.

    É a CHAVE DE JOIN com a frota: o reference_url é tcgplayer.com/product/<id>
    e os repos (outlook, etc.) indexam a carta por esse mesmo productId.
    """
    if not reference_url:
        return None
    m = re.search(r"tcgplayer\.com/product/(\d+)", str(reference_url))
    return m.group(1) if m else None


def forecast_dir(forecast: str | None) -> str:
    f = (forecast or "").lower()
    if "buy" in f:
        return "buy"
    if "sell" in f:
        return "sell"
    return "neutral"


# --- dh_score: SINGLE SOURCE da nota "2ª opinião Double Holo" -----------------
# Consumida pelo outlook (coluna DH) e pelo caminho 1 (2ª análise de deals).
# 50 = neutro. >50 = Double Holo otimista; <50 = pessimista. None = sem sinal.
# Racional aberto (pesos fáceis de ajustar):
#   base 50; forecast_dir buy+20/sell-20; ai_signal Buy+12/Sell-12;
#   ai_grade Yes+8/Maybe+4; best_roi_pct ≥300+10/≥150+7/≥50+4;
#   price_change ≥+10%+8/>0+4/≤-10%-8/<0-4  -> clamp 0-100.
_FORECAST_PTS = {"buy": 20, "sell": -20}
_SIGNAL_PTS = {"buy": 12, "sell": -12}
_GRADE_PTS = {"yes": 8, "maybe": 4}


def dh_score(signals: dict | None) -> int | None:
    if not signals:
        return None
    fdir = (signals.get("forecast_dir") or "neutral").lower()
    ai = (signals.get("ai_signal") or "").lower()
    grade = (signals.get("ai_grade") or "").lower()
    roi = signals.get("best_roi_pct")
    mom = signals.get("price_change_pct")
    # `price_change_pct` (momentum) é dado PÚBLICO — existe mesmo deslogado. Ele
    # MODIFICA a nota, mas sozinho NÃO a qualifica: sem ao menos um sinal PREMIUM
    # (forecast/ai_signal/ai_grade/best_roi) não há "2ª opinião premium" — devolve
    # None (DH '—') em vez de fabricar uma nota só com variação de preço pública.
    has_premium_signal = fdir != "neutral" or bool(ai) or bool(grade) or roi is not None
    if not has_premium_signal:
        return None
    score = 50 + _FORECAST_PTS.get(fdir, 0) + _SIGNAL_PTS.get(ai, 0) + _GRADE_PTS.get(grade, 0)
    if roi is not None:
        score += 10 if roi >= 300 else 7 if roi >= 150 else 4 if roi >= 50 else 0
    if mom is not None:
        score += 8 if mom >= 10 else 4 if mom > 0 else -8 if mom <= -10 else -4 if mom < 0 else 0
    return max(0, min(100, score))


def normalize_record(raw: dict) -> dict:
    """JSON cru do DOM-scraper -> registro canônico."""
    prem = raw.get("premium") or {}
    psa10 = _int(prem.get("psa10"))
    total = _int(prem.get("totalGraded"))
    gem_pct = _percentish(prem.get("gemRate"))
    # gem_rate como FRAÇÃO (consumo do psa-arbitrage --psa10-prob)
    gem = (gem_pct / 100.0) if gem_pct is not None else (
        round(psa10 / total, 4) if (psa10 is not None and total) else None)

    flags = []
    pop_mismatch = bool(prem.get("popMismatch"))
    if psa10 is not None and total and gem_pct is not None:
        if abs(gem_pct - 100 * psa10 / total) > 1.0:
            pop_mismatch = True
    if pop_mismatch:
        flags.append("pop_mismatch: gem_rate exibido ≠ psa10/total — revisar")
    if not raw.get("premiumRendered", True):
        flags.append("premium NÃO renderizou (logar/abrir Card Insights antes de raspar)")
    ref_url = raw.get("referenceUrl")
    if not ref_url:
        flags.append("sem reference_url TCGplayer (trainer/sem produto) — não inventar")
    elif _tcg_product_id(ref_url) is None:
        # reference_url PRESENTE mas não é tcgplayer.com/product/<id> (link genérico:
        # busca/parceiro/rodapé) → sem productId, a chave de join. Flag explícita
        # p/ a perda não ser calada (o scraper já prefere o link de produto).
        flags.append("reference_url sem productId TCGplayer (link genérico, não /product/) — DH não casa")

    price_change_pct = _percentish(raw.get("priceChangePct"))
    signals = {
        "psa10_pop": psa10,
        "total_pop": total,
        "gem_rate": gem,
        "gem_rate_pct": gem_pct if gem_pct is not None else (round(100 * gem, 1) if gem is not None else None),
        "best_roi_pct": _percentish(prem.get("bestROI")),
        "forecast": prem.get("forecast"),
        "forecast_dir": forecast_dir(prem.get("forecast")),
        "ai_grade": prem.get("aiGrade"),
        "ai_signal": prem.get("aiSignal"),
        "price_change_pct": price_change_pct,  # momentum p/ dh_score (lido de signals)
        "pop_mismatch": pop_mismatch,
    }
    # dh_score (2ª opinião, single source). Se o premium NÃO renderizou (deslogado
    # / "Upgrade to unlock"), força None mesmo que dh_score() derivasse algo —
    # cinto-e-suspensório com o guard de sinal premium, p/ a nota e a flag
    # "premium NÃO renderizou" jamais se contradizerem (consumidores só LEEM a nota).
    dh = dh_score(signals)
    if not raw.get("premiumRendered", True):
        dh = None
    return {
        "source": "doubleholo",
        "card_id": raw.get("cardId"),
        "name": raw.get("name"),
        "set": raw.get("set"),
        "number": raw.get("number"),
        "market_price_usd": _money(raw.get("marketPrice")),
        "price_change_pct": price_change_pct,
        "offer_url": raw.get("offerUrl"),
        "reference_url": raw.get("referenceUrl"),  # TCGplayer (preço fica aqui)
        "tcg_product_id": _tcg_product_id(raw.get("referenceUrl")),  # JOIN key c/ a frota
        "dh_score": dh,   # 2ª opinião (single source); consumidores só LEEM
        "signals": signals,
        "flags": flags,
    }


def ingest_file(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = [data]
    return [normalize_record(r) for r in data]


# --------------------------------------------------------------------------- #
# Saída
# --------------------------------------------------------------------------- #
def print_signals_table(rows: list[dict]):
    print("\nDoubleHolo — SINAIS normalizados (schema canônico)")
    print("gem_rate -> psa-arbitrage --psa10-prob · forecast_dir/best_roi -> outlook --trend\n")
    hdr = f"{'#':>4}  {'Carta':<22} {'gem%':>6} {'pop(10/tot)':>12} {'bestROI':>9} {'fcst':>5} {'AI':>9}"
    print(hdr); print("-" * len(hdr))
    for r in rows:
        s = r["signals"]
        pop = f"{s['psa10_pop']}/{s['total_pop']}" if s["psa10_pop"] is not None and s["total_pop"] else "—"
        ai = f"{s['ai_grade'] or '?'}/{s['ai_signal'] or '?'}"
        print(f"{str(r.get('number') or ''):>4}  {(r.get('name') or '?')[:22]:<22} "
              f"{(str(s['gem_rate_pct'])+'%' if s['gem_rate_pct'] is not None else '—'):>6} "
              f"{pop:>12} {(str(s['best_roi_pct'])+'%' if s['best_roi_pct'] is not None else '—'):>9} "
              f"{s['forecast_dir'][:5]:>5} {ai[:9]:>9}")
        for fl in r["flags"]:
            print(f"        ⚠ {fl}")
    print()


def main(argv=None):
    ap = argparse.ArgumentParser(description="DoubleHolo pipeline (discover + ingest)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("discover", help="descobre card_id por set (Firecrawl, público)")
    d.add_argument("--set", required=True)
    d.add_argument("--numbers", help="filtra por números (vírgula); vazio = todos")
    d.add_argument("--max-pages", type=int, default=2)
    d.add_argument("--json", action="store_true")

    g = sub.add_parser("ingest", help="normaliza JSON do DOM-scraper -> schema canônico")
    g.add_argument("files", nargs="+", help="um ou mais JSON baixados pelo scraper")
    g.add_argument("--json", action="store_true")

    args = ap.parse_args(argv)

    if args.cmd == "discover":
        try:
            index = discover_set(args.set, max_pages=args.max_pages)
        except Exception as e:
            print(f"ERRO: {e}", file=sys.stderr); return 2
        wanted = [n.strip() for n in args.numbers.split(",")] if args.numbers else sorted(index, key=lambda x: int(x) if x.isdigit() else 0)
        result = {n: index.get(n) for n in wanted}
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"\n{len(index)} cartas no índice de '{args.set}'. Pedidas: {len(wanted)}")
            for n in wanted:
                e = index.get(n)
                print(f"  #{n}: " + (f"card_id={e['card_id']}  {e['name']}\n        {e['url']}" if e else "NÃO ENCONTRADA"))
            print("\n→ abra cada /card/<id> no Chrome logado e rode dhCard() (DOM-scraper) p/ os sinais premium.")
        return 0

    if args.cmd == "ingest":
        rows = []
        for p in args.files:
            try:
                rows.extend(ingest_file(p))
            except Exception as e:
                print(f"ERRO lendo {p}: {e}", file=sys.stderr)
        if not rows:
            return 1
        if args.json:
            print(json.dumps(rows, indent=2, ensure_ascii=False))
        else:
            print_signals_table(rows)
            withgem = sum(1 for r in rows if r["signals"]["gem_rate"] is not None)
            mism = sum(1 for r in rows if r["signals"]["pop_mismatch"])
            print(f"Resumo: {len(rows)} cartas · {withgem} com gem_rate · {mism} com pop_mismatch")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
