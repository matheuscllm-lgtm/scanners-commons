# HANDOFF — Análise de investimento em Pokémon TCG (produtos em inglês)

**Status: ABERTO (2026-09-12) — pesquisa parcialmente concluída; relatório NÃO escrito.**
A sessão de origem (Claude Code na nuvem, 2026-09-06 → 09-08) foi interrompida pelo operador ("parar") depois que o limite de sessão da API derrubou 4 das 6 frentes de pesquisa web. Este handoff existe para que **outra conversa** retome do ponto exato, sem refazer o que já está pronto.

> **Não é scanner, não é deal.** É um relatório analítico (tese de investimento), pedido pelo operador com um prompt longo e muito específico (Apêndice A). Nada aqui altera scanners, margens ou regras da frota.

---

## 0. Como retomar (cole isto na conversa nova)

```
Leia /home/user/scanners-commons/HANDOFF-POKEMON-TCG-INVESTMENT-ANALYSIS.md e retome
a partir da seção "4. Próximos passos". O pedido original está no Apêndice A (siga o
formato de saída dele à risca). Dados primários e evidências já coletados estão em
scanners-commons/tooling/pokemon-investment-analysis/ (não recoletar o que já existe;
só atualizar a data de corte). Entrega = relatório em português no chat.
```

Pré-requisitos no container novo: `pip install py7zr markdown` (o `py7zr` lê o arquivo `.ppmd.7z` do tcgcsv). Os scripts usam só stdlib + py7zr.

---

## 1. O pedido, em uma frase

Relatório independente e crítico sobre **se vale a pena investir em Pokémon TCG físico em inglês** (horizonte 3–5 anos, perspectiva 5–10), respondendo separadamente: (A) a base de consumidores cresce? (B) é sustentável? (C) vira valorização ou a oferta absorve? (D) o retorno líquido compensa? — com segmentação (selado recente/antigo; singles raw; graduadas modernas/antigas), teste da durabilidade da demanda e da resposta da oferta, avaliação econômica com exemplo numérico de retorno líquido, três cenários, melhor tese a favor/contra, classificação decisória, 6–8 indicadores de acompanhamento, fontes com links/datas e seção condicional para investidor no Brasil. Formato de saída em 9 seções + pergunta final. **Texto integral do prompt: Apêndice A.**

Data de corte prevista para o relatório: a data em que for escrito (dados desta sessão vão até **2026-09-05** no tcgcsv e **2026-09-06** na pesquisa web).

---

## 2. O que já está PRONTO (não refazer)

### 2.1 Dados primários de preço — TCGplayer via arquivo histórico do tcgcsv.com

**O que é:** o tcgcsv.com publica um dump diário de todos os preços do TCGplayer desde 2024-02-08 (`https://tcgcsv.com/archive/tcgplayer/prices-YYYY-MM-DD.ppmd.7z`, ~2–4 MB cada). O `marketPrice` é o mesmo preço de mercado (baseado em vendas concluídas) que os scanners da frota usam. Conferido: arquivo de 2026-09-05 = endpoint ao vivo, centavo por centavo.

**O que foi feito:** 32 snapshots mensais (dia 8 de cada mês, fev/2024 → set/2026, último = 2026-09-05), categoria Pokémon (3), ~25 mil → ~31 mil produtos com preço. Metadados de produto (nome, número, raridade) e a lista de 220 grupos/sets com `publishedOn` vieram dos endpoints ao vivo. Segmentação por **era** (data de publicação do set: WotC ≤ jun/2003; EX; DP/HGSS; BW/XY; SM; SWSH; SV; ME) × **tipo** (selado por palavra-chave do nome: booster box, ETB, bundle, pack, outros; singles por tier de raridade: T1 chase = SIR/Secret/Hyper/Rainbow/Shiny Ultra/Mega Hyper; T2 = IR/Ultra/Shiny; T3 = Holo/Double Rare/ACE etc.; T4 = bulk). Só produtos com preço ≥ US$5 no início de cada janela; variante "Reverse Holofoil" ignorada; mediana e ponderado por valor.

**Arquivos (em `tooling/pokemon-investment-analysis/`):**
- `scripts/fetch_hist.py` — baixa/extrai os arquivos (uso: `python3 fetch_hist.py 2024-02-08 2024-03-08 …`).
- `scripts/fetch_products.py` — metadados de produto (`products3.json`); precisa de `groups3.json` (`curl https://tcgcsv.com/tcgplayer/3/groups`).
- `scripts/analyze.py` — gera `windows.md`, `windows.json`, `monthly_index.md`.
- `data/tcgcsv_windows_compact.md` (tabela-resumo), `data/tcgcsv_windows_full.md` (todas as janelas), `data/tcgcsv_monthly_index.md` (índice mensal, base fev/2024 = 100), `data/tcgcsv_postrelease_sealed.md` (trajetória pós-lançamento de ETB/booster box/bundle de cada set SV e ME), `data/tcgcsv_groups_pokemon.md` (calendário de sets com datas), `data/tcgcsv_dates_used.txt`.

**Resultados-chave (fev/2024 → set/2026, mediana; N = produtos):**

