---
name: auto-cowork
description: >-
  Modo AUTÔNOMO da frota de scanners de arbitragem (o `/auto` do terminal):
  resolve a tarefa ponta a ponta — corrige, aprimora, testa, commita, abre PR —
  sem pedir confirmação, parando só em quatro freios de risco alto. Use SOMENTE
  quando o operador escrever `/auto` ou pedir explicitamente "modo autônomo",
  "resolve sozinho", "toca isso ponta a ponta sem me perguntar". NÃO acione por
  conta própria: uma tarefa de código comum, um scan, um ranking ou uma pergunta
  sobre os repos NÃO são convite para modo autônomo — autonomia que ninguém
  pediu é exatamente o risco que este contrato existe para controlar.
---

# `/auto` no Cowork — modo autônomo da frota

O contrato canônico deste modo tem ~370 linhas e vive em **`tooling/auto.md` do
repo `matheuscllm-lgtm/scanners-commons`** (privado). Ele é a fonte única: o
terminal distribui cópias dele para os repos da frota pelo
`tooling/sync-auto-skill.sh`. Esta skill existe porque o Cowork trabalha com
skills, não com comandos de barra, e porque parte do contrato pressupõe terminal.

## Primeiro passo: buscar o contrato

Leia `tooling/auto.md` do `scanners-commons` e **siga-o como contrato**. Ele traz
o pré-voo obrigatório, o mandato de corrigir + aprimorar, a orquestração
paralela, a verificação multi-camada e o encerramento.

**Precedência:** onde esta página e o contrato completo divergirem, **esta página
vence** — em especial a seção "O que muda no Cowork" (sem alvo: perguntar, nunca
puxar backlog; sem `$ARGUMENTS`; GitHub via `mcp__github__*`). Instruções do
contrato que pressupõem terminal (`AskUserQuestion`, `Start-Process`, `gh run
watch`, `/compact`) não existem aqui: pergunte em texto, rode processos longos
em primeiro plano com timeout, acompanhe CI pelas ferramentas `mcp__github__*`.

Se o repo não estiver acessível nesta sessão, **você ainda pode operar** — mas só
dentro dos limites desta página, e diga ao operador que está rodando com o
contrato reduzido. O que não depende de buscar nada está logo abaixo, de
propósito: rail de segurança nunca pode depender de uma leitura que falha.

## Os quatro freios (pare e pergunte SOMENTE nestes)

Fora destes quatro, não pare — resolva. Esta é a parte do contrato que não se
negocia, porque cada um é irreversível:

- **Perda de dados** — apagar ou sobrescrever arquivo que você não criou,
  `git reset --hard`, `push --force`, deletar branch ou repo, `rm` largo.
- **Segredo/credencial** — expor, commitar, logar ou rotacionar uma chave.
- **Custo relevante** — recurso pago em volume (créditos Firecrawl, Amazon
  PA-API, quota de Actions, dezenas de agentes). Suba a escada antes: (1) cache
  só da coleta em andamento e metadados estáveis, nunca preço de outro scan →
  (2) rotas grátis (pokemontcg.io, tcgcsv, API MYP, PriceCharting público,
  curl_cffi) → (3) pago em amostra pequena e proporcional ao valor → (4) volume
  pago = este freio. Entregue o que a amostra cobre, rotule o resto como
  não-validado e registre a pergunta de autorização no resumo.
- **Irreversível de produção** — release público, merge que apaga trabalho,
  mudança difícil de desfazer no comportamento de produção.

## Invariantes que o modo autônomo nunca quebra

Valem mesmo com o contrato completo em mãos, e valem mais ainda sem ele. Esta
lista é uma cópia manual do §9 do contrato: ao editar o §9, edite aqui também.

- **O `CLAUDE.md` do repo manda.** Margem **bruta**, mínimo **30%**, sem taxa
  embutida (`(revenda − compra)/compra`; o eBay tem regra própria no `CLAUDE.md`
  dele); threshold (a direção muda por repo: fração em CardTrader/COMC/Selados,
  inteiro em MYP/Liga/eBay); NM-only por match exato; nunca inventar preço —
  fonte que falhou vira fallback rotulado, jamais número fabricado.
- **Entrega = tabela markdown no chat**, gerada pela ferramenta do repo e colada
  verbatim. Nunca remontada à mão, nunca arquivo por padrão, todas as linhas,
  os dois links em toda linha de todo bucket — e as **URLs sempre das colunas
  da fonte, jamais inventadas**.
- **Preço é sempre desta coleta**: cada pedido renova ofertas, referências e
  câmbio; resultado antigo nunca é apresentado como atual.
- **Dados de scan não entram no repo** (`results/`, `outputs/`, planilhas são
  gitignored de propósito). Só código e documentação.
- **Branch designada, nunca push direto na `main`.**
- **Nunca commitar segredo/chave.** Segredo com BOM ou zero-width crasha o
  header (latin-1) e o scan vem "verde mas vazio"; `.strip()` não tira BOM.
- **Capital é do operador.** Você é técnico: código, dados, auditoria. Nunca
  recomenda comprar ou não comprar.

## O que muda no Cowork (e o que isso exige de você)

O contrato foi escrito para o terminal. Três diferenças que mudam a execução:

1. **O repo pode não estar clonado.** Clone antes de agir e diga em qual repo
   está trabalhando. Sem repo, o pré-voo não lê `CLAUDE.md` nenhum — e modo
   autônomo sem os invariantes carregados é precisamente o cenário perigoso.
   Nesse caso, pergunte em qual repo é a tarefa em vez de adivinhar.
2. **Não existe `$ARGUMENTS`.** O objetivo da rodada é o que o operador escreveu
   no pedido. Se ele disse só "/auto" sem alvo, pergunte qual é a tarefa em vez
   de escolher uma do backlog por conta própria: no terminal o backlog do §7 é
   uma saída razoável porque o operador está olhando; aqui ele pode não estar.
3. **`gh` CLI não existe.** Operações de GitHub vão pelas ferramentas
   `mcp__github__*`; `git push` por linha de comando funciona normalmente.

## Encerramento

Termine com um resumo honesto: o que mudou, o que foi verificado com saída real
(teste rodado, CI verde, preço conferido em mais de uma fonte), o que ficou
fora e por quê, e qualquer autorização que você registrou em vez de pedir na
hora. Se algo não foi verificado, diga que não foi — o contrato inteiro depende
de a diferença entre "feito" e "feito e provado" nunca ser borrada.
