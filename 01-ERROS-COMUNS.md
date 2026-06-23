# 01 — Principais erros que se repetem nos scanners

Ordenados pelos que mais aparecem / mais doem. Cada um tem: **o que é**, **como percebe**, **como evita**.

---

## 🔴 1. BOM/caractere invisível numa chave de API → scan "verde mas vazio"
- **O que é:** ao colar uma chave que veio de um arquivo salvo como "UTF-8 com BOM", entra um caractere invisível (`U+FEFF`) no começo. Ele não aparece na tela, mas quebra o envio da chave como cabeçalho HTTP: `UnicodeEncodeError: 'latin-1' codec can't encode character`.
- **Como percebe:** o workflow "passa" (fica verde) mas **não precifica nada** — entrega vazia, sem erro óbvio. Foi o que travou o **CardTrader** em 2026-06-22.
- **Como evita (faça os DOIS):**
  1. Setar o secret sem BOM: `printf '%s' 'A_CHAVE' | gh secret set NOME --repo OWNER/REPO`. Confira: `printf '%s' 'A_CHAVE' | wc -c` deve dar o tamanho exato (a Pokémon key = 36).
  2. Limpar no código ao ler: função `_clean_secret()` que tira BOM + zero-width + espaços. **Já existe** em CT e MYP. ⚠️ `.strip()` sozinho **NÃO** tira BOM.

## 🔴 2. Galho (branch) velho parecendo "trabalho pendente"
- **O que é:** os repos usam "squash-merge" (junta vários commits num só ao fechar um PR). Isso deixa o galho local parecendo "à frente" do main, e o `main` local "atrasado" — mesmo o conteúdo já estando todo no main.
- **Como percebe:** você abre o repo e ele está num galho estranho (`feat/...`, `chore/...`), não no `main`. Bateu em **Liga, COMC e eBay** ao mesmo tempo na auditoria — parecia haver 3 pendências, não havia nenhuma.
- **Como evita:** o teste de verdade pra saber se um galho já foi mergeado é `git diff --stat origin/main <galho>` estar **vazio** (NÃO `git merge-base`, que sempre falha em squash). Depois de cada PR: `git checkout main && git pull --ff-only` e apague o galho mergeado.

## 🟠 3. Cobrança do GitHub bloqueando os Actions ("falha" fantasma)
- **O que é:** quando a conta tem pendência de pagamento/limite, os Actions nem iniciam e aparecem como "failure" — mas **não é erro de código**. Mensagem: *"The job was not started because recent account payments have failed…"*.
- **Como evita:** **repositório público tem Actions grátis.** Todos os 6 já são públicos (2026-06-19), então isso não deve mais ocorrer. Se um PR aparecer "vermelho", confira se a falha é essa mensagem de billing antes de mexer no código.

## 🟠 4. Entrega vazia mesmo tendo precificado (handoff scanner → relatório)
- **O que é:** o scanner precificava as cartas mas **jogava fora as abaixo do limiar antes de montar o relatório** → o relatório lia uma planilha vazia → "_nada a entregar_". Era o caso do **CardTrader** (corrigido na v2.22).
- **Como evita:** guardar TODAS as cartas precificadas (com flag "abaixo do limiar"); o limiar vira só uma classificação no fim. Quando ninguém bate 30%, mostrar os "quase-lá" (near-miss) com aviso honesto. Há teste travando esse contrato (um rename de coluna agora quebra um teste em vez de entregar vazio).

## 🟠 5. Preço de referência inflado → falso positivo de "deal"
Aparece de jeitos diferentes em cada scanner; é a causa nº1 de "oportunidade" que não existe:
- **MYP:** o "preço TCG" do próprio site MYP infla 10×–130× (ex.: Jirachi R$1499 vs R$132 real). **Guarda:** sanity-check via `.estatistica-ultimo`; flag `tcg_suspect`.
- **CardTrader:** (a) usar preço *per-expansion* cru em vez de *per-blueprint* dá **76% de falso positivo** → guarda = `validate_per_blueprint`. (b) Variante errada (reverse holo lida como holo) inflava (Gengar US$146 vs US$1599) → guarda `_rarity_is_holo`. (c) Trainer Gallery / Galarian Gallery (`TG##`/`GG##`) inflam 5–10× → filtro por regex.
- **COMC:** resolução de set por "substring solto" casava set errado → guarda = match por palavra inteira + gap-gate de Tier 2.
- **Regra geral:** todo preço de referência precisa de validação/sanity antes de virar deal. Casar **condição NM** e **versão/variante exata** da carta.

## 🟡 6. Tratar fallback como se fosse preço real (no "balde limpo")
- **O que é:** quando o preço veio do plano B (fallback), ele NÃO pode entrar no balde de deals "limpos/confiáveis" como se fosse real. Bug clássico do MYP (#55/#58): o 1º review olhou só a linha mudada e perdeu o fallback vazando pro balde limpo.
- **Como evita:** o "portão de honestidade" (`_is_real`) separa real de fallback; deals com preço de fallback saem do balde limpo. **Lição de review:** revisar o SISTEMA inteiro (todos os baldes que chegam a você), não só o diff.

## 🟡 7. Quebra de "só NM" por match de substring
- **O que é:** filtrar condição com "contém NM" em vez de "== NM" deixa passar SP, NM-/etc.
- **Como evita:** match EXATO `== "NM"`, lendo de célula dedicada de condição. Invariante dura em todos os scanners de singles.

## 🟡 8. pokemontcg.io bloqueado nos servidores da nuvem
- **O que é:** o `api.pokemontcg.io` é bloqueado em IPs de datacenter (onde o GitHub Actions roda) → 404/timeout em massa.
- **Como evita:** na nuvem, usar **tcgcsv.com** como fonte de preço real (MYP já faz via `--tcg-source tcgcsv`; COMC nasceu assim). pokemontcg.io fica pra rodar no PC local.

## 🟡 9. Confusão de unidade do threshold (fração × percentual)
- Ver o aviso no [`README.md`](README.md): **inteiro** (`30`) = MYP, Liga, eBay; **fração** (`0.30`) = CardTrader, COMC, Selados. Errar isso dá "0 deals" ou "tudo é deal".

## 🟢 10. Documentação desatualizada (contagem de testes etc.)
- **O que é:** o `CLAUDE.md` de cada repo às vezes diz "36 testes" quando já são 50. Confunde quem retoma ("será que faltam testes?").
- **Como evita:** ao mexer nos testes, atualizar a contagem no `CLAUDE.md` no mesmo PR. (MYP 36→50, eBay 57→65 corrigidos em 2026-06-22.)

## 🟢 11. Rodar dois scans na mesma pasta de estado (CardTrader)
- **O que é:** o CT tem um "run-guard" que **recusa** iniciar se já houver outra instância usando o mesmo `--state-dir`.
- **Como evita:** use `--state-dir` diferente por run, ou `--allow-concurrent`. Scans longos: rodar em segundo plano (detached), nunca preso numa janela.

---

### Padrão por trás de quase tudo acima
Três famílias de erro respondem pela maioria:
1. **Higiene de segredo/ambiente** (BOM, billing, key não usada) → "verde mas vazio".
2. **Higiene de git** (galho/main defasado) → falsa sensação de pendência.
3. **Honestidade de preço** (inflação, fallback-como-real, NM frouxo) → deal falso.

Se um scan novo der resultado estranho, suspeite primeiro destas três.