| Segmento | N | Mediana | Pond. valor | fev/24→fev/25 | fev/25→fev/26 | fev/26→set/26 | % subiram |
|---|---|---|---|---|---|---|---|
| Selado SWSH (2020–23) — todos | 311 | +229% | +279% | +22% | +86% | +33% | 98% |
| Selado SV (2023–25) — todos | 100 | +284% | +366% | +40% | +65% | +42% | 98% |
| Selado SM (2017–19) | 162 | +223% | +288% | +17% | +89% | +25% | 96% |
| Selado XY/BW (2011–16) | 75 | +278% | +343% | +17% | +124% | +28% | 96% |
| Selado WotC (1999–2003) | 19 | +97% | +103% | +21% | +32% | +33% | 100% |
| Selado ME (2025–26) | 69 | — | — | — | — | +24% | — |
| Singles WotC (1999–2003) | 877 | +126% | +115% | +10% | +45% | +41% | 97% |
| Singles EX/DP/HGSS | 887 | +192% | +205% | +6% | +75% | +53% | 97% |
| Singles XY/BW | 894 | +213% | +222% | +13% | +77% | +33% | 92% |
| Singles SM | 657 | +133% | +166% | +10% | +50% | +25% | 91% |
| Singles SWSH ≥$5 | 440 | +87% | +205% | +18% | +13% | +34% | 82% |
| Singles T1 chase SWSH | 182 | +34% | +160% | +5% | +3% | +23% | 80% |
| Singles SV ≥$5 | 234 | +60% | +149% | +2% | −15% | +48% | 65% |
| Singles T1 chase SV | 79 | +6% | +93% | 0% | −27% | +19% | 54% |
| Singles T3 mid SV | 7 | −39% | −36% | −51% | −47% | +29% | 43% |
| Singles T4 bulk SV | 127 | — | — | — | −74% | +73% | — |
| Promos (todas as eras) | 931 | +215% | +212% | +8% | +72% | +43% | 93% |

- **Índice mensal (base fev/2024 = 100, cesta fixa) em set/2026:** selado SWSH 329; selado SV 384; selado SM 323; singles WotC 226; singles EX/DP T1/T2 280; T1 chase SWSH 134; T1 chase SV 106. Selados e vintage: **nenhum mês de queda** desde fev/2024 (máx. drawdown mensal 0 a −1%), mas desaceleração clara em jul–set/2026 (selado SV m/m: +8,7%, +8,6%, +1,3%, +0,8%). T1 chase SV: drawdown máx. −26% (2025).
- **Concentração dos ganhos:** em T1 chase SWSH, os 10 maiores ganhadores respondem por **75%** do ganho em dólar (Umbreon VMAX alt $540→$2.298; Rayquaza VMAX alt $250→$1.255; Gengar VMAX alt $208→$1.035); os piores são "Secret Rare" de treinador/energia ($10→$3). Mediana +34% vs ponderado +160% = viés de seleção dos índices famosos.
- **Trajetória pós-lançamento de selados (1º mês pós-lançamento → set/2026):** sets de 2023–início 2024 (medidos a partir de fev/2024) +190% a +935% (ex.: 151 ETB $55→$565; Paldean Fates ETB $44→$445; Obsidian Flames ETB $37→$282). Sets de nov/2024 em diante: Surging Sparks BB $210→$304 (+45%); Prismatic ETB $110→$151 (+37%), Prismatic bundle $105→$89 (**−15%**); Journey Together BB $232→$241 (+4%); Destined Rivals BB $259→$419 (+61%); ME1 Mega Evolution BB $299→$320 (+7%); Phantasmal Flames BB $256→$403 (+57%). **Sets de 2026:** Perfect Order BB $200→$173 (**−14%**); Chaos Rising BB $233→$176 (**−25%**), ETB $83→$70; Pitch Black BB $184→$188 (≈0), ETB $75→$70. Menor anúncio/market em set/2026: ME 0,91–0,95 e SV 0,93–0,98 (oferta abundante abaixo do market) vs SM 1,06–1,10 e EX–XY 1,06–1,23 (livro fino).
- **Oferta/cadência (TCGplayer/tcgcsv):** produtos com preço 24.980 (fev/24) → 27.337 (fev/25) → 30.134 (fev/26) → 31.245 (set/26). Sets com booster por ano: 3–5 (1999–2016), 5–6 (2017–2024), **7 em 2025**, 6 em 2026 até nov (Ascended Heroes jan, Perfect Order mar, Chaos Rising mai, Pitch Black jul, **30th Celebration 16/set/2026**, **Delta Reign 6/nov/2026**). Cartas de raridade T1 por ano de lançamento: 86–111/ano desde 2021; SKUs selados por ano: 160–190 (2021–25); 2026 mostra 722 (inclui cases/placeholders — conferir antes de citar).
- **Níveis de preço em set/2026 (mediana):** booster box SWSH $503 (p90 $729), SV $310, ME $267, SM $1.736, BW/XY $3.728; ETB SWSH $237, SV $200, ME $146, SM $699, BW/XY $1.299; single T1 chase SV $20 (p90 $152), SWSH $8 (p90 $48), SM $22, WotC $719 (p90 $1.801).

### 2.2 Dados primários de graduadas e liquidez — PriceCharting (séries mensais por grau)

**O que é:** as páginas de produto do PriceCharting embutem `VGPC.chart_data` (série mensal desde ago/2021, em centavos, por chave: `used` = raw, `cib` = grau 7, `new` = grau 8, `graded` = PSA 9, `boxonly` = 9,5, `manualonly` = PSA 10) e a linha `<tr class="sales_volume">` com a frequência de vendas por grau. PriceCharting agrega vendas concluídas (eBay/TCGplayer). **Armadilha:** para produtos lançados depois de ago/2021 a série é preenchida para trás com o primeiro valor — ignorar pontos anteriores ao lançamento. **Armadilha 2:** a busca (`search-products`) falha para muitos slugs; use os slugs diretos que estão em `scripts/pull_direct.py`.

**Arquivos:** `scripts/pull_pc.py` (cesta + parser), `scripts/pull_direct.py` (slugs diretos), `scripts/pull_volumes.py` (frequência de vendas), `data/pricecharting_basket.md` (44 itens: valores em set/2021, jan/2022, jul/2022, jan/2023, jan/2024, jan/2025, jul/2025, jan/2026, set/2026, pico, vale pós-pico, atual vs pico, atual vs jan/2024), `data/pricecharting_sales_frequency.md`.

