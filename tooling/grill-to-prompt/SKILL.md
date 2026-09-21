---
name: grill-to-prompt
description: >-
  Pipeline em duas fases na MESMA conversa: entrevista socrática (`grill-me`,
  uma pergunta por vez) até a ideia vaga virar decisão fechada e, em seguida,
  compilação do fechamento num prompt pronto pra colar (`prompt-master-tcg`) —
  sem repetir pergunta entre as fases e sem congelar suposição dentro do
  prompt. Acione quando o operador disser "me grelha e depois vira prompt",
  "grelha isso e me dá o prompt", "entrevista e compila", "quero sair daqui
  com o prompt pronto", "grill to prompt", ou quando ele tiver uma ideia crua
  de tarefa e disser que vai executar em OUTRA sessão/ferramenta (Claude Code,
  Cowork, ChatGPT, n8n). Não ativa quando ele quer só clareza (`grill-me`), só
  o prompt a partir de pedido já fechado (`prompt-master-tcg`) ou a tarefa
  executada aqui.
---

# Grill to prompt

Skill de **cola**: não reescreve nenhuma das duas skills-mãe. Carrega cada uma
na sua fase e fixa o **contrato de passagem** entre elas. O método (lentes,
bifurcação, critério de parada, roteamento por ferramenta, checklist) continua
morando em `grill-me` e `prompt-master-tcg` — se uma das duas não estiver
instalada na conta, avise em uma linha e pare; não improvise o método de cabeça.

## Por que a ordem é fixa (grelhar → compilar, nunca o inverso)

- `prompt-master-tcg` faz **no máximo 3 perguntas** e assume o resto. Pedido
  vago entra, suposição sai **congelada dentro do prompt**. Grelhar depois
  reabre o que o prompt já fechou — e o prompt é reescrito duas vezes.
- O fechamento do `grill-me` (Decisão · Fechado · Premissas · Em aberto ·
  Próximo passo) é exatamente o insumo que o `prompt-master-tcg` extrai no
  Passo 1 dele (tarefa precisa, ferramenta, formato, restrições, critério de
  sucesso). A entrevista **gasta o orçamento de perguntas da compilação** —
  por isso a Fase 2 não pergunta nada.

## Fase 0 — Triagem (silenciosa, antes do primeiro turno)

Verifique se o pedido já traz, de forma inequívoca:

1. **ferramenta-alvo** (Claude chat / Claude Code / Cowork / ChatGPT / n8n / outra);
2. **formato de saída** (tabela, XLSX, `.md`, script, copy…);
3. **critério de sucesso binário** ("pronto quando…");
4. **o que é decisão em aberto** vs. **o que já está fechado e não é pra reabrir**.

