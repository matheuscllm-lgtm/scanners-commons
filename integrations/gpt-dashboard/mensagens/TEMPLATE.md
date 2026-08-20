# [MODELO] AAAA-MM-DD — <gpt-para-frota | frota-para-gpt> — <assunto curto>

> Copie este arquivo com o nome no padrão
> `AAAA-MM-DD-gpt-para-frota-<assunto>.md` (pedido do GPT) ou
> `AAAA-MM-DD-frota-para-gpt-<assunto>.md` (resposta/aviso da frota).
> Uma mensagem = um assunto. Decisão só vale depois de entrar no
> `CONTRATO-DE-DADOS.md` (mensagem é conversa, contrato é lei).

**De:** GPT (dashboard) | Frota (Claude/operador)
**Para:** Frota | GPT
**Assunto:**
**Referências:** (seção do contrato, arquivo de schema, PR, mensagem anterior)

## O que preciso / o que mudou

(Em 1-3 parágrafos. Se é pedido de campo/endpoint novo: **para qual tela do
dashboard**, e **o que ele faria com o dado** — o "porquê" decide se o campo
certo é outro que já existe.)

## Proposta concreta

(Campo/formato/endpoint proposto. Exemplo de payload se ajudar. Dados de
exemplo SEMPRE fictícios — nunca dados de scan reais, nunca segredo.)

## Impacto nos invariantes

(Diga explicitamente: isto toca margem/threshold/links/fallback/recomendação
de compra? Se tocar, qual invariante do §1 do contrato e por quê está ok.)

## Resposta da frota (preencher na resposta)

- [ ] Aceito → PR: `<link>` (contrato + schema atualizados no mesmo PR)
- [ ] Aceito com mudanças → o quê:
- [ ] Recusado → por quê:

**Decisão registrada em:** (data + onde no contrato)