**Destaques (set/2026; variação vs jan/2024):**
- Modernas chase SWSH: Umbreon VMAX alt raw $2.243 (+343%), PSA 10 $4.205 (+395%, 2 vendas/dia); Rayquaza VMAX alt raw $1.148 (+457%), PSA 10 $2.700; Giratina V alt raw $758 (+203%), PSA 10 $3.800.
- Modernas chase SV: Charizard ex 151 SIR raw $365 (+259%), PSA 10 $1.420 (−21% vs pico abr/2026); **Umbreon ex Prismatic SIR raw $1.254 (−27% vs lançamento jan/2025), PSA 10 $5.475 (−35%)**; Iono SIR raw $55 (−57% vs pico 2023); Pikachu ex 238 SIR raw $270 (−42% vs nov/2024); Charizard ex 223 OBF raw $105 (+106%).
- Jogáveis (Double Rare): Charizard ex 125 $18→$5 (−72%); Dragapult ex $13→$2 (−83%); Gardevoir ex $19→$1 (−94%) → utilidade competitiva **não** segura preço.
- Vintage: Charizard Base unlimited raw $345 (+57%), PSA 10 $12.531 (**1 venda/mês**; série volátil, pico $30.100 jun/2026); 1st Ed raw $10.100, PSA 10 $343.098 (4 vendas/ano); Blastoise PSA 10 $7.175 (+282%); Gold Star Charizard PSA 10 $228k (3 vendas/ano); Espeon Gold Star PSA 10 $64.5k. Pikachu Base #58 comum raw $5 vs PSA 10 $513 (100×).
- Selados: Evolving Skies BB $2.372 (+424%; 1 venda/dia); 151 ETB $535 (+951%); 151 UPC $890; Paldean Fates ETB $422 (+408%); Crown Zenith ETB $293 (+639%); Base Set BB unlimited $34.549 (+191%; 1 venda/semana); Prismatic ETB $151; Destined Rivals ETB $124 (−42% vs pico abr/2026); Journey Together BB $247.
- Liquidez (frequência de vendas): selado moderno ~1/dia; Prismatic ETB 3/semana; PSA 10 moderno 1–3/dia; PSA 10 vintage 1/mês a 4/ano; Gold Star PSA 10 3/ano.

### 2.3 Pesquisa web CONCLUÍDA (2 de 6 frentes) — arquivos em `research/`

- `research/research_prices_liquidity.md` — índices (Card Ladder +33,8% jun→set/2026; ~+28% YTD; estudo TCGinvest 2021–26: selado mediana +238%, singles +38%, S&P +81%, max DD selado −32%; Wooster 2021–23 −4,7%/a), históricos de selados e singles com vendas concluídas, recordes de leilão (Illustrator PSA 10 US$16,49M fev/2026; 1st Ed Charizard PSA 10 US$954.800 fev/2026; Gold Star Rayquaza CGC 10 US$1,02M ago/2026), **custos**: eBay 13,25% + US$0,40; TCGplayer 10,75% desde fev/2026; leilões BP ~20% + vendedor 10–15%; buylists 80/90% (selado) e ~60% (singles); eBay: Pokémon 3 dígitos em 2025, desaceleração guiada para 2026; 93 fontes.
- `research/research_grading_populations.md` — GemRate 2023–2026 (2025: 26,8M graduadas, Pokémon 16,1M; jun/2026 recorde 3,5M, PSA 2,5M, TCG 71%), pops PSA datadas (1st Ed Charizard PSA 10 125 de 5.302; Unlimited 489 de 92.856; Umbreon VMAX alt PSA 10 ~20.800; Charizard ex 151 PSA 10 ~28.500; Van Gogh PSA 10 49.261), múltiplos PSA 10/raw (mediana 3,4× moderno; PSA 9 ≈ raw; compressão acima de ~5.000 PSA 10), preços/tiers/backlog PSA (tiers Value pausados 2/jun/2026; backlog ~10,9M em 25/ago/2026), Fraud Report 2025 (Pokémon falsificadas +125%), PSAUpGate, eBay AG US$200; 99 fontes.

### 2.4 Pesquisa web NÃO concluída (4 frentes) — briefs no Apêndice B

1. **TPC/Play! Pokémon oficial** (cartas acumuladas produzidas, Kanpo/lucro da TPC, License Global, Worlds 2024–2026 e Regionais recorde, declarações de produção, TCG Pocket, 30º aniversário).
2. **Oferta/impressão/varejo** (calendário e cadência, MSRP e reajustes, política de reimpressão, estoque/escassez 2025 vs normalização 2026, Millennium Print Group/capacidade/tarifas, Circana, GameStop, estoque acumulado por investidores, falsificações).
3. **Qualidade da demanda/concorrência/riscos** (demografia, Google Trends, live-breaking/Whatnot, TCGs rivais e ICv2, TCG Pocket/Live, fadiga, macro, fraude/regulação, jogadores vs colecionadores/rotação).
4. **Brasil** (Remessa Conforme/ICMS, exportação e de minimis EUA, ganho de capital/DIRPF, câmbio/IOF, Liga/MYP/Copag/Play! Pokémon BR, liquidez doméstica).

Os agentes que rodavam essas frentes morreram por `rate_limit` (HTTP 429, "session limit") antes de gravar qualquer resultado. Sobraram no scratchpad efêmero uns PDFs baixados pelo agente de concorrência (resultados Bandai FY2026) que **não foram lidos nem analisados** — não confie neles sem abrir.

---

## 3. Leituras preliminares (hipóteses de trabalho — NÃO conclusões; valide com as 4 frentes pendentes)

