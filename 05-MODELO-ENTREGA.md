# Entrega dos scanners — regra vigente do operador

Esta regra substitui instruções anteriores de entrega, publicação de resultados
e reutilização de preços. Vale para todos os jogos e perfis deste scanner.

- Rodar uma coleta nova quando o operador solicitar um scan. Não criar execução
  recorrente. Uma análise de código ou formatação não autoriza uma coleta de mercado.
- Entregar a tabela Markdown do gerador canônico diretamente no painel de conversa,
  no padrão MYP Cards: carta com número (ou produto/SKU), compra, referência assumida,
  diferença, métricas econômicas e flags pertinentes, com links da oferta e referência.
- O próprio preço de referência deve ser clicável e apontar à fonte que sustenta
  aquele valor. Mediana e projeção devem ser identificadas, com suas evidências.
  Não substituir fonte ausente por uma busca genérica ou por outra carta.
- Preservar todas as linhas disponíveis e os avisos de revisão/rejeição. Não
  remontar tabelas à mão nem transformar uma ausência de referência em preço zero.
- Não publicar resultados, preços, relatórios ou logs de coleta no GitHub, inclusive
  commits, Pages, releases, issues, comentários, Actions artifacts ou job summaries.
  GitHub pode guardar código e documentação; a entrega dos resultados é só no chat.
- Arquivos locais temporários são apoio de processamento, não a entrega padrão.
  Só anexar arquivos se solicitado. Não usar resultados antigos como preços atuais.
- Em cada nova solicitação, renovar ofertas, referências de preço e câmbio.
  Cache apenas da coleta em andamento ou de metadados estáveis; nunca reutilizar
  preços de outro scan, mesmo no mesmo dia. Um dump atualizado do provedor deve
  ter sua data informada; não prometer cotação em tempo real se a fonte é diária.
- Falha da coleta atual: declarar indisponibilidade/resultado parcial. Nunca
  apresentar um snapshot anterior como se tivesse sido coletado agora.
- Não mudar regras de margem, taxas, moedas ou equivalências para padronizar a tabela.

## Procedimento antes de entregar

1. Fazer a nova coleta solicitada, com saída e caches voláteis próprios desta execução.
2. Gerar a tabela com a ferramenta do repositório, a partir somente dessa execução.
3. Conferir identificação, horário da coleta, preço clicável, fonte e flags.
4. Colar a tabela no chat; se longa, dividir em mensagens preservando todas as linhas.

Para CardTrader usar coleta sem cache de preços; para Liga desativar cache de preços
entre execuções; para MYP não retomar checkpoints de solicitações anteriores.
COMC/eBay devem usar diretório de cache novo por coleta. Selados devem reconstruir
as referências de classificação e coletar novamente as ofertas antes do relatório.
O integrado deve chamar as fontes nesta execução, sem carregar arquivos antigos.


# 05 — Modelo padrão de entrega (estilo MYP)

Regra do operador (canônica, 2026-06): **o resultado de um scan é entregue como TABELA MARKDOWN no chat** (terminal ou app), **nunca** como arquivo XLSX por padrão. O XLSX continua sendo gerado como apoio local, mas a entrega é a tabela. Arquivo só quando você pedir explicitamente.

A tabela é **sempre gerada pela ferramenta do repo** (que monta as colunas, os links clicáveis e a classificação) — **nunca** montada à mão a partir do CSV/JSON (isso introduz erro e perde colunas).

| Scanner | Ferramenta que gera a entrega |
|---|---|
| MYP | `myp_summary.py` |
| CardTrader | `cardtrader_postprocess.py` (`build_delivery_markdown`) |
| Liga | `src/reporting/markdown.py` (`build_markdown`) — impresso por `main.py` |
| COMC | `reporter.py` (`render_markdown`) |
| eBay | `src/report.py` (`to_markdown`) |

---

## As duas colunas que NÃO podem faltar

### 1. Coluna `Carta` = nome **+ número**
Pra você copiar/colar e achar a carta exata. Ex.: `Iono's Bellibolt ex (188/159)`, `Umbreon ex #161`.

### 2. Coluna `Links` = oferta **+** referência, num campo só
Combinada, com separador ` · `, **os dois lados sempre** (o link da loja onde compra e o link da referência de preço):

