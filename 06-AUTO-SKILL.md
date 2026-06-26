# 06 — O comando `/auto` (modo autônomo da frota)

> Pra você, Matheus: este arquivo explica o que é o `/auto`, onde ele mora, e
> como manter as cópias iguais nos scanners — em linguagem simples.

## O que é

`/auto` é um **modo de trabalho autônomo**. Quando você digita `/auto` (com ou
sem uma instrução depois) numa sessão do Claude Code dentro de um scanner, o
assistente passa a **resolver a tarefa do começo ao fim sozinho** — corrige,
testa, valida preço em várias fontes, salva (commit), abre o pedido de revisão
(PR) e, quando é trivialmente seguro, junta ao oficial (merge) — **sem ficar
pedindo permissão a cada passo**. Ele só **para e pergunta** em 4 situações de
risco alto: perder dados, mexer em senha/chave, gasto que pesa no bolso, ou algo
irreversível em produção.

## Onde mora (e por que tem 8 cópias)

O `/auto` é um arquivo (`auto.md`) que fica **dentro de cada scanner**, em
`.claude/commands/auto.md`. Tem que ser assim porque, quando o assistente roda
**na nuvem**, ele clona o repositório do GitHub — então o arquivo precisa estar
**dentro** do repo pra viajar junto (uma cópia em `~/.claude/` no seu PC **não**
chega na nuvem). São **8 scanners** com `/auto`: CardTrader, eBay, integrado,
Liga, MYP, longterm-outlook, COMC e Selados. (Oncology não usa — é outro
domínio.)

## A fonte-mestra (pra não derivarem)

Como são 8 cópias, elas **derivam** com o tempo se a gente edita uma a uma (já
aconteceu: o Selados ficou pra trás, sem metade do contrato). Pra resolver:

- A **versão oficial** fica aqui, em `tooling/auto.md`.
- O script `tooling/sync-auto-skill.sh` **copia a oficial pros 8 repos** de uma
  vez. Depois é só commitar/pushar em cada um.

```bash
# ver quais repos estão diferentes (não escreve nada):
bash tooling/sync-auto-skill.sh --check

# aplicar a versão oficial em todos:
bash tooling/sync-auto-skill.sh
```

## O que o `/auto` garante de bom (resumo do contrato)

- **Pré-voo obrigatório**: lê o `CLAUDE.md` do repo, confere a **direção do
  threshold** (fração no CT/COMC/Selados, inteiro no MYP/Liga/eBay), descobre o
  **comando de teste certo** (nem todo scanner usa `pytest`), e checa se a branch
  **já não foi mergeada por squash** (pra não refazer trabalho).
- **Nunca afirma sem prova**: não diz "teste passou" nem "CI verde" sem **colar a
  saída real**. É a mesma regra de "nunca inventar preço".
- **Multi-verificação de preço**: qualquer mudança que mexa em preço/margem é
  cruzada em **pelo menos 2 fontes** (pokemontcg.io, tcgcsv, PriceCharting, APIs
  MYP/CardTrader, e o site de origem). Divergiu → marca como suspeito, não
  escolhe a que confirma o deal.
- **Verificação multi-agente**: pra decisões ambíguas, dispara vários
  sub-assistentes em paralelo com olhares diferentes (correção, honestidade de
  preço, regressão) e exige maioria — assim resolve sozinho com segurança em vez
  de te interromper.
- **PR sem duplicar**: confere se já existe PR pra branch antes de criar.

*Versão da fonte-mestra: 2026-06-25.*