- **Os quatro claros** → pule a Fase 1. Avise em uma linha ("já está fechado;
  indo direto pro prompt") e vá pra Fase 2. Grelhar decisão tomada é cerimônia.
- **Faltando qualquer um** → Fase 1.
- Em qualquer caso, classifique a **frente**: uma das A–E do
  `prompt-master-tcg` (scanners/arbitragem, loja US, sourcing, dev, conteúdo)
  **ou fora de TCG**. Fora de TCG, a Fase 2 roda **sem bloco de contexto
  fixo** — senão o prompt nasce com a frente errada injetada.

## Fase 1 — Grelhar

Carregue a skill **`grill-me`** e siga-a integralmente: abertura com o alvo
confirmado em uma linha, **uma pergunta por turno**, teste da bifurcação,
verificação silenciosa do que está no repo, parada quando o desconhecido não
muda mais a ação, fechamento no formato fixo.

Três diferenças por estar dentro do pipeline:

1. **Perguntas que a Fase 2 faria entram aqui.** Antes de fechar, garanta
   resposta (dele, ou verificada por você em silêncio) para: ferramenta-alvo,
   formato de saída, critério de sucesso. Cada uma passa pelo teste da
   bifurcação como qualquer outra — mas nenhuma pode chegar ao fechamento sem
   resposta ou sem estar registrada em **Em aberto**.
2. **O fechamento ganha uma linha extra**, logo após "Próximo passo":
   ```
   **Compilar para:** <ferramenta> · <formato> · <frente A–E | fora de TCG>
   ```
3. **Checkpoint de um turno.** Termine o fechamento com uma linha: *"Confirma o
   fechamento? No próximo turno sai o prompt."* Compilar um recap errado é
   mais caro que um turno — e o `grill-me` avisa que atribuir ao operador uma
   posição que ele não tomou é o erro que ninguém nota. Se ele já tiver dito
   "chega, manda o prompt", pule o checkpoint. **Não** ofereça o menu "virar
   prompt / virar doc / executar" do `grill-me`: o próximo passo já é o prompt.

## Fase 2 — Compilar

Carregue a skill **`prompt-master-tcg`** e entregue no formato dela (um bloco
de código com o prompt · `🎯 Alvo` · `💡 uma frase` · nota de setup só se
necessária). Cinco diferenças por estar dentro do pipeline:

1. **Zero perguntas.** O orçamento de 3 foi gasto na Fase 1. O que ficou em
   **Em aberto** não vira pergunta nem suposição silenciosa: entra no prompt
   como `[PLACEHOLDER: …]` ou, em ferramenta agêntica, como "pare e pergunte
   antes de …".
2. **Mapa fechamento → prompt** (nada do fechamento pode sumir):

   | Linha do fechamento | Vira no prompt |
   |---|---|
   | **Decisão** | a tarefa/operação precisa; em agêntico, o *estado alvo* |
   | **Fechado** | restrições, *Pode / Não pode*, formato de saída, "não rediscutir" |
   | **Premissas** | bloco `## Contexto (carregar adiante)` com as suposições **explícitas** ("assuma X") — nunca embutidas como fato |
   | **Em aberto** | `[PLACEHOLDER]` ou checkpoint de revisão humana |
   | **Próximo passo** | *estado inicial* + condição de parada / "Pronto quando" |
   | **Compilar para** | `🎯 Alvo`, roteamento por ferramenta, idioma do prompt |

3. **Memory Block é obrigatório** (no `prompt-master-tcg` ele é condicional):
   "Decisões já tomadas" = o **Fechado**; "Restrições de turnos anteriores" =
   vetos e premissas; "Já tentado e falhou" = o que a lente *alternativa
   descartada* revelou na entrevista.
4. **Bloco de contexto fixo: só o da frente detectada na Fase 0**; fora de
   TCG, **nenhum**. Frase que mistura duas frentes segue a regra da skill-mãe:
   Prompt 1 e Prompt 2.
5. **Verificação final** = o checklist do `prompt-master-tcg` **+ um item**:
   *cada linha de Fechado e de Em aberto do fechamento aparece no prompt?* Se
   alguma sumiu, a compilação perdeu o que a entrevista pagou pra descobrir.

## Regras da frota que atravessam as duas fases

- **Nunca recomendar compra**: prompt sobre scan/deal pede margem, flags e
  fontes; a decisão de capital é do operador.
- **Nunca credencial** no prompt ("assume que [serviço] já está autenticado").
- **Formato de resposta:** na Fase 1 vale o do `grill-me` (pergunta em 1–2
  linhas, sem preâmbulo) — ele vence o padrão Objetivo → O que foi feito →
  Dependências. Na Fase 2 a saída é a do `prompt-master-tcg`. O teto de 200
  palavras só volta a valer se houver prosa fora dessas duas saídas.
- **Invocação explícita.** Skill de conversa dispara pouco sozinha (medido na
  frota em 2026-09-21: ~18% dos positivos). Quando quiser o pipeline, chame
  pelo nome: "usa a skill `grill-to-prompt`" ou `/grill-to-prompt`.

## Anti-padrões

- Compilar sem fechamento ("juntar as respostas de cabeça" e pular o recap).
- Perguntar na Fase 2 o que a Fase 1 já cobriu — ou o que ela deixou em
  aberto de propósito.
- Congelar um **Em aberto** como fato dentro do prompt.
- Injetar bloco de contexto TCG em tema fora de TCG.
- Grelhar pedido já fechado (ferramenta + formato + critério claros).
- Reescrever o método das skills-mãe aqui em vez de carregá-las.
