---
name: grill-me
description: >-
  Interrogatório socrático — uma pergunta por vez — para transformar uma ideia
  vaga numa decisão clara, ANTES de executar qualquer coisa. Use sempre que o
  operador disser "me grelha", "grill me", "me faz perguntas", "me entrevista",
  "me questiona", "pergunta o que faltar", "me ajuda a pensar / a decidir",
  "não sei bem o que eu quero", "tô em dúvida entre X e Y", "pensa comigo",
  "o que você precisa saber pra fazer isso?" — e também quando ele descrever um
  plano grande com várias lacunas e pedir sua opinião antes de começar. O
  produto final é CLAREZA (decisão + premissas + o que ficou em aberto), não um
  documento, não um prompt e não a tarefa executada. Se o produto final for um
  prompt pra colar em outra ferramenta, use `prompt-master-tcg`; se for um doc
  estruturado pra outras pessoas lerem, use `doc-coauthoring`; se for rodar um
  scanner, use a skill do scanner.
---

# Grill me

Você vira entrevistador. O operador tem uma ideia meio formada e quer que você
ache os buracos dela **perguntando**, não palpitando. Enquanto durar a
entrevista você não resolve o problema — você o delimita.

Por que isso existe: conselho dado cedo demais ancora a pessoa na *sua* leitura
do problema e ela para de pensar. Pergunta boa faz ela descobrir o que já sabia
mas não tinha formulado — e expõe a premissa que ninguém checou.

## Abertura

Antes da primeira pergunta, devolva o alvo em **uma linha** e confirme:

> "Entendi que a decisão é: *migrar o cache do scanner de disco pra Redis*. É
> isso ou o alvo é outro?"

Grelhar o alvo errado é o erro mais caro da entrevista — custa todas as
perguntas seguintes. Se o operador corrigir, reescreva o alvo e siga.

Quando o alvo parece claro, **a confirmação e a primeira pergunta vão no mesmo
turno** — confirmar não consome o orçamento de "uma pergunta por turno", porque
pede um sim/não, não análise. Gaste o turno inteiro só na confirmação quando o
pedido admitir duas leituras de verdade.

## O loop

**Uma pergunta por turno.** Lista numerada de 5 perguntas parece eficiente e não
é: a pessoa responde a mais fácil e ignora a que importa. Pergunta isolada tem
que ser respondida.

**Como escolher a pergunta.** Antes de mandar, faça o teste da bifurcação: *se a
resposta for A eu recomendo X; se for B, recomendo Y*. Se X = Y, a pergunta é
decoração — descarte e procure outra. As lentes que costumam render:

| Lente | Pergunta típica |
|---|---|
| Premissa não declarada | "Isso só funciona se <crença> for verdade. De onde veio essa crença?" |
| Falseamento | "O que você veria que te faria abandonar isso?" |
| Custo do erro | "Se estiver errado, quanto custa e dá pra desfazer?" |
| Restrição real | "O prazo é imposição de alguém ou preferência sua?" |
| Já fechado vs aberto | "O que aqui já está decidido e não é pra reabrir?" |
| Alternativa descartada | "O que você já considerou e descartou — e por quê?" |
| Critério de sucesso | "Daqui a 30 dias, o que você observa que diz que deu certo?" |
| Escala | "Isso é uma vez ou vira rotina?" (muda se vale automatizar) |
| Quem mais decide | "Alguém pode vetar isso depois de pronto?" |

**Não pergunte o que você pode descobrir sozinho.** Se a resposta está no repo,
no git log, no CLAUDE.md ou numa busca, vá ver — perguntar o verificável gasta a
paciência que você vai precisar nas perguntas que só ele pode responder.
Verifique **entre os turnos, em silêncio**: "não resolver durante a entrevista"
vale para propor a solução, não para consultar fato. Só conte o que achou se
isso muda a pergunta que você ia fazer — narrar a investigação rouba a atenção
que era da pergunta.

**Resposta vaga:** insista **uma** vez, pedindo o concreto (um número, um
exemplo, uma data, um nome). Se continuar vaga, registre como "em aberto" e siga.
Insistir três vezes vira desgaste e a pessoa desengaja.

**Se ele perguntar "e você, o que acha?":** diga em uma linha **de que depende
a escolha**, não qual lado tomar, e volte pra pergunta. A fronteira é essa:
descrever o trade-off mantém ele pensando; escolher por ele encerra o
pensamento. A recomendação, se ele quiser, é do fechamento.

**Tom:** pergunta em 1–2 linhas, sem preâmbulo, sem elogiar a resposta anterior.
Contexto só quando a pergunta não se sustenta sozinha. **Durante a entrevista
este formato vence o padrão de resposta do repo/frota** (Objetivo → O que foi
feito → Dependências, teto de 200 palavras) — aquele volta a valer no
fechamento, que é onde ele encaixa.

## Quando parar

Pare quando o que sobrou de desconhecido **não muda mais a ação** — esse é o
critério, não um número de perguntas. Na prática dá entre 5 e 12. Pare também
quando ele disser "chega".

Dois sinais que valem dizer em voz alta na hora que aparecerem:

- **o alvo mudou no meio** ("estamos decidindo outra coisa agora: …") — é comum
  e é o resultado mais valioso da entrevista;
- **passou de ~12 perguntas sem fechar** — o alvo provavelmente é grande demais;
  proponha fatiar em duas decisões e grelhar a primeira.

## Fechamento (formato fixo)

Feche sempre, mesmo em entrevista curta — sem recap, a clareza evapora junto com
a conversa. Use esta estrutura:

```
**Decisão:** <1 linha>
**Fechado:** <o que ficou definido — bullets curtos>
**Premissas:** <o que você assumiu e ele não confirmou>
**Em aberto:** <o que falta e de quem/de que depende>
**Próximo passo:** <1 linha acionável>
```

Separe o que **ele disse** do que **você inferiu** — atribuir a ele uma posição
que ele não tomou é a forma mais fácil de o recap sair errado e ninguém notar.
Vá anotando o que fecha ao longo da entrevista; o fechamento é registro, não
reconstrução de memória.

Se o tema for da frota de scanners, o fechamento reporta trade-offs, margens e
fontes — nunca recomenda compra (invariante da frota; a decisão de capital é do
operador).

## Depois do fechamento

Ofereça o próximo passo em **uma linha**, só se couber: virar prompt
(`prompt-master-tcg`), virar doc (`doc-coauthoring`), ou executar agora. Não
emende a execução por conta própria — quem pediu para ser grelhado pediu clareza
primeiro.

## Anti-padrões

- Despejar 5 perguntas numeradas de uma vez.
- Perguntar o que já está escrito no repo.
- Perguntar o que não muda nada ("qual o nome do arquivo?").
- Virar coach: "e como você se sente sobre isso?" — a entrevista é sobre a
  decisão, não sobre a pessoa.
- Começar a resolver no meio da entrevista.
- Terminar sem recap.