```
[oferta](url_da_loja) · [TCG](url_da_referência)
```
- `[oferta]` = o anúncio na loja (MYP / CardTrader / Liga / COMC / eBay).
- `[TCG]` / `[referência]` = a página de preço de referência (pokemontcg.io, tcgcsv, PriceCharting…).
- Lado faltando → renderiza `—`.
- **URL sempre percent-encodada pela ferramenta** (espaço, aspas e **parênteses** → `%20`/`%27`/`%28`/`%29`, sem re-encodar `%XX` existente — `quote(url, safe="%/?&=:+,*")`). Em `[label](url)` um `)` cru fecha o link no primeiro parêntese, e o wrap `<url>` **não** é respeitado por todo renderizador (oferta da Liga truncada no remote-control, operador 2026-08-04). URLs da Liga carregam `(ING)`/`(Kit Pré-Lançamento)` no `prod=` — sem encode o link abre a página errada.

> Isto **substitui** o formato antigo de colunas de link separadas. Todos os 6 já convergiram pra coluna `Links` combinada (o eBay foi o último, alinhado em 22/06 no PR #2).

---

## Colunas canônicas completas (modelo de referência — CardTrader/MYP)

```
# | Margem % | <preço loja> | <preço ref> | Dif | Carta | Set | Raridade | Cond | Qtd | Flag | Links
```
- **#** = ranking por margem (maior primeiro).
- **Margem %** = margem BRUTA (sem taxa).
- **preço loja / preço ref** = os dois preços comparados (na moeda do scanner).
- **Dif** = diferença absoluta.
- **Carta** = nome + número (ver acima).
- **Cond** = condição (sempre Near Mint).
- **Qtd** = quantidade disponível naquela oferta.
- **Flag** = bandeira por linha (`ok`, `validar`, `abaixo do limiar`, `REF DESALINHADA`, etc.).
- **Links** = combinada (ver acima).

Mostra **TODAS** as linhas (aprovadas + rejeitadas/near-miss), ordenadas por margem — não é amostra curada.

---

## Exemplo real (CardTrader, set Journey Together, 2026-06-22)

Cenário em que **nenhuma** carta bateu o limiar de 30% — antes isto entregava vazio; agora mostra os "quase-lá" com aviso honesto:

> ⚠️ _Nenhum deal acima do limiar — mostrando os candidatos mais próximos por margem (todos ABAIXO do limiar, só referência)._

| # | Margem % | CT US$ | TCG US$ | Dif | Carta | Set | Raridade | Cond | Qtd | Flag | Links |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 18% | 16.24 | 19.85 | 3.61 | Iono's Bellibolt ex (188/159) | Journey Together (jtg) | Secret Rare | Near Mint | 1 | abaixo do limiar | [oferta](https://www.cardtrader.com/cards/326102) · [TCG](https://prices.pokemontcg.io/tcgplayer/sv9-188) |
| 2 | 13% | 17.24 | 19.89 | 2.65 | Wailord (162/159) | Journey Together (jtg) | Illustration Rare | Near Mint | 3 | abaixo do limiar | [oferta](https://www.cardtrader.com/cards/326077) · [TCG](https://prices.pokemontcg.io/tcgplayer/sv9-162) |

---

## Pequenas variações aceitáveis entre scanners
- A palavra dentro do link de referência pode mudar conforme a fonte: `[TCG]` (MYP/CT), `[referência]` ou `[referência de preço]` (Liga/COMC), `[referência]` (eBay → PriceCharting). A **estrutura** (coluna única `Links`, dois lados, separador ` · `) é o que importa.
- Os nomes das colunas de preço refletem a moeda/fonte (`Liga R$` / `Ref TCG R$` / `CT US$` / `TCG US$`).
- Selados têm coluna extra **`Qtd disponível`** (você importa em lote) e são agrupados por produto.

## O que NÃO fazer
- ❌ Entregar XLSX/CSV por padrão (só sob pedido explícito).
- ❌ Montar/transcrever a tabela à mão.
- ❌ Colunas de link separadas (use a `Links` combinada).
- ❌ Curar/esconder linhas — mostre todas, use a coluna `Flag` pra sinalizar.
- ❌ Rankear "comprar/não comprar" — reporte margem/flags/fontes; você decide o capital.
