# 03 — Chaves de API necessárias

Duas camadas: **(A)** chaves no seu PC (variáveis de ambiente do Windows) — usadas quando você roda local; **(B)** secrets no GitHub — usados pelos robôs (Actions) na nuvem.

> A `POKEMONTCG_API_KEY` é a mesma em todo lugar. **O valor não é versionado** — fica nas variáveis de ambiente do Windows e nos secrets do GitHub. Confira com os comandos abaixo.

---

## (A) No seu PC — variáveis de ambiente do Windows (User)

Conferidas presentes em 2026-06-22:

| Variável | Pra que serve | Usada por |
|---|---|---|
| `POKEMONTCG_API_KEY` | preço de referência pokemontcg.io | MYP, CardTrader, (Liga — hoje não lê), local |
| `FIRECRAWL_API_KEY` | scrape robusto (fura WAF, etc.) | MYP (drift), COMC (nuvem), Selados |
| `OPENAI_API_KEY` | ASI-Evolve / experimentos de LLM | ferramentas auxiliares |
| `EBAY_CLIENT_ID` | login na eBay Browse API | eBay |
| `EBAY_CLIENT_SECRET` | senha da eBay Browse API | eBay |

Conferir uma chave (PowerShell):
```powershell
[System.Environment]::GetEnvironmentVariable('POKEMONTCG_API_KEY','User')
```

O CardTrader também lê **`CT_JWT`** (token da API do CardTrader) — fica no arquivo `.env` do repo do CT, não nas variáveis globais.

---

## (B) No GitHub — secrets por repositório (estado em 2026-06-22)

| Repo | Secrets configurados | Observação |
|---|---|---|
| `myp-arbitrage-scanner` | `POKEMONTCG_API_KEY`, `FIRECRAWL_API_KEY` | ambos OK; Pokémon resetado limpo (sem BOM) em 22/06 |
| `Card-trader-scanner` | `CT_JWT`, `POKEMONTCG_API_KEY` | Pokémon resetado limpo (sem BOM) em 22/06 |
| `Liga-cards-scanner` | *(nenhum)* | CI roda em modo mock/offline; coleta ao vivo é só local |
| `scanner-comc` | *(nenhum)* | scan na nuvem está dormente; se ligar, precisa `FIRECRAWL_API_KEY` |
| `ebay-arbitrage-scanner` | *(nenhum)* | CI é offline; chaves eBay ficam só no PC |
| `sealed-arbitrage-scanner` | *(nenhum)* | roda local headful; `FIRECRAWL_API_KEY` vem do PC |

Listar/setar secret (sem BOM — ver erro nº1 em [`01-ERROS-COMUNS.md`](01-ERROS-COMUNS.md)):
```bash
gh secret list --repo matheuscllm-lgtm/<repo>
printf '%s' 'A_CHAVE' | gh secret set NOME --repo matheuscllm-lgtm/<repo>
```

---

## Regras sobre chaves
1. **Nunca** colar chave dentro do código (hardcode). Sempre ler de variável de ambiente / secret. (Conferido: nenhum dos scanners tem chave hardcoded.)
2. **Nunca** editar `.env` com o Claude Code observando o terminal (o file-watcher ecoa a credencial). Use confirmação por palavra + smoke sanitizado.
3. Ao setar secret, **cuidado com BOM** (ver erro nº1). Use `printf '%s'`.
4. Chave que existe mas o código não usa também é problema (ex.: Liga tem a Pokémon key no PC mas chama a API anônima — perde o limite maior de requisições). Ligar é melhoria de backlog.