1. **O rali 2024–2026 é de estoque, não de lançamento.** Selados fora de impressão (SWSH, SV 2023–24, SM, XY) e singles de eras antigas subiram 2–4× com 92–100% dos produtos em alta; **chases modernas SV ficaram flat** (mediana +6%) com queda de 27% em 2025, e **selados lançados em 2026 estão iguais ou abaixo do 1º mês** — consistente com "adoção forte + oferta absorvendo a demanda nova" (hipótese central do item 3 do pedido).
2. **Setembro de 2026 = topo ou pausa?** Índices de selado/vintage ainda em máxima, mas com momentum caindo (m/m <1% em ago–set), eBay guiando desaceleração, relatos (secundários, com COI) de liquidação de cases e quedas de 13–22% em singles modernos em 30 dias. Não há correção registrada nos dados primários até 2026-09-05.
3. **Graduação não cria escassez no moderno:** ~1M novos PSA 10 de TCG por mês (todas as línguas), gem rate 50–60%; prêmio PSA 10 comprime acima de ~5 mil cópias; PSA 9 vale o raw. Escassez real só em pré-2003 (gem 13,5%) e SIRs inglesas de gem baixo (27–32%).
4. **Custos de saída são grandes:** ~13–16% (eBay) a ~20%+ (leilão) por transação; buylist cash a 60–90% do market; slabs vintage caros vendem 1×/mês a 4×/ano → desconto para liquidar posições grandes é material. Isso alimenta o exemplo numérico do item 4 do pedido.
5. **Viés de sobrevivência é mensurável:** mediana vs ponderado (+34% vs +160% em chases SWSH) e índices curados (Card Ladder = 9.591 cartas).

---

## 4. Próximos passos (ordem sugerida)

1. **Relançar as 4 frentes pendentes** (Apêndice B) com orçamento menor por agente (≈12 buscas + 8 fetches cada) e instrução de **gravar achados parciais em arquivo a cada lote** (`tooling/pokemon-investment-analysis/research/research_<frente>.md`), para que um novo 429 não perca tudo. Rodar 2 por vez se o limite voltar a estourar. Priorizar: (a) TPC/Play! Pokémon (adoção — é o coração das perguntas A/B), (b) oferta/MSRP/reimpressão (pergunta C), (c) demanda/concorrência, (d) Brasil.
2. **Atualizar a data de corte dos dados primários:** rodar `fetch_hist.py` para o último arquivo disponível (o tcgcsv publica D-1) e `analyze.py`; opcionalmente acrescentar ao `dates.txt` o dia 8 de cada mês novo. Reexecutar `pull_pc.py`/`pull_direct.py`/`pull_volumes.py` se quiser a cesta PriceCharting do dia.
3. **Escrever o relatório** exatamente no formato do Apêndice A (9 seções + pergunta final), em português, com citações inline (links + datas), separando fato / inferência / hipótese, declarando a data de corte e as lacunas (incluindo o que ficar NÃO ENCONTRADO). Usar as tabelas de `data/` como evidência primária de preço; usar `research/` para o resto. Exemplo numérico ilustrativo do item 4 do pedido: montar com os custos já levantados (eBay 13,25% + US$0,40; ou TCGplayer 10,75% + 2,5% + US$0,30; frete/seguro; graduação US$32,99–79,99 conforme tier; armazenamento; buylist 80–90% como piso de liquidez).
4. **Seção Brasil condicional** (só após a frente 4): câmbio, importação, tributação e liquidez local — sem presumir patrimônio ou residência.
5. **Entrega = relatório no chat** (regra da frota: resultado no chat). Um artifact/HTML é opcional e só se o operador quiser; se fizer, carregar o skill `artifact-design` antes.
6. Ao concluir, fechar este handoff (status CONCLUÍDO + data) e, se o operador quiser, versionar o relatório final em `tooling/pokemon-investment-analysis/` — o repo é privado, mas mesmo assim: sem chaves, sem dado pessoal.

---

## 5. Armadilhas e lições desta sessão (não re-descobrir)

- **Limite de sessão da API (429 "session limit"):** 6 agentes em paralelo com ~300k tokens cada derrubaram 4. Orçamento menor + gravação progressiva em arquivo. O resultado de um agente **só chega pela notificação**; o `output_file` dele é o transcript JSONL — não leia.
- **`pkill -f <padrão>` mata o próprio shell** (exit 144) quando o padrão aparece na linha de comando do próprio Bash (ex.: `pkill -f pull_vol` num comando que também cita `pull_vol2.py`). Use `pgrep -f "nome[_]x"` (truque do colchete) num comando isolado, ou PID em arquivo.
- **PriceCharting:** chart_data preenche para trás antes do lançamento; busca de slug não confiável → slugs diretos; `sales_volume` usa `data-show-tab="completed-auctions-<grau>"` com hífen (`box-only`, `manual-only`) — regex precisa de `[a-z-]+`. Séries PSA 10 vintage têm 1 venda/mês ou menos: pontos isolados podem ser outliers (ex.: Shadowless PSA 10 "US$200.645" em abr/2025).
- **gemrate.com responde 403** à nuvem; use imprensa (SI/cllct) e PSA. **Heritage/Goldin/Fanatics** bloqueiam páginas de taxas; use secundárias e marque.
- **tcgcsv:** arquivo só existe até D-1; alguns grupos antigos têm `publishedOn` placeholder = data de hoje (ex.: POP Series, Nintendo Promos com 2026-09-05) — excluir por `groupId < 24000`. Importar `pull_pc.py` executava a cesta inteira (código de módulo) — já corrigido com `if __name__ == '__main__'`.
- **Fontes com COI** dominam o tema (dealers, graduadoras, marketplaces, blogs afiliados). Os únicos quantitativos quase independentes achados: TCGinvest (2026) e Wooster (2024), ambos sobre PriceCharting.
- O operador mandou **parar** no meio; o pedido de handoff veio depois. Não retome sem o operador pedir.

---

## 6. Inventário de arquivos deste handoff

