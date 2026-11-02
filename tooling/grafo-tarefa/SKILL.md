---
name: grafo-tarefa
description: >-
  Executa uma tarefa grande e REPETÍVEL como um grafo de etapas pequenas
  (nós), cada uma com entrada, saída e checagem, e só conclui quando os
  critérios de aceite definidos ANTES de começar são cumpridos com evidência.
  Passo com resposta única (juntar, ordenar, contar, deduplicar, comparar
  preço) vira código, nunca chamada de modelo. Deixa graph.md e checks.md para
  outra sessão repetir ou continuar. Acione quando o operador disser "roda em
  grafo", "faz em etapas com checagem", "grafo de tarefa", "quero o pronto
  definido antes", ou ao montar pipeline que se repete: rodada de scanners
  (MYP, CardTrader, Liga), scraper de população da PSA, cruzamento de preço
  raw x PSA 10. Não use em pedido simples, em tarefa fiscal no Bling (cada
  passo exige aprovação) nem para construir coisa nova do zero — aí o caminho
  é planejar com o operador antes.
---

# Grafo de tarefa

Origem: pendencias#31 (2026-11-02) — versão própria da frota, inspirada no
método "autoresearch" (etapas pequenas + portões com evidência). Não depende
de nenhum prompt de terceiro.

Por que existe: tarefa longa feita "de uma vez" termina quando o modelo *acha*
que terminou. Aqui ela termina quando cada checagem observável passou — e o
que deu certo fica escrito para a próxima rodada começar dali.

## 0. Definir o pronto (antes de qualquer ferramenta)

Preencha; se faltar algo que **muda o grafo**, pergunte **uma vez** (uma
pergunta por turno). O resto vira suposição declarada no `graph.md`.

```
TAREFA:
ENTREGA e caminho de saída:
CHECAGENS de aceite (observáveis: arquivo existe e abre, colunas certas,
  contagem bate com o dado real, link abre):
FONTES:
ESCOPO (pastas e arquivos que pode alterar):
LIMITE (tempo, rodadas, chamadas de API ou créditos):
```

## Regras fixas (valem em todo nó)

- **Nunca inventar preço nem dado.** Fonte falhou → `n/d`/erro rotulado e segue;
  jamais preencher número para fechar um portão.
- **Nunca recomendar compra** nem comprar, vender ou alterar preço em
  marketplace; só avaliar.
- **Entrega da frota sai da ferramenta do repo** (ex.: `myp_summary.py`,
  `cardtrader_postprocess.py`, `ebay_summary.py`), colada verbatim — nó de IA
  não remonta tabela de entrega.
- Nunca transmitir NF-e, lançar estoque ou gerar contas no Bling sem
  autorização expressa.
- Perguntar antes de publicar, enviar mensagem ou gastar dinheiro/créditos
  pagos (Firecrawl, Apify, APIs com cota).
- Token, senha e chave nunca entram no repositório nem no `graph.md`.
- Dois nós nunca editam o mesmo arquivo. Guardar versão recuperável (commit ou
  cópia) antes de juntar mudanças arriscadas.

## 1. Dividir

Quebre em **nós**: uma entrada, uma saída, uma checagem. Ligue nós só quando
um usa a saída do outro; sem ligação, rodam em paralelo. Escreva nós,
ligações e checagens em `graph.md` e **mostre antes de executar**.

```markdown
| Nó | Tipo | Entrada | Saída | Checagem |
|---|---|---|---|---|
| N1 | IA | ... | ... | ... |
| N2 | Código | saída N1 | arquivo.csv | nº de linhas = nº de cartas do set |
```

## 2. Código ou IA

Passo com **uma única resposta certa** (juntar, ordenar, contar, deduplicar,
normalizar coluna, comparar preço, filtrar por limiar) é **código Python**,
nunca chamada de modelo. Marque os nós de código no `graph.md`. IA fica para o
que exige julgamento: descobrir estrutura de uma fonte, explicar divergência,
escrever o relatório final.

## 3. Executar

Cada nó de IA roda como subagente só com o contexto de que precisa e devolve:
**caminho da saída · veredito · evidência**.

- Se os subagentes da frota existirem (pendencias#11): `rapido` para tarefa
  mecânica, `padrao` para implementação comum, `profundo` para arquitetura ou
  bug sem causa óbvia.
- Se não existirem: use o subagente geral. O método é o mesmo; só não há
  escolha de modelo por nó.

## 4. Portões

Toda passagem com risco tem portão. Ele abre com evidência, nesta ordem de
força: **checagem automática → relatório do nó → confiança do modelo**.
Confiança sozinha nunca abre portão.

Registre em `checks.md`:

```markdown
| Nó | Requisito | Veredito (passou / falhou / pendente) | Evidência |
|---|---|---|---|
```

## 5. Voltas

- **Correção:** portão reprovado devolve **só aquele nó**, com motivo e
  evidência. Máximo **3 tentativas**; na 3ª falha o nó vira pendência
  declarada, não gambiarra.
- **Aprendizado:** resultado aceito vira regra escrita no `graph.md` (seção
  "Regras aprendidas") para a próxima rodada começar dali.

## 6. Conclusão

Conclua **só** quando: toda saída existe e abre; todo portão rodou na versão
salva; falhas foram corrigidas ou relatadas; o `graph.md` bate com o que de
fato rodou. Bateu no LIMITE → entregue status **parcial** com os nós que
faltam. **Nunca afrouxe um portão para terminar.**

## Entrega

Saída + `graph.md` + `checks.md` + resumo no formato da frota:
**Objetivo** (1 linha) → **O que foi feito** (bullets com o porquê) →
**Dependências/pendências**. `graph.md`/`checks.md` com dado de scan ficam em
pasta local gitignored (`results/`, `outputs/`), nunca em repo público.

## Quando NÃO usar

- Pergunta rápida, edição de uma linha, ajuste pontual.
- Tarefa fiscal no Bling ou qualquer fluxo em que cada passo exige aprovação
  humana.
- Construção de coisa nova do zero (painel, app): primeiro feche a decisão com
  o operador (`grill-me`); o grafo é para o que se **repete**.
