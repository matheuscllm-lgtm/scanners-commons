# 06 — O comando `/auto` (modo autônomo da frota)

> Pra você, Matheus: este arquivo explica o que é o `/auto`, onde ele mora, e
> como manter as cópias iguais nos scanners — em linguagem simples.

## O que é

`/auto` é o **agente master de produtos de arbitragem** em modo autônomo. Quando
você digita `/auto` (com ou sem instrução depois) numa sessão do Claude Code
dentro de um scanner, o assistente passa a agir como **dono do produto + tech
lead**: não só **resolve a tarefa do começo ao fim sozinho** (corrige, testa,
valida preço em várias fontes, salva, abre PR e — quando trivialmente seguro —
mergeia), como também **aprimora a ferramenta** no caminho (fecha ponto cego,
endurece teste frágil, tira fallback que mente). Ele trabalha **em paralelo**:
quebra a tarefa em frentes e dispara vários sub-assistentes/ferramentas de uma
vez, em vez de marchar em série. **Sem pedir permissão a cada passo** — só
**para e pergunta** em 4 situações de risco alto: perder dados, mexer em
senha/chave, gasto que pesa no bolso, ou algo irreversível em produção.

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
- **Orquestração (multi-tarefa/multi-agente)**: decompõe a tarefa em frentes
  independentes e **paraleliza** — varredura de código com `Explore`, trabalho
  pesado com vários `Agent` (ou o lead agent do repo, tipo `card-agent`),
  varredura grande com `Workflow`. Tem uma **caixa de ferramentas** que mapeia
  "preciso de X → uso a ferramenta Y" (GitHub, Firecrawl pra scrape de preço,
  Excel pra XLSX, skills `deep-research`/`code-review`/`verify`). Se a ferramenta
  não existe naquele ambiente (a nuvem clona só o repo), **degrada com elegância**
  em vez de travar.
- **Verificação multi-agente**: pra decisões ambíguas, dispara vários
  sub-assistentes em paralelo com olhares diferentes (correção, honestidade de
  preço, regressão) e exige maioria — assim resolve sozinho com segurança em vez
  de te interromper.
- **Aprimora, não só conserta**: ao tocar uma área, deixa melhor (ponto cego,
  teste, fallback honesto). E **quando você não dá tarefa**, escolhe sozinho o
  item de maior valor e menor risco do backlog (bug/honestidade primeiro).
- **PR sem duplicar**: confere se já existe PR pra branch antes de criar.
- **Quick-ref da frota (§Q)**: uma tabela única com, por scanner, o comando de
  teste real, a direção do threshold (fração vs inteiro) e se tem lead agent —
  acelera o pré-voo (o `CLAUDE.md` do repo ainda manda se divergir).
- **Playbook de fan-out (§4)**: exemplos prontos de "tarefa → plano de agentes"
  (bug de preço → 3 lentes; set sem cobertura → Explore + 2 fontes; drift →
  Workflow; auditoria → silent-failure-hunter).
- **Checklist Definition-of-Done (§5e)**: lista que o assistente marca antes de
  dizer "pronto" (teste colado? CI verde? preço 2 fontes? segredo varrido?
  coleta não-vazia? run longo seguro? custo na escada?).
- **Execução segura de runs longos (§4b)**: scan que demora horas nunca roda
  "preso" na sessão (morre junto) — é lançado **solto no sistema** com log em
  arquivo; antes de lançar confere se **já não tem outro scan rodando**; se o
  processo morrer, diagnostica antes de tentar de novo (1 retry retomando o
  checkpoint), e se morrer de novo divide em **lotes menores** em vez de
  insistir. Entrega sempre declara o que cobriu e o que faltou.
- **Espera de CI sem estourar o GitHub (§4b)**: nada de vigiar o CI a cada 3
  segundos (isso esgota a cota da API do GitHub em ~25 min) — consulta espaçada
  (1 a 15 min) com limite de espera; e enquanto espera, adianta outra tarefa.
- **Gate "verde-mas-vazio" (§5a)**: scan que termina "com sucesso" mas coletou
  **0 produtos** não vira "0 deals hoje" — é sintoma (headless sem janela, BOM
  no segredo, Cloudflare, API fora) e exige diagnóstico antes de qualquer
  entrega.
- **Escada de custo (§3)**: primeiro cache e rotas grátis; recurso pago só em
  amostra pequena proporcional ao valor; volume pago é freio duro — entrega o
  que a amostra cobre e deixa a pergunta de autorização registrada, sem travar
  o resto.
- **Escada de desbloqueio (§4b)**: travou? 1 retry → rota alternativa → 1
  contorno barato → registra a pendência com prova e segue com o resto. Nunca
  fica repetindo o mesmo comando, e nunca te acorda por bloqueio que não seja
  um dos 4 freios.
- **Regras que viajam pra nuvem**: tudo acima está **dentro do contrato** de
  propósito — na nuvem a memória do seu PC e o CLAUDE.md global não existem, e
  antes essas lições de segurança só moravam lá.

*Versão da fonte-mestra: 2026-07-03 (v3.2 — execução segura: runs longos,
rate-limit de CI, verde-mas-vazio, escadas de custo/desbloqueio, entrega
verbatim 2-links no contrato).*