```
HANDOFF-POKEMON-TCG-INVESTMENT-ANALYSIS.md            este arquivo
tooling/pokemon-investment-analysis/
  scripts/fetch_hist.py        baixa arquivos diários do tcgcsv e extrai a categoria Pokémon → cat3/<data>.json
  scripts/fetch_products.py    metadados de produto por grupo → products3.json (exige groups3.json)
  scripts/analyze.py           janelas de retorno por segmento + índice mensal (windows.md/json, monthly_index.md)
  scripts/pull_pc.py           cesta PriceCharting (chart_data por grau) + parser
  scripts/pull_direct.py       slugs diretos para os itens que a busca não resolve
  scripts/pull_volumes.py      frequência de vendas por grau (liquidez)
  data/tcgcsv_windows_compact.md / tcgcsv_windows_full.md / tcgcsv_monthly_index.md
  data/tcgcsv_postrelease_sealed.md / tcgcsv_groups_pokemon.md / tcgcsv_dates_used.txt
  data/pricecharting_basket.md / pricecharting_sales_frequency.md
  research/research_prices_liquidity.md      frente concluída (93 fontes)
  research/research_grading_populations.md   frente concluída (99 fontes)
```

---

## Apêndice A — Prompt original do operador (verbatim)

```
# PAPEL / PERSONA

Atue como um analista independente especializado em mercados de colecionáveis, Pokémon Trading Card Game (TCG), comportamento do consumidor e avaliação de investimentos alternativos.

Sua postura deve ser investigativa, crítica e imparcial. Não atue como vendedor, influenciador ou entusiasta tentando justificar uma compra. Procure tanto evidências favoráveis quanto evidências que possam invalidar a tese de investimento.


# CONTEXTO

Quero avaliar se vale a pena investir em produtos físicos de Pokémon TCG em língua inglesa nos próximos anos.

Meu interesse principal é entender se a adoção está crescendo de maneira estrutural, sustentável e duradoura ou se a demanda depende principalmente de fatores temporários, especulação, nostalgia e ciclos de atenção.

Considere um horizonte principal de investimento de 3 a 5 anos e uma perspectiva estrutural de 5 a 10 anos.

O objeto da análise são cartas e produtos impressos em inglês, negociados no mercado internacional. Não confunda "produtos em inglês" com "mercado localizado apenas na Inglaterra" ou "apenas nos Estados Unidos".

Use USD como moeda de referência. Não presuma meu patrimônio, tolerância a risco ou residência fiscal. Caso apresente implicações para um investidor no Brasil, trate-as em uma seção separada e condicional, considerando câmbio, importação, tributação e liquidez local.

Não estou buscando recomendações de compras motivadas por lançamentos ou ganhos rápidos. Quero testar a solidez da tese de investimento.


# PERGUNTA CENTRAL

As evidências disponíveis indicam que a adoção de Pokémon TCG em inglês está em ascensão estrutural e tem condições de se sustentar nos próximos anos? Mesmo que essa adoção seja duradoura, os preços, a oferta e a liquidez atuais tornam esse mercado atrativo para investimento?

Responda separadamente:

A. A base de consumidores e colecionadores está crescendo?
B. Esse crescimento parece sustentável?
C. Esse crescimento pode resultar em valorização dos produtos existentes, ou a oferta tende a absorver a demanda?
D. O retorno potencial líquido compensa os riscos, o trabalho operacional e o custo de oportunidade?


# TAREFAS DA ANÁLISE

## 1. Delimite e segmente o mercado

Não trate todo o mercado como um único ativo. Diferencie, no mínimo:

- Produtos selados de edições recentes.
- Produtos selados de edições antigas.
- Cartas individuais sem graduação, separando valor colecionável e utilidade competitiva.
- Cartas graduadas, distinguindo modernas e antigas.

Defina o que considera "recente", "antigo" e "moderno", quando essas distinções forem relevantes.

Explique como os segmentos diferem em demanda, oferta futura, escassez efetiva, liquidez, formação de preços e dependência de condições excepcionais de conservação ou graduação.

Não use o desempenho de algumas cartas famosas como representação automática de todo o mercado.


## 2. Investigue a trajetória da adoção e a qualidade da demanda

Examine a evolução histórica dos últimos 10 anos, quando houver dados confiáveis, dando atenção especial aos últimos 24 a 36 meses.

Procure distinguir crescimento estrutural, expansão cíclica, efeitos extraordinários e possíveis correções.

Avalie indicadores como participação em eventos oficiais, atividade em lojas, compradores ativos, frequência de compra, volume de transações, interesse de busca, disponibilidade no varejo e entrada de novos participantes.

Para cada indicador relevante, explique:
- O que ele efetivamente mede.
- O período e a abrangência geográfica dos dados.
- Se cobre produtos em inglês ou o mercado global de Pokémon.
- O que permite concluir e o que não permite concluir.

Separe a demanda de jogadores, colecionadores, consumidores ocasionais, revendedores e investidores, reconhecendo que essas categorias podem se sobrepor.

Investigue especialmente:
- Entrada de novos participantes versus aumento do gasto dos participantes existentes.
- Retenção e compras recorrentes versus interesse pontual.
- Renovação geracional versus dependência de consumidores nostálgicos.
- Consumo por abertura de produtos versus acumulação de estoque para revenda.
- Participação que provavelmente persistiria mesmo sem expectativa de valorização.

Não use alta de preços, faturamento nominal, buscas na internet, tiragem ou quantidade de cartas graduadas, isoladamente, como prova de adoção sustentável.

Quando não houver dados públicos de compradores únicos, retenção ou perfil dos participantes, declare a lacuna e use indicadores indiretos com cautela. Não invente essas métricas.


## 3. Teste a durabilidade da demanda e a resposta da oferta

Analise os fatores que podem sustentar ou enfraquecer a adoção:

Renovação do público, força da propriedade intelectual, comunidade, jogo organizado, experiência de colecionar, canais de distribuição, concorrência de outros hobbies e TCGs, renda disponível, fadiga de lançamentos e sensibilidade à especulação.

Diferencie a popularidade geral da franquia Pokémon da demanda específica por cartas físicas em inglês.

Do lado da oferta, investigue impressão, reimpressões, disponibilidade, estoque acumulado por investidores e revendedores, quantidade de produtos preservados lacrados e crescimento das populações de cartas graduadas.

Diferencie:
- Escassez comprovada.
- Falta temporária de estoque.
- Escassez de uma condição ou graduação específica.
- Narrativas de raridade sem evidência suficiente.

Não presuma que todo produto antigo seja raro nem que todo produto selado se valorize com o tempo.

Teste explicitamente a hipótese de que a adoção possa continuar crescendo, mas a valorização seja limitada pelo aumento da oferta ou por preços de entrada elevados.


## 4. Avalie a atratividade econômica do investimento

Examine se os preços atuais parecem compatíveis com os fundamentos identificados ou se já exigem um cenário muito otimista.

Quando houver dados comparáveis, analise valorização histórica, quedas, volatilidade, tempo de recuperação e liquidez. Explique limitações de amostragem, seleção de produtos vencedores e ausência de índices representativos.

Utilize transações efetivamente concluídas sempre que possível. Não confunda preços anunciados, estimativas de plataformas ou recordes de leilão com preços realizáveis para um investidor comum.

Considere o retorno líquido após custos relevantes, como:
Comissões, diferença entre compra e venda, frete, seguro, armazenamento, conservação, graduação, tributos aplicáveis e eventuais perdas por fraude ou danos.

Avalie também o tempo necessário para vender, a profundidade da demanda e o desconto que pode ser necessário para liquidar posições maiores ou em momentos de retração.

Apresente um exemplo numérico claramente identificado como ilustrativo, mostrando:
- Custo total de entrada.
- Custos de manutenção e saída.
- Valorização bruta necessária para atingir o ponto de equilíbrio.
- Retorno líquido anualizado sob premissas explícitas.

Compare o investimento com alternativas líquidas e diversificadas, usando a mesma moeda e o mesmo horizonte. Não trate retornos futuros dessas alternativas como garantidos.

A conclusão deve distinguir "o hobby continuará relevante" de "comprar aos preços atuais oferece uma relação risco-retorno atrativa".


## 5. Construa cenários e tente refutar a tese

Elabore três cenários para os próximos 3 a 5 anos: otimista, base e pessimista. Discuta também as implicações estruturais para 5 a 10 anos.

Para cada cenário, apresente:
- Premissas sobre adoção, retenção e gasto dos consumidores.
- Evolução provável da oferta e do estoque disponível para revenda.
- Consequências para preços e liquidez por segmento.
- Sinais observáveis que indicariam sua materialização.
- Fatores que poderiam invalidá-lo.

Não invente metas de preço, taxas de crescimento ou probabilidades para preencher tabelas. Quando houver projeções quantitativas, mostre sua base e separe dados observados de hipóteses.

Apresente a melhor tese favorável e a melhor tese contrária ao investimento. Compare a qualidade das evidências de ambas, sem forçar uma falsa equivalência.

Responda também:
"O que precisaria acontecer para que a adoção permanecesse forte, mas o investidor ainda assim tivesse um resultado ruim?"


## 6. Produza uma conclusão decisória e um plano de acompanhamento

Classifique separadamente:

Adoção:
- Expansão estrutural.
- Expansão predominantemente cíclica ou especulativa.
- Estabilidade ou maturidade.
- Retração.
- Evidência insuficiente.

Atratividade para investimento:
- Favorável sob condições claramente definidas.
- Seletiva, dependendo do segmento e do preço de entrada.
- Desfavorável nas condições analisadas.
- Evidência insuficiente.

Não transforme essas classificações em uma recomendação personalizada, pois meu perfil financeiro não foi informado.

Explique quais segmentos têm fundamentos relativamente mais sólidos, quais dependem mais de especulação e quais condições justificariam investir, aguardar ou evitar exposição.

Finalize com 6 a 8 indicadores para acompanhar trimestral ou semestralmente. Informe a fonte, a interpretação e os sinais que fortaleceriam ou enfraqueceriam a tese. Se propuser limites numéricos, justifique-os ou identifique-os como critérios analíticos, não como fatos estabelecidos.


# REGRAS DE PESQUISA E RESTRIÇÕES

Faça pesquisa atualizada e informe a data de corte da análise.

Priorize fontes primárias e dados verificáveis: divulgações oficiais da The Pokémon Company, informações de Play! Pokémon, dados de eventos, transações de marketplaces e relatórios de populações de empresas de graduação.

Use fontes secundárias confiáveis para complementar e contextualizar. Conteúdo de lojas, influenciadores e empresas interessadas em vender ou graduar cartas deve ser identificado como potencialmente sujeito a conflitos de interesse.

Para as principais conclusões, busque confirmação independente quando possível. Duas matérias que reproduzem a mesma informação original não contam como duas evidências independentes.

Identifique a data de publicação e o período a que os dados se referem. Não apresente dados antigos como retrato atual.

Não extrapole automaticamente dados da franquia inteira, de todas as línguas ou de um único país para o mercado de cartas em inglês.

Separe claramente:
1. Fatos observados.
2. Inferências sustentadas por evidências.
3. Hipóteses e projeções.

Não invente dados, fontes, vendas, índices ou acesso a bases privadas. Quando uma informação não estiver disponível ou verificável, diga isso e explique como a lacuna reduz a confiança da conclusão.

Evite linguagem promocional, afirmações de valorização garantida e generalizações como "Pokémon sempre sobe".

Não confunda ausência de evidência de enfraquecimento com comprovação de crescimento sustentável.


# FORMATO DE SAÍDA

Organize o relatório em:

1. Resumo executivo com respostas diretas sobre adoção, sustentabilidade e atratividade do investimento, indicando o grau de confiança de cada conclusão.
2. Quadro dos principais indicadores, evidências, tendências e limitações.
3. Análise da qualidade e durabilidade da demanda.
4. Comparação dos segmentos: oferta, riscos, liquidez e condições de atratividade.
5. Avaliação econômica e exemplo de retorno líquido.
6. Tabela com os três cenários.
7. Melhor argumento favorável, melhor argumento contrário e veredito condicionado às evidências.
8. Indicadores de acompanhamento e fatos que fariam você mudar de opinião.
9. Fontes com links, datas e indicação das principais lacunas de informação.

Escreva em português do Brasil, com linguagem clara. Explique termos técnicos quando necessários.

Inclua citações junto às afirmações relevantes, não apenas uma lista de referências ao final.

Priorize profundidade analítica, evidências e implicações para a decisão. Evite uma longa introdução sobre a história de Pokémon ou repetições entre seções.

Ao final, responda de forma objetiva:
"A tese de investir em Pokémon TCG em inglês está sustentada principalmente por adoção duradoura, por expectativas especulativas ou por uma combinação das duas? E quanto dessa tese parece já estar refletido nos preços atuais?"
```

