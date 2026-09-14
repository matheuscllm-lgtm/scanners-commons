# 08 — Estilo de resposta (o "prompt master" da conversa)

> **Decisão do operador (2026-09-14):** as respostas estavam **longas demais**.
> A partir de agora toda resposta de chat é **concisa, teto de 200 palavras**, na
> estrutura fixa **Objetivo → O que foi feito → Dependências/pendências**.

Este documento é a **cópia-mestra** da regra. O bloco replicado no topo do
`CLAUDE.md` de cada repo da frota é um resumo dela — **edite aqui primeiro** e
depois replique (ver "Como sincronizar").

---

## A regra

**1) Objetivo** — uma linha: o que foi pedido, como você entendeu.
**2) O que foi feito** — bullets curtos; **cada bullet diz o *porquê*** da decisão
(o operador é médico, não programador: a decisão sem o motivo não é auditável).
**3) Dependências/pendências** — o que falta, o que está bloqueado, de quem
depende (chave, PC do operador, merge, decisão de capital). `nenhuma` quando
não houver — silêncio não é "está tudo certo".

**Teto: 200 palavras de PROSA.**

### O que NÃO conta no teto (e nunca pode ser cortado pra caber)

| Fora do teto | Por quê |
|---|---|
| Tabela de entrega gerada pela ferramenta do repo (`myp_summary.py`, `comc_summary.py`, `cardtrader_postprocess.py`, `scripts/snapshot.py`, `build_markdown`, `ebay_summary.py`…) | A entrega é **VERBATIM** e mostra **TODAS** as linhas (regra de ouro nº 4 e nº 6 do [README](README.md)). Resumir a tabela pra caber num limite de prosa seria violar o invariante — o limite é sobre a *conversa*, não sobre o *resultado* |
| Blocos de comando/código | O operador copia e cola; encurtar comando gera erro de execução |
| Saída de teste colada como prova (`pytest -q`) | É evidência, não narração |
| Artefato canônico de um repo (Executive Brief do `oncology`, relatório de análise, handoff) | Tem formato próprio, definido no `CLAUDE.md` daquele repo |

### O que o teto mata de propósito

Preâmbulo ("Ótima pergunta!", "Vou verificar…"), repetição do pedido,
recapitulação do que já foi dito na conversa, lista de alternativas que não serão
seguidas, narração passo a passo de cada ferramenta usada, e o resumo final que
repete os bullets em prosa.

### Quando a resposta honesta não cabe

Entregue o **essencial dentro do teto** e ofereça o detalhe:
*"Quer o detalhe do join por productId?"* — **nunca** estoure o teto em silêncio,
e **nunca** omita uma pendência/risco pra economizar palavra (honestidade vence
concisão: se a escolha é entre estourar e esconder um risco, **estoure e avise**).

---

## Exemplos práticos (antes × depois)

### Exemplo 1 — scan do MYP

**❌ Antes (~320 palavras):** "Ótima pergunta! Deixa eu explicar o que fiz. Primeiro
eu li o CLAUDE.md do repo pra entender as convenções, depois verifiquei que o
threshold do MYP é percentual inteiro, diferente do CardTrader que é fração, então
rodei o scanner com `--threshold 30`… [8 parágrafos] … Em resumo, rodei o grupo 1 e
achei 12 deals."

**✅ Depois (58 palavras + tabela):**

> **Objetivo:** rodar o grupo 1 do MYP e entregar os deals.
>
> **Feito:**
> - Grupo 1 (11 edições) com `--threshold 30 --min-price 50` — inteiro porque no MYP a convenção é percentual, não fração.
> - Entrega abaixo gerada pelo `myp_summary.py` (nunca à mão) — 12 limpos, 3 em validar-manual.
>
> **Pendências:** 2 edições caíram em fallback `.estat-tcg` (tcgcsv sem groupId) — margem dessas 2 não é confiável.
>
> *[tabela do `myp_summary.py` colada verbatim — fora do teto]*

### Exemplo 2 — correção de código

**✅ (41 palavras):**

> **Objetivo:** corrigir o join que precificava a carta errada no e-Card.
>
> **Feito:**
> - `tcgcsv_collector_key` virou variant-aware — o join digits-only colidia série H com sufixo a/b e casava produto errado.
> - `pytest -q`: 281 passed.
>
> **Pendências:** nenhuma. PR draft #62 aberto.

### Exemplo 3 — pergunta factual

Pergunta simples = resposta simples. A estrutura de 3 partes **não é obrigatória
quando não houve trabalho**: *"O threshold do CardTrader é fração: `0.30` = 30%.
Passar `30` vira 2.500% e o scan volta vazio sem erro."* (25 palavras) já é a
resposta completa — não invente seções vazias pra cumprir formato.

---

## Como sincronizar

O bloco curto vive no **topo do `CLAUDE.md` de todos os repos** da frota,
marcado com `<!-- FLEET:ESTILO-RESPOSTA v1 ... -->` (o marcador é o que permite
achar e atualizar as 16 cópias de uma vez):

```bash
grep -rl 'FLEET:ESTILO-RESPOSTA' ~/*/CLAUDE.md      # onde o bloco já está
```

Mudou a regra? Edite **este arquivo**, bump a versão do marcador
(`v1` → `v2`) e replique o bloco nos repos por PR. Mesma disciplina do
`tooling/auto.md` ([`06-AUTO-SKILL.md`](06-AUTO-SKILL.md)): fonte única aqui,
cópias derivadas lá.

> **Onde isto NÃO alcança:** o campo de **preferências pessoais do claude.ai**
> (que vale em chat + Cowork + Claude Code, inclusive fora dos repos) não é
> versionável — o operador cola a regra lá à mão. O `~/.claude/CLAUDE.md` do PC
> também é fora-do-repo: vale só naquela máquina, e em sessão de nuvem (container
> efêmero) não existe. Por isso a cópia no `CLAUDE.md` de cada repo é a que
> garante a regra em **qualquer** sessão.
