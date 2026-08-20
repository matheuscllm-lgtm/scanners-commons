# 📊 STATUS — integração GPT ↔ frota (dashboard integrativo)

Estado vivo do canal. Atualizar **no fim de cada rodada de mensagens** (padrão
da frota: toda decisão com data).

_Última atualização: 2026-08-20, rodada 2 (resposta ao checklist de campos do GPT)._

## O que já existe e o GPT pode consumir HOJE

| Peça | Estado | Onde |
|---|---|---|
| Contrato de dados (humano) | ✅ v1 | `CONTRATO-DE-DADOS.md` |
| Schema do feed unificado | ✅ v1 (`schema_version: 1`) | `schemas/dashboard-feed.schema.json` |
| Exemplo fictício do feed | ✅ | `exemplos/dashboard-feed.example.json` |
| Validador offline + testes | ✅ 19 testes verdes | `validate_feed.py`, `test_validate_feed.py` |
| Feed real unificado (4 fontes singles) | ✅ produzido por run do `integrated-scanner` | `integrated-scanner/outputs/deals_store.json` + API `api.py` |
| Feed de selados | ✅ por run | `sealed-scanner/results/[<jogo>/]unified_*/` + painel `panel.py` |
| Feed eBay | ✅ por run | `ebay-arbitrage-scanner/results/last_scan.json` |
| Feed COMC | ✅ por run | `scanner-comc/results/comc_deals_<era>_latest.json` |
| Pacote de contexto p/ colar no GPT | ✅ | `PACOTE-CONTEXTO-GPT.md` |

## Decisões registradas

- **2026-08-20 (rodada 2)** — GPT enviou (via operador) checklist de campos
  obrigatórios e citou uma API `POST /api/ingest` no dashboard. Frota respondeu
  campo a campo (`mensagens/2026-08-20-frota-para-gpt-campos-padronizados.md`):
  7 já existem (`run_id`=`stamp`, `scanner`=`fonte`, preços, fx, status,
  horário, URLs), 4 viram metadados v1.1 **opcionais** no schema
  (retrocompatível), e **score de confiança unificado foi recusado** (fontes têm
  metodologias diferentes; número sintético violaria o invariante 4) — a
  confiança chega em `notas[]`.

- **2026-08-20** — canal criado em `scanners-commons/integrations/gpt-dashboard/`
  (pedido do operador). Rota default de leitura pelo GPT = colar o
  `PACOTE-CONTEXTO-GPT.md` (o repo é privado). Feed canônico recomendado =
  `deals_store.json` do integrated-scanner. Dados de exemplo sempre fictícios;
  dado de scan real e segredo nunca entram no canal.

## Aberto / aguardando

- **GPT → frota:** spec do `POST /api/ingest` do dashboard (pedida na resposta
  de 2026-08-20) + confirmação de que o v1 é consumível enquanto a v1.1 não sai.
- **Frota (backlog condicionado):** PR no `integrated-scanner` gravando os
  metadados v1.1 no store (`game`, `product_type`, `margin_basis`, `condition`,
  `language`, `fx_source`) — abre depois que o GPT confirmar que precisa deles
  na primeira tela (senão fica no backlog).

## Ideias registradas (não compromissadas)

- Unificar selados/eBay/COMC num envelope multi-feed (`schema_version: 2`?) —
  só se o dashboard demonstrar a necessidade; hoje são feeds separados de
  propósito (bases e vocabulários diferentes).
- Expor o `deals_store.json` por um endpoint estável para consumo remoto — hoje
  a API é local (`127.0.0.1`); qualquer exposição além disso é decisão do
  operador (custo/risco).