---

## Apêndice B — Briefs das 4 frentes pendentes (prompts dos agentes, em inglês; reutilizar com orçamento menor e gravação progressiva)

Regras comuns a todos (repetir no prompt): para CADA fato registrar URL, título, publicador, data de publicação, período a que o dado se refere, escopo geográfico, se cobre produtos em inglês ou a franquia global, e o número/trecho verbatim; marcar PRIMÁRIA vs SECUNDÁRIA e sinalizar conflito de interesse; nunca inventar — escrever "NOT FOUND" e o que foi tentado; duas matérias que repetem a mesma fonte não são duas evidências; **gravar achados parciais em `tooling/pokemon-investment-analysis/research/research_<frente>.md` a cada lote de buscas**; reportar em markdown estruturado com lista numerada de fontes.

### B1 — TPC oficial / Play! Pokémon / franquia
1. Cumulative Pokémon TCG cards produced (official milestones: ~52.9 billion as of March 2023, 64.8 billion as of March 2024; find March 2025 and, if published, March 2026; countries/regions and languages). Cite the official corporate page/press release with exact wording and "as of" date.
2. The Pokémon Company financial results filed in Japan (Kanpo) — revenue, operating profit, net profit for FY ending Feb 2023, Feb 2024, Feb 2025, and Feb 2026 if reported (Gamesindustry.biz, Nikkei, Serkan Toto, Bloomberg). Note: whole franchise, global, not only English cards.
3. Pokémon global licensed merchandise retail sales estimates (License Global "Top Global Licensors", 2023–2026), noting they are estimates covering all merchandise.
4. Play! Pokémon: World Championships 2024 (Honolulu), 2025 (Anaheim), 2026 (San Francisco, Aug 2026) — TCG competitors, attendees, viewership; record Regionals/Internationals attendance 2025–2026 (EUIC, NAIC, LAIC, OCIC; largest by TCG masters count); TPCi statements on organized play growth, number of events, Championship Points changes, League Cups/Challenges, Play! Pokémon app. Note whether counts are TCG only or TCG+VGC+GO+Unite.
5. Official TPCi statements (press releases, executive interviews — Forbes, Polygon, IGN, Bloomberg, Nikkei) on 2024–2026 demand, production increases, "printing at maximum capacity", reprint commitments, new printing facilities, product allocation, 30th anniversary (2026) plans.
6. Pokémon TCG Pocket (launched Oct 30 2024): downloads and revenue milestones (Sensor Tower / AppMagic / official), and any statements/evidence about its effect on physical demand. Flag that app data is not physical card data.
7. Official data on number of players, Pokémon Trainer Club accounts, TCG Live users.

