#!/usr/bin/env python3
"""Validador do feed unificado de deals (o contrato do canal com o GPT).

Em português simples: pega o JSON que o dashboard vai consumir e responde
"esse arquivo está no formato combinado?" — checando não só os campos, mas os
**invariantes da frota** (margem bruta na base compra, os 2 links por linha,
preço nunca inventado, `qtd` nulo quando a fonte não informa estoque).

Stdlib pura, offline, sem dependência — os DOIS lados podem rodar:

    python validate_feed.py caminho/do/feed.json
    python validate_feed.py --exemplo          # valida o exemplo do repo

Sai com código 0 se o feed está conforme, 1 se há problema (lista no stdout).
Contrato humano: ../CONTRATO-DE-DADOS.md · schema: schemas/dashboard-feed.schema.json
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
EXEMPLO = HERE / "exemplos" / "dashboard-feed.example.json"

SCHEMA_VERSION = 1
FONTES = {"MYP", "CardTrader", "COMC", "Liga"}
STATUS = {"ok", "falhou", "timeout", "pulado", "indisponível"}
UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

# Tolerância da conferência de margem: o store guarda float cru, a entrega
# arredonda 1 casa — 0.6 p.p. (ou 1% do valor) absorve arredondamento sem
# deixar passar margem calculada na base ERRADA (revenda em vez de compra),
# que erra na casa das dezenas de p.p.
def _tol(valor: float) -> float:
    return max(0.6, abs(valor) * 0.01)


def _num(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _check_link(url: Any, campo: str, onde: str, probs: list[str]) -> bool:
    if not isinstance(url, str):
        probs.append(f"{onde}: {campo} deve ser string (veio {type(url).__name__})")
        return False
    if not url:
        return False
    if not url.startswith(("http://", "https://")):
        probs.append(f"{onde}: {campo} não parece URL ({url!r}) — link é lido do artefato, nunca fabricado")
    return True


def validate_source(src: Any, i: int) -> list[str]:
    onde = f"sources[{i}]"
    probs: list[str] = []
    if not isinstance(src, dict):
        return [f"{onde}: deveria ser objeto"]
    if not isinstance(src.get("source"), str) or not src.get("source"):
        probs.append(f"{onde}: 'source' obrigatório (nome da fonte)")
    status = src.get("status")
    if status not in STATUS:
        probs.append(f"{onde}: status inválido {status!r} — use um de {sorted(STATUS)}")
    for campo in ("deals_raw", "deals_kept"):
        v = src.get(campo)
        if v is not None and (not isinstance(v, int) or isinstance(v, bool) or v < 0):
            probs.append(f"{onde}: {campo} deve ser inteiro >= 0")
    raw, kept = src.get("deals_raw"), src.get("deals_kept")
    if isinstance(raw, int) and isinstance(kept, int) and kept > raw:
        probs.append(f"{onde}: deals_kept ({kept}) > deals_raw ({raw})")
    return probs


def validate_deal(deal: Any, i: int) -> list[str]:
    onde = f"deals[{i}]"
    probs: list[str] = []
    if not isinstance(deal, dict):
        return [f"{onde}: deveria ser objeto"]

    if deal.get("fonte") not in FONTES:
        probs.append(f"{onde}: fonte inválida {deal.get('fonte')!r} — use uma de {sorted(FONTES)}")
    if not isinstance(deal.get("carta"), str) or not deal.get("carta", "").strip():
        probs.append(f"{onde}: 'carta' obrigatório e não vazio")

    for campo in ("compra_brl", "ref_brl"):
        if not _num(deal.get(campo)):
            probs.append(f"{onde}: {campo} deve ser número")
    if not _num(deal.get("margem_pct")):
        probs.append(f"{onde}: margem_pct deve ser número (PERCENT, base compra)")

    compra = deal.get("compra_brl")
    ref = deal.get("ref_brl")
    margem = deal.get("margem_pct")

    if _num(compra) and compra <= 0:
        probs.append(f"{onde}: compra_brl deve ser > 0 (preço 0/ausente nunca vira deal)")

    # Invariante 4 da frota: nunca inventar preço. Margem sem referência real
    # significa número fabricado em algum ponto do caminho.
    if _num(ref) and ref <= 0 and _num(margem) and margem != 0:
        probs.append(f"{onde}: margem {margem} sem ref_brl (>0) — preço de referência nunca é inventado")

    # Invariante 1: margem BRUTA na base COMPRA, sem taxa embutida.
    if _num(compra) and compra > 0 and _num(ref) and _num(margem):
        esperado = (ref - compra) / compra * 100.0
        if abs(esperado - margem) > _tol(esperado):
            probs.append(
                f"{onde}: margem_pct {margem} não bate com a base COMPRA "
                f"(esperado {esperado:.1f} a partir de compra_brl {compra} e ref_brl {ref}) — "
                f"conferir se a fonte não veio na base revenda ou com taxa embutida"
            )

    lucro = deal.get("lucro_brl")
    if _num(lucro) and _num(compra) and _num(ref) and abs((ref - compra) - lucro) > 0.02:
        probs.append(f"{onde}: lucro_brl {lucro} != ref_brl − compra_brl ({ref - compra:.2f})")

    qtd = deal.get("qtd", None)
    if qtd is not None and (not isinstance(qtd, int) or isinstance(qtd, bool) or qtd < 0):
        probs.append(f"{onde}: qtd deve ser inteiro >= 0 ou null (null = fonte não informa estoque)")

    notas = deal.get("notas", [])
    if not isinstance(notas, list) or any(not isinstance(n, str) for n in notas):
        probs.append(f"{onde}: notas deve ser lista de strings (flags da linha — exibidas na entrega)")

    # Invariante 7: dois links por linha. Zero link = linha que o operador não
    # consegue validar em lugar nenhum.
    tem_oferta = _check_link(deal.get("link_oferta", ""), "link_oferta", onde, probs)
    tem_tcg = _check_link(deal.get("link_tcg", ""), "link_tcg", onde, probs)
    if not tem_oferta and not tem_tcg:
        probs.append(f"{onde}: linha sem nenhum link (invariante: [oferta] + [TCG] em toda linha)")

    return probs


def validate_feed(feed: Any) -> list[str]:
    """Devolve a lista de problemas do feed. Lista vazia = conforme."""
    probs: list[str] = []
    if not isinstance(feed, dict):
        return ["feed: o topo deveria ser um objeto JSON"]

    if feed.get("schema_version") != SCHEMA_VERSION:
        probs.append(f"schema_version: esperado {SCHEMA_VERSION}, veio {feed.get('schema_version')!r}")

    gen = feed.get("generated_utc")
    if not isinstance(gen, str) or not UTC_RE.match(gen):
        probs.append(f"generated_utc: esperado 'AAAA-MM-DDTHH:MM:SSZ', veio {gen!r}")

    fx = feed.get("fx")
    if not _num(fx) or fx <= 0:
        probs.append(f"fx: câmbio deve ser número > 0 (veio {fx!r}) — sem câmbio real o run falha alto, não chuta")

    if not _num(feed.get("min_margin_pct")):
        probs.append("min_margin_pct: obrigatório (PERCENT, ex. 30)")

    scope = feed.get("scope")
    if scope is not None and not (isinstance(scope, str) or isinstance(scope, list)):
        probs.append("scope: lista de códigos canônicos ou string de profile")

    sources = feed.get("sources")
    if not isinstance(sources, list):
        probs.append("sources: obrigatório (status honesto por fonte — fonte que falhou nunca some)")
    else:
        for i, s in enumerate(sources):
            probs.extend(validate_source(s, i))

    deals = feed.get("deals")
    if not isinstance(deals, list):
        probs.append("deals: obrigatório (lista, mesmo que vazia)")
        return probs

    count = feed.get("deal_count")
    if isinstance(count, int) and not isinstance(count, bool) and count != len(deals):
        probs.append(f"deal_count {count} != len(deals) {len(deals)}")

    for i, d in enumerate(deals):
        probs.extend(validate_deal(d, i))
    return probs


def main(argv: list[str]) -> int:
    args = argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    caminho = EXEMPLO if args[0] == "--exemplo" else Path(args[0])
    try:
        feed = json.loads(caminho.read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"não consegui ler {caminho}: {exc}")
        return 2
    except json.JSONDecodeError as exc:
        print(f"{caminho}: JSON inválido — {exc}")
        return 2

    probs = validate_feed(feed)
    if not probs:
        n = len(feed.get("deals", []))
        print(f"OK — {caminho.name}: {n} deal(s), formato e invariantes conforme o contrato.")
        return 0
    print(f"{len(probs)} problema(s) em {caminho.name}:")
    for p in probs:
        print(f"  - {p}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
