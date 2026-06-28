"""Testes do pipeline DoubleHolo (dh_score canônico + extração + normalização).

Rodar:  cd ~/scanners-commons/tooling && python -m pytest test_doubleholo_signals.py -q
"""
from doubleholo_signals import (_tcg_product_id, dh_score, forecast_dir,
                                normalize_record)


def _sig(**kw):
    base = {"forecast_dir": "neutral", "ai_signal": None, "ai_grade": None,
            "best_roi_pct": None, "price_change_pct": None}
    base.update(kw)
    return base


def test_dh_score_none_without_signal():
    assert dh_score(_sig()) is None
    assert dh_score({}) is None
    assert dh_score(None) is None


def test_dh_score_bullish_clamps_100():
    assert dh_score(_sig(forecast_dir="buy", ai_signal="Buy", ai_grade="Yes",
                         best_roi_pct=320, price_change_pct=15)) == 100


def test_dh_score_bearish_floor():
    assert dh_score(_sig(forecast_dir="sell", ai_signal="Sell", price_change_pct=-15)) == 10


def test_dh_score_tiers():
    assert dh_score(_sig(best_roi_pct=150)) == 57
    assert dh_score(_sig(best_roi_pct=40)) == 50
    assert dh_score(_sig(ai_grade="Maybe")) == 54


def test_forecast_dir():
    assert forecast_dir("Slightly favors buying") == "buy"
    assert forecast_dir("Strongly favors selling") == "sell"
    assert forecast_dir(None) == "neutral"


def test_tcg_product_id_extraction():
    assert _tcg_product_id("https://www.tcgplayer.com/product/83978") == "83978"
    assert _tcg_product_id("https://prices.pokemontcg.io/tcgplayer/sv1-1") is None
    assert _tcg_product_id(None) is None


def test_normalize_emits_dh_score_and_pid():
    raw = {
        "cardId": "1513", "name": "Brock's Rhydon", "set": "Pokemon Gym Heroes",
        "number": "2", "marketPrice": "$27.70", "priceChangePct": "+4.4%",
        "offerUrl": "https://doubleholo.com/card/1513",
        "referenceUrl": "https://www.tcgplayer.com/product/83978",
        "premiumRendered": True,
        "premium": {"psa10": 138, "totalGraded": 3392, "gemRate": "4.1%",
                    "bestROI": "+648.5%", "forecast": "Slightly favors buying",
                    "aiGrade": "Maybe", "aiSignal": "Buy"},
    }
    rec = normalize_record(raw)
    assert rec["tcg_product_id"] == "83978"
    assert rec["signals"]["psa10_pop"] == 138
    assert rec["signals"]["total_pop"] == 3392
    assert rec["signals"]["pop_mismatch"] is False  # 138/3392 ≈ 4.1% bate
    # dh_score = 50 + buy20 + Buy12 + Maybe4 + roi(648≥300)10 + mom(4.4>0)4 = 100
    assert rec["dh_score"] == 100


def test_normalize_flags_pop_mismatch_on_swapped_data():
    raw = {
        "cardId": "x", "name": "Y", "referenceUrl": "https://www.tcgplayer.com/product/1",
        "premiumRendered": True,
        "premium": {"psa10": 138, "totalGraded": 3, "gemRate": "4.1%"},  # total trocado (pré-fix)
    }
    rec = normalize_record(raw)
    assert rec["signals"]["pop_mismatch"] is True
    assert any("pop_mismatch" in f for f in rec["flags"])


