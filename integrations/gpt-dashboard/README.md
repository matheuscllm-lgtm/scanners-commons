# 🔌 Canal de integração com o GPT — dashboard integrativo da frota

**O que é isto, em uma frase:** o **ponto de encontro versionado** entre a frota de
scanners (mantida por sessões Claude Code) e o **GPT**, que está construindo um
**dashboard integrativo** por cima dos nossos scanners e ferramentas.

O problema que resolve: hoje o GPT não tem como saber *o que* cada scanner produz,
*com que formato*, *com que convenção de threshold* e *quais invariantes não pode
violar* — e nós não temos onde registrar o que ele pediu/decidiu. Sem um lugar
único, cada lado inventa contrato por conta (e a frota já pagou caro por
número/alias inventado — ver `01-ERROS-COMUNS.md`).

## Como o canal funciona (protocolo)

Três peças, nesta ordem de importância:

| Arquivo | Papel | Quem escreve |
|---|---|---|
| **`CONTRATO-DE-DADOS.md`** | a verdade sobre o que cada ferramenta produz (arquivo, formato, campos, convenções) e os **invariantes que o dashboard NÃO pode violar** | **frota** (Claude/operador) |
| **`schemas/`** + **`exemplos/`** | o contrato em forma de máquina: JSON Schema do feed + payload de exemplo (dados fictícios) | **frota** |
| **`mensagens/`** | a conversa assíncrona: pedidos do GPT, respostas da frota, decisões com data | **os dois lados** |

Complementos: **`STATUS.md`** (estado vivo da integração — o que já existe, o que
falta, o que está bloqueado) e **`PACOTE-CONTEXTO-GPT.md`** (arquivo único,
autocontido, para **colar no GPT** — ver "Como o GPT lê isto" abaixo).

### O ciclo, na prática

1. **GPT pede** algo (um campo novo, um endpoint, um formato) → vira um arquivo em
   `mensagens/` no padrão `AAAA-MM-DD-gpt-para-frota-<assunto>.md`
   (template em `mensagens/TEMPLATE.md`).
2. **Frota responde** com um arquivo `AAAA-MM-DD-frota-para-gpt-<assunto>.md`:
   ou entrega (com o campo real, do código), ou explica por que não dá.
3. Mudança **aceita** → o `CONTRATO-DE-DADOS.md` e o schema são atualizados **no
   mesmo PR** que muda o código do scanner. Contrato desatualizado é bug.
4. **`STATUS.md`** é atualizado no fim de cada rodada.

Regra de ouro do canal: **mensagem é conversa, contrato é lei.** Nada vira
comportamento do dashboard só porque foi dito numa mensagem — só depois de entrar
no `CONTRATO-DE-DADOS.md` + schema.

## Como o GPT lê isto (o repo é PRIVADO)

`scanners-commons` é privado de propósito (é o manual da frota). Três rotas, da
mais simples à mais automática:

1. **Colar o pacote** (recomendado, funciona hoje, custo zero): o operador abre
   `PACOTE-CONTEXTO-GPT.md` — arquivo **autocontido**, pensado para caber num
   prompt — e cola na conversa com o GPT. É a rota default.
2. **Anexar os arquivos**: subir `CONTRATO-DE-DADOS.md` + `schemas/*.json` +
   `exemplos/*.json` como arquivos de contexto/knowledge do GPT.
3. **Acesso ao repo** (só se o operador quiser): dar leitura ao GPT via conector
   de GitHub. ⚠️ Este repo fala *sobre* chaves (`03-CHAVES-API.md`) mas **nunca**
   contém valor de chave — e essa regra continua valendo, com ou sem GPT lendo.

⚠️ **O que NUNCA entra neste canal:** valor de chave/segredo, e **dados de scan
reais** (margens, preços, cartas de uma run). Os exemplos aqui são **fictícios**,
de propósito — o invariante da frota é que dado de deal não entra em repo
(ver `05-MODELO-ENTREGA.md`). Se o dashboard precisar de dados reais, ele os lê do
artefato local da run, não daqui.

## Alternativa: GitHub Issues como caixa de entrada

Se o operador preferir conversa em vez de arquivo, o mesmo protocolo roda em
**issues deste repo** com o label `gpt-dashboard` — o template de mensagem é o
mesmo. A vantagem do arquivo é ficar versionado junto do contrato; a da issue é
notificar. Os dois são aceitos; o que **não** é aceito é decisão que só existe no
chat e nunca chega ao `CONTRATO-DE-DADOS.md`.

## Validador (para os dois lados usarem)

```bash
python integrations/gpt-dashboard/validate_feed.py <feed.json>   # valida um feed real
python -m pytest integrations/gpt-dashboard -q                   # 100% offline
```

`validate_feed.py` é stdlib pura (sem dependência) e checa o envelope, os campos
de cada deal **e os invariantes da frota** (margem na base compra, os 2 links por
linha, preço nunca inventado). O GPT pode rodar o mesmo script no que o dashboard
consome — se passar aqui, o formato está certo.