### B2 — Oferta, impressão, varejo, MSRP
1. English set release calendar 2023–2026 with dates (SV era through Mega Evolution era; late-2026 / 30th anniversary schedule) and a table of main English expansions per year 2016–2026. (Nota: a tabela já existe em `data/tcgcsv_groups_pokemon.md` — usar como base e só confirmar/complementar.)
2. MSRP history of booster packs, ETBs, booster bundles, booster boxes (pack $3.99→$4.49 in 2023?; any 2025/2026 increase and the reason — tariffs, costs), with TPCi statements or retailer listings/press.
3. Reprint policy and evidence: TPCi statements that 151, Prismatic Evolutions, Evolving Skies, Crown Zenith etc. were/are reprinted; how long reprint waves continued; confirm TPC does not publish print-run numbers.
4. Retail availability 2024–2026: 2025 stock-outs, Target pausing in-store card sales (May 2025), Walmart/Costco restrictions, scalping/fights news, Pokémon Center limits; whether availability normalized by mid/late 2026 (products at/below MSRP; price drops). Evidence in both directions.
5. Printing capacity: who prints English cards (Millennium Print Group, NC — TPCi-owned since 2022; European printers e.g. Cartamundi; expansions/new plants 2023–2026); 2025 US tariff effects.
6. Circana (NPD) trading-card/collectibles category growth for the US in 2023, 2024, 2025, H1 2026; Pokémon as top property (dollar sales, not unique buyers); GameStop earnings commentary 2025–2026 (trading cards, in-store PSA grading); big-box retailer statements.
7. Secondary-market sealed inventory accumulation: estimates of boxes/ETBs held by investors/resellers (with source), the "sealed investing" narrative, and counter-evidence (large quantities of older sealed still listed on TCGplayer/eBay in 2026, with listing counts if available).
8. Counterfeits/resealed products as supply risk (2024–2026 seizures/news with numbers).

