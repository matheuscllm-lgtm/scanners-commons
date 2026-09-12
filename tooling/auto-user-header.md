
> **Cópia de USUÁRIO** (`~/.claude/commands/auto.md`): existe para o `/auto`
> funcionar em **qualquer diretório**, não só dentro dos repos da frota.
> Duas deferências, nesta ordem:
>
> 1. **O repo vence.** Se o diretório atual for um repo com o próprio
>    `.claude/commands/auto.md`, leia-o e siga **aquele** — repos divergem de
>    propósito (o `ebay-arbitrage-scanner` tem regras econômicas próprias, e o
>    `CLAUDE.md` dele diz explicitamente que comando histórico não as substitui).
> 2. **Fora de um repo da frota, o pré-voo do §0 não acha `CLAUDE.md` nenhum** —
>    ou seja, o modo autônomo rodaria sem os invariantes carregados, que é
>    exatamente onde ele é perigoso. Nesse caso **pergunte em qual repo é a
>    tarefa** antes de agir, e só então siga o contrato.
