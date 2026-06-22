# 📚 Manual da Frota de Scanners (pasta comum)

> **O que é isto:** o ponto único de consulta para os **6 scanners de arbitragem** (5 de singles + selados). Reúne, num lugar só, o que se repete entre eles: os **erros mais comuns**, qual **fonte de preço** cada um usa, quais **chaves de API** são necessárias, quais **fallbacks** (planos B) entram em ação, o **estado dos GitHub Actions** e o **modelo padrão de entrega** (tabela estilo MYP).
>
> Mantido por: auditoria cross-scanner de **2026-06-22**. Atualize quando algo mudar.

Termos rápidos (o operador é médico, não programador):
- **scanner** = o programa que compara o preço de compra (loja) com o de referência (mercado) e lista as cartas com margem boa.
- **API** = uma "porta" oficial de um site que devolve dados (preços) pra um programa.
- **chave de API (key)** = a senha que identifica você nessa porta.
- **fallback** = plano B: se a fonte principal falha, usa a secundária.
- **GitHub Actions / workflow** = robô que roda o scanner sozinho na nuvem (sem ligar seu PC).
- **secret** = a chave de API guardada de forma segura dentro do GitHub, pro robô usar.
- **CI / tests** = robô que roda os testes a cada mudança pra avisar se algo quebrou.

---

## Índice dos documentos

| Arquivo | Conteúdo |
|---|---|
| [`01-ERROS-COMUNS.md`](01-ERROS-COMUNS.md) | Os erros que mais se repetem + como evitar cada um |
| [`02-REFERENCIAS-E-FALLBACKS.md`](02-REFERENCIAS-E-FALLBACKS.md) | Qual preço de referência cada scanner usa e quais fallbacks |
| [`03-CHAVES-API.md`](03-CHAVES-API.md) | Todas as chaves de API necessárias, onde ficam, como conferir |
| [`04-GITHUB-ACTIONS.md`](04-GITHUB-ACTIONS.md) | Workflows ativos por scanner (todos públicos = Actions grátis) |
| [`05-MODELO-ENTREGA.md`](05-MODELO-ENTREGA.md) | O formato padrão da tabela de entrega (estilo MYP) |

---

## Visão geral dos scanners (tabela-mãe)

| Scanner | Pasta local | Repo GitHub | Compra (loja) | Referência de preço | Chaves necessárias |
|---|---|---|---|---|---|
| **MYP** | `myp-arbitrage-scanner` | `matheuscllm-lgtm/myp-arbitrage-scanner` | MYP Cards (BR, R$) | **tcgcsv.com** (real) → pokemontcg.io → `.estat-tcg` (fallback) | `POKEMONTCG_API_KEY`, `FIRECRAWL_API_KEY` |
| **CardTrader** | `card-trader-scanner` | `matheuscllm-lgtm/Card-trader-scanner` | CardTrader (Europa, €/US$) | **pokemontcg.io** (+ validação per-blueprint) | `CT_JWT`, `POKEMONTCG_API_KEY` |
| **Liga** | `liga-pokemon-scanner` | `matheuscllm-lgtm/Liga-cards-scanner` | Liga Pokémon (BR, R$) | **pokemontcg.io** (anônimo) → sets novos via MYP API → PriceCharting | nenhuma p/ CI (coleta ao vivo é headful) |
| **COMC** | `scanner-comc` | `matheuscllm-lgtm/scanner-comc` | COMC (US, US$) | **tcgcsv.com** (market→mid→low) | `FIRECRAWL_API_KEY` (só nuvem, hoje dormente) |
| **eBay** | `ebay-arbitrage-scanner` | `matheuscllm-lgtm/ebay-arbitrage-scanner` | eBay (US, US$) | **PriceCharting** (raw + graded) | `EBAY_CLIENT_ID`, `EBAY_CLIENT_SECRET` |
| **Selados** | `sealed-arbitrage-scanner` | `matheuscllm-lgtm/sealed-arbitrage-scanner` | Liga / OLX / Amazon BR / ML | **TCGplayer US** (selado) | `FIRECRAWL_API_KEY` |

> A chave **`POKEMONTCG_API_KEY`** é a mesma pra todos (valor gerenciado nas variáveis de ambiente do Windows e nos secrets do GitHub — **o valor não é versionado**; ver [`03-CHAVES-API.md`](03-CHAVES-API.md) pra conferir/setar).

---

## Regras de ouro que valem pra TODOS os scanners

1. **Margem é BRUTA, 30% mínimo.** Só `(revenda − compra) / compra`. Nenhuma taxa embutida (frete, cartão, IOF — você calcula por fora). Piso de relevância: **R$50** (~US$10).
2. **Só Near Mint (NM).** Condição lida de célula dedicada, match EXATO `== "NM"` — nunca "contém NM" (isso já vazou SP no passado).
3. **Nunca inventar preço.** Se a fonte falha, marca como fallback/erro e segue — jamais fabrica um número.
4. **Entrega = tabela markdown no chat.** Nunca arquivo XLSX por padrão (só se você pedir). Gerada pela ferramenta do repo, nunca montada à mão. Ver [`05-MODELO-ENTREGA.md`](05-MODELO-ENTREGA.md).
5. **Claude é o técnico, você decide o capital.** O scanner reporta margem, flags e fontes; não rankeia "compre isto".
6. **Mostrar TODOS os deals** (aprovados + rejeitados/near-miss), não uma amostra curada.

⚠️ **Cuidado com a convenção de threshold (pega muita gente):**
- **MYP** usa **percentual inteiro**: `--threshold 30` = 30%.
- **CardTrader / COMC / eBay** usam **fração**: `--threshold 0.30` = 30%. No CT, `0.30` e `30` dão resultados absurdamente diferentes (`30` = 3000%, zero deals).
