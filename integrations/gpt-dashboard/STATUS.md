# 📊 STATUS — integração GPT ↔ frota (dashboard integrativo)

Estado vivo do canal. Atualizar **no fim de cada rodada de mensagens** (padrão
da frota: toda decisão com data).

_Última atualização: 2026-08-20 (abertura do canal)._

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

- **2026-08-20** — canal criado em `scanners-commons/integrations/gpt-dashboard/`
  (pedido do operador). Rota default de leitura pelo GPT = colar o
  `PACOTE-CONTEXTO-GPT.md` (o repo é privado). Feed canônico recomendado =
  `deals_store.json` do integrated-scanner. Dados de exemplo sempre fictícios;
  dado de scan real e segredo nunca entram no canal.

## Aberto / aguardando

- Nenhuma mensagem pendente do GPT ainda. Primeira rodada esperada: o GPT lê o
  pacote e responde com o que falta para o dashboard.

## Ideias registradas (não compromissadas)

- Unificar selados/eBay/COMC num envelope multi-feed (`schema_version: 2`?) —
  só se o dashboard demonstrar a necessidade; hoje são feeds separados de
  propósito (bases e vocabulários diferentes).
- Expor o `deals_store.json` por um endpoint estável para consumo remoto — hoje
  a API é local (`127.0.0.1`); qualquer exposição além disso é decisão do
  operador (custo/risco).
