"""Testes do validador do feed do canal GPT-dashboard.

Rodar:  cd integrations/gpt-dashboard && python -m pytest test_validate_feed.py -q
100% offline, stdlib pura.
"""
import copy
import json
from pathlib import Path

from validate_feed import validate_feed

HERE = Path(__file__).resolve().parent
EXEMPLO = json.loads((HERE / "exemplos" / "dashboard-feed.example.json").read_text(encoding="utf-8"))


def _feed():
    return copy.deepcopy(EXEMPLO)


def _tem(probs, trecho):
    return any(trecho in p for p in probs)


def test_exemplo_do_repo_e_conforme():
    assert validate_feed(_feed()) == []


def test_topo_nao_objeto():
    assert validate_feed([]) and validate_feed(None)


def test_schema_version_errada():
    f = _feed(); f["schema_version"] = 2
    assert _tem(validate_feed(f), "schema_version")


def test_generated_utc_malformado():
    f = _feed(); f["generated_utc"] = "20/08/2026 13:05"
    assert _tem(validate_feed(f), "generated_utc")


def test_fx_zero_ou_negativo_reprova():
    for fx in (0, -5.2, "5.2", None):
        f = _feed(); f["fx"] = fx
        assert _tem(validate_feed(f), "fx"), fx


def test_deal_count_divergente():
    f = _feed(); f["deal_count"] = 99
    assert _tem(validate_feed(f), "deal_count")


def test_fonte_desconhecida():
    f = _feed(); f["deals"][0]["fonte"] = "eBay"
    assert _tem(validate_feed(f), "fonte inválida")


def test_margem_na_base_errada_e_detectada():
    # Base REVENDA: (ref-compra)/ref = 40% quando a base compra daria 66.7%.
    f = _feed()
    d = f["deals"][1]
    d["margem_pct"] = (d["ref_brl"] - d["compra_brl"]) / d["ref_brl"] * 100.0
    assert _tem(validate_feed(f), "base COMPRA")


def test_arredondamento_de_1_casa_passa():
    f = _feed()
    d = f["deals"][1]
    d["margem_pct"] = 66.7  # exato seria 66.666...
    assert validate_feed(f) == []


def test_margem_sem_referencia_reprova():
    f = _feed()
    d = f["deals"][0]
    d["ref_brl"] = 0.0
    d["ref_usd"] = 0.0
    assert _tem(validate_feed(f), "nunca é inventado")


def test_compra_zero_reprova():
    f = _feed(); f["deals"][0]["compra_brl"] = 0
    assert _tem(validate_feed(f), "compra_brl")


def test_lucro_incoerente_reprova():
    f = _feed(); f["deals"][0]["lucro_brl"] = 999.0
    assert _tem(validate_feed(f), "lucro_brl")


def test_qtd_null_e_valido_mas_negativo_nao():
    f = _feed()
    f["deals"][0]["qtd"] = None
    assert validate_feed(f) == []
    f["deals"][0]["qtd"] = -1
    assert _tem(validate_feed(f), "qtd")


def test_linha_sem_nenhum_link_reprova():
    f = _feed()
    f["deals"][2]["link_oferta"] = ""
    f["deals"][2]["link_tcg"] = ""
    assert _tem(validate_feed(f), "sem nenhum link")


def test_um_link_so_passa_mas_url_fabricada_nao():
    f = _feed()
    f["deals"][2]["link_tcg"] = ""      # só o link de oferta: ok (célula mostra o que existe)
    assert validate_feed(f) == []
    f["deals"][2]["link_oferta"] = "www.sem-esquema.com/x"   # não parece URL
    assert _tem(validate_feed(f), "não parece URL")


def test_status_de_fonte_invalido():
    f = _feed(); f["sources"][0]["status"] = "quebrou"
    assert _tem(validate_feed(f), "status inválido")


def test_kept_maior_que_raw_reprova():
    f = _feed()
    f["sources"][0]["deals_raw"] = 1
    f["sources"][0]["deals_kept"] = 5
    assert _tem(validate_feed(f), "deals_kept")


def test_notas_nao_lista_reprova():
    f = _feed(); f["deals"][0]["notas"] = "validar"
    assert _tem(validate_feed(f), "notas")


def test_feed_vazio_com_zero_deals_e_valido():
    f = _feed()
    f["deals"] = []
    f["deal_count"] = 0
    assert validate_feed(f) == []