### B3 — Qualidade da demanda, concorrência, riscos
1. Buyer demographics (age, adults vs children, collectors vs players vs investors/resellers) from TPCi, Circana, YouGov, Morning Consult, eBay/TCGplayer, academic studies, Statista; new entrants vs increased spend; retention/repeat purchase; nostalgia cohort (born ~1990–2000) vs younger cohorts (Gen Alpha / TCG Pocket).
2. Search-interest and attention-cycle data: Google Trends "Pokémon cards" 2016–2026 (2020–21 spike, 2022–23 decline, 2024–26 surge — press quoting levels with dates); live-breaking growth (Whatnot GMV in cards 2024–2026, eBay Live, TikTok Shop); number of local game stores / Play! Pokémon retailers if any figure exists.
3. Competition 2023–2026 with numbers: Magic (Hasbro Wizards segment 2023–2025, Final Fantasy record), One Piece (Bandai), Disney Lorcana (Ravensburger), Star Wars Unlimited, Riftbound (2025), Gundam (2025), Union Arena; sports cards (Fanatics/Topps); overall TCG market size estimates 2024–2026 (ICv2 North America hobby-games reports; methodology) and Pokémon's share per ICv2.
4. TCG Pocket and TCG Live: downloads, MAU/DAU, revenue; cannibalization vs funnel evidence; franchise pipeline 2025–2027 (Legends Z-A Oct 2025, Pokémon Champions, 30th anniversary 2026, new mainline games, Netflix/anime).
5. Fatigue/saturation signs: "too many sets", "Pokémon bubble", burnout, scalper exit, store owners on slowing sell-through in 2026, recent-set product below MSRP (Destined Rivals, Mega Evolution), and counter-evidence (continued sell-outs). Name conflicts of interest.
6. Macro: US discretionary hobby spending 2025–2026, tariffs, inflation; the 2021 stimulus-boom narrative and 2022 reversal (data on 2022 price declines).
7. Fraud/scams/legal: counterfeit and resealed seizures (2024–2026), lawsuits (loot-box mechanics, gambling concerns about rip-and-ship/live breaking, state regulation), theft incidents; platform policy risks (eBay/TCGplayer).
8. Organized play as a durable-demand pillar vs collecting: share of demand from players (competitive staples) vs collectors (chase cards) — TCGplayer statements on what sells; competitive-only cards losing value on Standard rotation (dates and price effects).

### B4 — Brasil (condicional)
1. Import taxation for individuals in 2026: Remessa Conforme (20% federal up to US$50; 60% above with US$20 deduction; ICMS 17–20% by state; effective total on US$100 and US$1,000 examples), Correios/DHL/FedEx dispatch fees, 2025–2026 changes/proposals ("taxa das blusinhas"). Cite Receita Federal/official + reliable press.
2. Exporting/selling abroad from Brazil (eBay US, consignment to Probstein/PWCC/Fanatics): shipping options and costs (Correios Exporta Fácil limits, DHL/FedEx), customs declaration, insurance, transit time; US de minimis end (Aug 2025) and what applies to a private seller shipping a card to a US buyer.
3. Brazilian income tax on gains from selling collectibles as an individual: ganho de capital rules — R$35,000/month exemption for "bens de pequeno valor" (same nature), 15% rate (progressive to 22.5%), GCAP and DARF deadline, declaring assets in DIRPF; treatment if habitual (commercial activity, CNPJ/MEI). Not tax advice — record rules with sources.
4. USD/BRL: level in Sept 2026 and path 2020–2026 (annual averages/year-end); IOF on international card purchases (2026 rate) and remittances.
5. Domestic market for English cards: Liga Pokémon/LigaMagic, MYP Cards, Mercado Livre, Shopee — volume/user data, typical premiums vs US prices; Copag (official printer of Portuguese-language sets, Cartamundi) and Copag/TPCi statements on Brazilian growth 2024–2026; Brazilian Regionals/LAIC attendance; Pokémon Center Brazil plans; Play! Pokémon Brazil.
6. Liquidity constraints for high-value English cards in Brazil (few listings, time-to-sell for US$500+), fraud/counterfeits in Brazilian marketplaces, whether Brazilian sellers commonly export to the US.

---

## Apêndice C — Regenerar os dados primários (≈10 min)

```bash
cd /home/user/scanners-commons/tooling/pokemon-investment-analysis
pip install -q py7zr
mkdir -p work && cd work
curl -sS https://tcgcsv.com/tcgplayer/3/groups -o groups3.json
python3 - <<'EOF'
from datetime import date
ds=[date(y,m,8).isoformat() for y in (2024,2025,2026) for m in range(1,13) if date(2024,2,8)<=date(y,m,8)<=date.today()]
open('dates.txt','w').write(' '.join(ds)); print(len(ds), ds[0], ds[-1])
EOF
# acrescente ao dates.txt a data mais recente disponível (o arquivo do tcgcsv é D-1):
python3 ../scripts/fetch_hist.py $(cat dates.txt) 2026-09-05      # troque pela data mais recente
python3 ../scripts/fetch_products.py                                 # ~220 requests, ~1 min
python3 ../scripts/analyze.py                                        # gera windows.md, windows.json, monthly_index.md
# PriceCharting (cesta de 44 itens; ~3 min; pausa de 1,2–1,3 s entre requests):
cd .. && python3 scripts/pull_pc.py && python3 scripts/pull_direct.py && python3 scripts/pull_volumes.py
```

`analyze.py` lê `products3.json`, `groups3.json`, `dates.txt` e `cat3/<data>.json` do diretório atual. A tabela pós-lançamento e os cálculos extras (concentração de ganhos, SKUs por ano, níveis de preço, low/market, drawdown) foram feitos com trechos ad hoc sobre os mesmos JSONs — o racional está na seção 2.1; reimplementar leva minutos.