def test_percentish_accepts_bare_number_when_scraper_drops_percent():
    """Robustez (follow-up #3): campos percentuais (bestROI/gemRate/priceChangePct)
    aceitam número puro além de "12%". Se o scraper algum dia parar de emitir o
    '%', o sinal NÃO some calado — é parseado igual."""
    raw = {
        "cardId": "x", "name": "Y",
        "referenceUrl": "https://www.tcgplayer.com/product/1",
        "premiumRendered": True,
        "priceChangePct": 4.4,  # número puro, SEM '%'
        "premium": {"psa10": 138, "totalGraded": 3392,
                    "gemRate": 4.1, "bestROI": 648.5,  # números puros
                    "forecast": "Slightly favors buying",
                    "aiGrade": "Maybe", "aiSignal": "Buy"},
    }
    rec = normalize_record(raw)
    assert rec["signals"]["best_roi_pct"] == 648.5
    assert rec["signals"]["gem_rate_pct"] == 4.1
    assert rec["price_change_pct"] == 4.4
    assert rec["signals"]["pop_mismatch"] is False  # 4.1 ≈ 138/3392
    # mesmo dh_score que a variante com "%" (test_normalize_emits_dh_score_and_pid)
    assert rec["dh_score"] == 100


def test_percentish_ignores_currency_strings():
    """_percentish NÃO deve confundir um valor monetário com percentual (cifrão
    presente → None), pra nunca cruzar com o campo de preço."""
    from doubleholo_signals import _percentish
    assert _percentish("$27.70") is None
    assert _percentish("12%") == 12.0
    assert _percentish("+4.4%") == 4.4
    assert _percentish(648.5) == 648.5
    assert _percentish(None) is None


def test_dh_score_none_when_only_public_momentum():
    """price_change_pct é dado PÚBLICO (lido fora do bloco premium do scraper).
    Sozinho NÃO qualifica como 2ª opinião premium → dh_score None. Sem isto, uma
    carta raspada deslogada (só com variação de preço pública) ganharia uma nota
    'premium' fabricada (ex.: 58) sem nenhum dado premium por trás."""
    assert dh_score(_sig(price_change_pct=35.9)) is None
    assert dh_score(_sig(price_change_pct=-12)) is None
    # momentum só MODIFICA quando há sinal premium (aqui forecast=buy):
    assert dh_score(_sig(forecast_dir="buy", price_change_pct=35.9)) == 78  # 50+20+8


def test_normalize_dh_score_none_when_premium_not_rendered():
    """premiumRendered=False (deslogado / 'Upgrade to unlock'): dh_score = None
    (DH '—'), NUNCA um número. O sinal cru público (momentum) segue disponível,
    só não vira nota — para a nota e a flag 'premium NÃO renderizou' não se
    contradizerem."""
    raw = {
        "cardId": "x", "name": "Y",
        "referenceUrl": "https://www.tcgplayer.com/product/1",
        "premiumRendered": False,
        "priceChangePct": "+35.9%",  # só dado público
        "premium": {},
    }
    rec = normalize_record(raw)
    assert rec["dh_score"] is None
    assert any("premium" in f.lower() for f in rec["flags"])
    assert rec["signals"]["price_change_pct"] == 35.9  # sinal cru preservado


def test_normalize_flags_reference_url_without_product_id():
    """referenceUrl PRESENTE mas sem /product/<id> (link tcgplayer genérico:
    busca/parceiro/rodapé) → tcg_product_id None E uma FLAG explícita. Sem a flag,
    a perda da chave de join seria calada (o guard antigo só flagava AUSÊNCIA)."""
    raw = {
        "cardId": "x", "name": "Y", "premiumRendered": True,
        "referenceUrl": "https://www.tcgplayer.com/search/pokemon/product?q=foo",
        "premium": {"forecast": "Slightly favors buying"},
    }
    rec = normalize_record(raw)
    assert rec["tcg_product_id"] is None
    assert any("product" in f.lower() for f in rec["flags"])


def test_int_handles_non_finite_floats():
    """_int não pode crashar com NaN/inf (int(nan)→ValueError, int(inf)→OverflowError)
    — um único registro com NaN abortaria a normalização do arquivo INTEIRO. Trata
    como None (campo ausente, honesto)."""
    from doubleholo_signals import _int
    assert _int(float("nan")) is None
    assert _int(float("inf")) is None
    assert _int(float("-inf")) is None
    assert _int(3392) == 3392
    assert _int(12.0) == 12
