# 📦 Pacote de contexto para o GPT (colar isto na conversa)

> **Operador:** este arquivo é autocontido — copie o conteúdo inteiro e cole na
> conversa/knowledge do GPT que está montando o dashboard. Junto dele, se
> possível, anexe `schemas/dashboard-feed.schema.json` e
> `exemplos/dashboard-feed.example.json`.

---

Você (GPT) está construindo um **dashboard integrativo** sobre uma frota de
scanners de arbitragem de cartas colecionáveis (Pokémon + Dragon Ball + One
Piece) e ferramentas afins, do operador Matheus. Este pacote é o seu contrato
com a frota. O canal oficial de comunicação é o diretório
`integrations/gpt-dashboard/` do repo privado `matheuscllm-lgtm/scanners-commons`
— seus pedidos e as respostas da frota são registrados lá como arquivos
markdown datados.

## Regras que o dashboard NÃO pode violar

1. **Margem é BRUTA, base COMPRA:** `(revenda − compra)/compra`, sem nenhuma
   taxa embutida (frete/cartão/IOF ficam por fora, com o operador). Nunca
   derive "margem líquida" nem embuta taxa.
2. **Nunca recomendar compra.** Sem botão/coluna "COMPRAR", sem "BUY NOW". O
   dashboard ranqueia, flagea e explica; capital é decisão do operador.
3. **Nunca inventar dado.** Preço/URL/campo que a fonte não deu = mostrar
   vazio/`—`/flag, jamais estimar ou completar.
4. **Real vs fallback sempre visível:** cada linha declara a fonte do preço de
   referência; fallback nunca aparece como preço real.
5. **Todas as linhas:** aprovadas E rejeitadas/em revisão, com motivo. Fonte que
   falhou aparece como falha, não some da tela (`ok (0 deals)` ≠ `indisponível`).
6. **Dois links por linha:** `[oferta]` (onde comprar) e `[TCG]`/`[referência]`
   (onde validar). URLs vêm do feed — nunca construídas por você.
7. **Piso R$50 só para singles; selados não têm piso.**
8. **Mostrar a idade do dado** (`generated_utc`): deal envelhece rápido.

## As duas armadilhas clássicas (já causaram bug real)

- **Threshold tem convenção OPOSTA por scanner:** percent inteiro (`30`) no
  MYP/Liga/eBay; **fração** (`0.30`) no CardTrader/COMC/Selados. Passar `30`
  para o CardTrader = pedir 3.000% = zero resultados sem erro.
- **Base da margem diverge:** CardTrader e COMC calculam sobre a revenda; os
  demais sobre a compra. **Não compare margens de feeds crus diferentes** — use
  o feed unificado (abaixo), que já recalcula tudo na base compra.
- Bônus: **não deduza** nome de campo, alias/código de set nem substring de
  edição. Nesta frota, aliases deduzidos por LLM já saíram alucinados e foram
  descartados. Falta algo? peça pelo canal.

## Feed principal (use este): `deals_store.json`

Gerado a cada run do **integrated-scanner** (orquestrador dos 4 scanners de
singles: MYP, CardTrader, COMC, Liga) em `outputs/deals_store.json` — 4 fontes,
mesmas colunas, margem já unificada na base compra. Estrutura resumida
(`schema_version: 1`; schema formal e exemplo acompanham este pacote):

```jsonc
{
  "schema_version": 1,
  "generated_utc": "2026-08-20T13:05:00Z",
  "scope": ["PRE", "SSP"],          // sets do run, ou "full"
  "fx": 5.2,                         // câmbio USD→BRL do run
  "min_margin_pct": 30.0,            // corte, em PERCENT
  "deal_count": 3,
  "sources": [                       // status honesto por fonte — SEMPRE exibir
    {"source": "MYP", "status": "ok", "deals_raw": 412, "deals_kept": 1, ...},
    {"source": "COMC", "status": "indisponível", "detail": "...", ...}
  ],
  "deals": [{
    "fonte": "MYP",                  // MYP | CardTrader | COMC | Liga
    "carta": "...", "set_name": "...", "numero": "161/131",
    "raridade": "...",               // pouco confiável no MYP (SIR pode vir "Comum")
    "notorio": "⭐ ...",             // Pokémon notório; informação, não ranking
    "compra_brl": 100.0, "compra_usd": 19.23, "fx": 5.2,
    "ref_brl": 208.0, "ref_usd": 40.0,
    "margem_pct": 108.0,             // PERCENT, base compra, bruta
    "lucro_brl": 108.0,
    "qtd": null,                     // null = fonte não informa estoque → renderize "—"
    "notas": ["validar manualmente ..."],  // flags — exibir sempre
    "link_oferta": "https://...", "link_tcg": "https://..."
  }]
}
```

Há também uma **API HTTP local** (FastAPI, mesmo dado): `GET /deals` (filtros
`source`, `set`, `min_margin`, `notorious`, `q`, `limit`), `GET /sets`,
`GET /sources`, `GET /status`, `POST /scan` (dispara run; **cuidado**: fontes
COMC/Liga abrem Chrome na máquina do operador e exigem opt-in explícito no
corpo). Swagger em `/docs`.

## Feeds complementares (separados de propósito — vocabulários diferentes)

- **Selados** (`sealed-scanner`): `unified_deals.csv` + `run_meta.json` por run;
  buckets GREEN/YELLOW/RED (YELLOW = match ambíguo ou referência velha, NUNCA
  faixa de margem); painel local read-only com `/api/deals`, `/api/products`,
  `/api/status`, `/api/routes` (`?game=pokemon|onepiece`). Colunas/link eBay
  são informativos, nunca classificam. Sem piso de preço.
- **eBay** (`ebay-arbitrage-scanner`): `results/last_scan.json`; vereditos
  OPORTUNIDADE/REVISAR/SUSPEITO/REJEITADO, `score` 0-100, `trust_score`
  separado da margem, `ref_kind` = tcgplayer|pricecharting. Run degradado não
  grava artefato (preserva o anterior) — cheque a idade.
- **COMC** (`scanner-comc`): `results/comc_deals_<era>_latest.json`; flag
  `validar` (confiança < 0.90) e sufixo `preço:<campo>` quando a referência
  não é `market`.
- **Longo prazo** (`pokemon-longterm-outlook`): score 0-100 de potencial de
  valorização — **não é arbitragem**; nunca misturar com margem no mesmo
  ranking.

## Validação

A frota mantém `validate_feed.py` (Python stdlib, offline) que checa formato E
invariantes do feed unificado. Se o que o dashboard consome passa nele, está no
contrato.

## Como pedir mudanças

Escreva o pedido no formato do template do canal (o operador transporta):
**o que falta → para qual tela → o que o dashboard faria com o dado → se toca
algum invariante**. A frota responde com o campo real do código, ou o motivo de
não existir. Mudança aceita entra no contrato + schema por PR — até lá, não
implemente por suposição.

## O que nunca circular neste canal

Valores de chave/segredo (API keys, tokens, JWT) e **dados de scan reais**
(margens/preços/cartas de uma run) — os repos são públicos/privados sob regra
de discrição; exemplos são sempre fictícios.
