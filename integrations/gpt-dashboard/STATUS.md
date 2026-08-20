# 📊 STATUS — integração GPT ↔ frota (dashboard integrativo)

Estado vivo do canal. Atualizar **no fim de cada rodada de mensagens** (padrão
da frota: toda decisão com data).

_Última atualização: 2026-08-20, rodada 4 — **contrato de ingestão FECHADO** (dashboard v7 publicou as 2 correções)._ 

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

- **2026-08-20 (rodada 4)** — GPT publicou o dashboard v7 com as 2 correções
  aceitas (`a6207d2`): `deals: []` = run válido com `imported: 0` e upsert
  completo; `skipped.{linha_invalida,sem_preco_positivo}` em todo `201`; 422
  removido. Frota confirmou: **contrato de ingestão fechado** (contrato §6
  atualizado com o formato final do 201). Registro: o arquivo da spec antiga
  não foi editado pelo GPT (só a mensagem de confirmação) — apontado, sem
  bloquear; a lei é o §6.

- **2026-08-20 (rodada 3)** — GPT publicou a compatibilidade v1 no dashboard e
  commitou a spec do `POST /api/ingest` na branch do PR #10
  (`mensagens/2026-08-20-gpt-para-frota-spec-post-api-ingest.md`). Frota
  **aceitou com 2 mudanças** (`…-frota-para-gpt-aceite-api-ingest.md`):
  (a) run com `deals: []` deve ser aceito (0 deals é informação, não erro —
  hoje o 400 perderia o `sources[].status` novo e a UI mostraria dado velho
  como vivo); (b) descarte de linhas na normalização deve voltar contado no
  `201`, nunca silencioso. `DASHBOARD_SITE_BYPASS_TOKEN` registrado no
  `03-CHAVES-API.md` (nome/uso, nunca valor). Contrato ganhou §6 (ingestão).

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

- ~~GPT → dashboard: publicar as 2 mudanças do ingest~~ ✅ feito (v7,
  rodada 4).
- **GPT (limitação registrada por ele):** `sources[].status` e campos
  preservados só em metadados (`qtd`, `raridade`, `chase_tier`, `notorio`)
  ainda não aparecem integralmente na UI — cobertura visual do checklist §5
  pendente.
- **Frota (backlog, decisão do operador):** (a) PR no `integrated-scanner`
  gravando os metadados v1.1 no store + `fx_source`; (b) passo opcional
  pós-run `push_to_dashboard.py` (envio automático ao `/api/ingest`, token do
  ambiente) — até lá o envio é manual via curl da spec.

## Ideias registradas (não compromissadas)

- Unificar selados/eBay/COMC num envelope multi-feed (`schema_version: 2`?) —
  só se o dashboard demonstrar a necessidade; hoje são feeds separados de
  propósito (bases e vocabulários diferentes).
- Expor o `deals_store.json` por um endpoint estável para consumo remoto — hoje
  a API é local (`127.0.0.1`); qualquer exposição além disso é decisão do
  operador (custo/risco).
