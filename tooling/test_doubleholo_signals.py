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
