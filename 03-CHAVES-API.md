# 03 — Chaves de API necessárias

Duas camadas: **(A)** chaves no seu PC (variáveis de ambiente do Windows) — usadas quando você roda local; **(B)** secrets no GitHub — usados pelos robôs (Actions) na nuvem.

> A `POKEMONTCG_API_KEY` é a mesma em todo lugar. **O valor não é versionado** — fica nas variáveis de ambiente do Windows e nos secrets do GitHub. Confira com os comandos abaixo.

---

## (A) No seu PC — variáveis de ambiente do Windows (User)

Conferidas presentes em 2026-06-22:

| Variável | Pra que serve | Usada por |
|---|---|---|
| `POKEMONTCG_API_KEY` | preço de referência pokemontcg.io | MYP, CardTrader, Liga (lê quando presente, PR #30), local |
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

## (B) No GitHub — secrets por repositório (estado em 2026-06-24)

Gravados em **Actions E Codespaces** (`--app actions` e `--app codespaces`), todos BOM-safe via `printf '%s'`.

| Repo | Secrets configurados | Observação |
|---|---|---|
| `myp-arbitrage-scanner` | `POKEMONTCG_API_KEY`, `FIRECRAWL_API_KEY` | Pokémon resetado limpo (sem BOM) em 22/06 |
| `Card-trader-scanner` | `CT_JWT`, `POKEMONTCG_API_KEY` | Pokémon resetado limpo (sem BOM) em 22/06 |
| `Liga-cards-scanner` | `POKEMONTCG_API_KEY` | CI roda mock/offline, mas a key sobe o limite quando a coleta usa pokemontcg.io |
| `scanner-comc` | *(nenhum)* | scan na nuvem está dormente; se ligar, precisa `FIRECRAWL_API_KEY` |
| `ebay-arbitrage-scanner` | `EBAY_CLIENT_ID`, `EBAY_CLIENT_SECRET`, `EBAY_DEV_ID`, `EBAY_ENV`, `EBAY_MARKETPLACE_ID`, `EBAY_SCOPE` | gravadas 24/06; CI é offline (não precisa), mas ficam disponíveis p/ Codespaces e runs na nuvem |
| `sealed-arbitrage-scanner` | *(nenhum)* | roda local headful; `FIRECRAWL_API_KEY` vem do PC |

Outros repos da frota com `POKEMONTCG_API_KEY` (não são os 6 scanners de cima, mas usam a key): `pokemon-longterm-outlook`, `integrated-scanner`. Os repos da ASI (`asi-evolve`, `asi-main`, `github.com-GAIR-NLP-ASI-Evolve`) têm `ASI_EVOLVE_API_KEY` + `OPENAI_API_KEY` (⏳ falta `OPENAI_BASE_URL`, endpoint real da ASI-Evolve, pra a chave OpenAI roteada funcionar).

⚠️ Esses repos são **públicos** — secret de produção em repo público não vaza em log/PR de fork por padrão, mas considere repos privados pros que guardam chave sensível (eBay PRD, ASI).

Listar/setar secret (sem BOM — ver erro nº1 em [`01-ERROS-COMUNS.md`](01-ERROS-COMUNS.md)):
```bash
gh secret list --repo matheuscllm-lgtm/<repo>                       # Actions
gh secret list --repo matheuscllm-lgtm/<repo> --app codespaces      # Codespaces
printf '%s' 'A_CHAVE' | gh secret set NOME --repo matheuscllm-lgtm/<repo>                 # Actions
printf '%s' 'A_CHAVE' | gh secret set NOME --repo matheuscllm-lgtm/<repo> --app codespaces
```

---

## Regras sobre chaves
1. **Nunca** colar chave dentro do código (hardcode). Sempre ler de variável de ambiente / secret. (Conferido: nenhum dos scanners tem chave hardcoded.)
2. **Nunca** editar `.env` com o Claude Code observando o terminal (o file-watcher ecoa a credencial). Use confirmação por palavra + smoke sanitizado.
3. Ao setar secret, **cuidado com BOM** (ver erro nº1). Use `printf '%s'`.
4. Chave que existe mas o código não usa é problema (perde-se o limite maior de requisições). Era o caso da Liga, **já resolvido** (PR #30: passou a mandar `X-Api-Key` quando a key está presente). Ao adicionar uma fonte, confira que a chave dela é de fato lida no código.
