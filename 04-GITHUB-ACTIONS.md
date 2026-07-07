# 04 — GitHub Actions (robôs) por scanner

GitHub Actions = robôs que rodam na nuvem. Dois tipos aqui: **`tests`/`CI`** (rodam os testes a cada mudança, pra avisar se quebrou) e **scans** (rodam o scanner de fato).

> ✅ **Todos os 6 repos são PÚBLICOS desde 2026-06-19** → Actions **grátis** (repo público não consome cota). O bloqueio antigo por billing (que aparecia como "falha" fantasma) não deve mais ocorrer. Ver erro nº3 em [`01-ERROS-COMUNS.md`](01-ERROS-COMUNS.md).
>
> Os scans rodam por **disparo manual** (`workflow_dispatch`) — os crons automáticos foram removidos pra controlar custo/ruído. Disparar pela aba **Actions** do GitHub, ou: `gh workflow run <arquivo>.yml --repo matheuscllm-lgtm/<repo>`.

---

## MYP — `myp-arbitrage-scanner`
| Workflow | Tipo | Quando |
|---|---|---|
| `tests` | testes | push/PR no main |
| Daily MYP Quick Scan | scan | manual |
| Quick MYP Scan (chunked) | scan | manual |
| Weekly MYP Scan | scan | manual |
| Probe TCG price sources | sonda | manual (confere se a nuvem alcança tcgcsv/pokemontcg) |
- Python na nuvem: 3.14 (scans) / 3.12 (testes). Usa `--tcg-source tcgcsv` (a rota que funciona na nuvem).

## CardTrader — `card-trader-scanner`
| Workflow | Tipo | Quando |
|---|---|---|
| `tests` | testes | push/PR |
| Daily CT Scan | scan | manual |
| Weekly Scan (full scope) | scan | manual |
- **Corrigido em 22/06 (PR #32):** os scans estavam fixados em Python 3.14 (quebrava numpy/pandas) e a chave tinha BOM → agora Python **3.12** + chave limpa. Os scans agora rodam de verdade (108s pra ~37k listings).

## Liga — `liga-cards-scanner` (pasta local no PC: `liga-pokemon-scanner`)
| Workflow | Tipo | Quando |
|---|---|---|
| `CI` | testes + smoke mock | push/PR |
| `tests` | testes | push/PR |
- Sem secrets (roda mock/offline). A coleta ao vivo (navegador headful) é **só local** — não dá pra rodar na nuvem. `CI` e `tests` são quase redundantes (ambos `pytest`); consolidar é opcional.

## COMC — `scanner-comc`
| Workflow | Tipo | Quando |
|---|---|---|
| `tests` | testes | push/PR |
| COMC Scan | scan | manual — **dormente** |
| Dependency Graph | infra | automático |
- O scan na nuvem precisa do secret `FIRECRAWL_API_KEY` (não setado) — está dormente **de propósito**: o COMC roda local (headful, grátis). Só ligar se quiser scan na nuvem.

## eBay — `ebay-arbitrage-scanner`
| Workflow | Tipo | Quando |
|---|---|---|
| `tests` | testes | push/PR |
- Só testes (offline). Não há scan na nuvem — o eBay roda local (usa as chaves do PC). Os testes não precisam das chaves (são mock/fixture).

## Selados — `sealed-scanner` (pasta local no PC: `sealed-arbitrage-scanner`)
| Workflow | Tipo | Quando |
|---|---|---|
| `tests` | testes | push/PR |
- Scan roda local (Liga/OLX/Amazon precisam headful). `main` é gateada (protegida).

---

## Como conferir o estado (qualquer repo)
```bash
gh workflow list --repo matheuscllm-lgtm/<repo>          # workflows ativos
gh run list --repo matheuscllm-lgtm/<repo> --limit 6     # últimas execuções + resultado
gh run view <run-id> --repo matheuscllm-lgtm/<repo> --log-failed   # ver por que falhou
```
Se um run aparecer "failure", confira **primeiro** se a mensagem é de billing (conta) e não de código — ver erro nº3.
