# Radar·TCG — painel visual dos scanners (MYP + CardTrader)

Interface interativa (um único arquivo HTML, sem dependência externa) que
transforma os scanners de arbitragem em uma ferramenta visual:

1. **Montar scan** — escolhe os sets pelos **6 grupos canônicos** de cada
   scanner (verbatim das skills `scan-myp` e `/scan`), ajusta margem bruta
   mínima (default 30%), piso de preço e demais parâmetros, e gera o
   **comando exato** para copiar e rodar — convertendo sozinho a convenção de
   threshold (inteiro no MYP, **fração** no CardTrader, a pegadinha nº 1).
2. **Explorar resultados** — importa o resultado de um scan já rodado
   (CSV exportado do XLSX, ou JSON), aplica **filtros dinâmicos** (set, tipo
   de carta, raridade, arte especial IR/SIR/SAR, faixa de preço, margem,
   fonte real × fallback, status ok/validar/reprovada, piso extra **por
   carta**) e exporta o recorte em CSV / JSON / tabela Markdown no formato
   padrão da frota.

## Como usar

- **No Claude:** peça para publicar `tooling/radar-tcg/index.html` como
  Artifact (ferramenta `Artifact`) — vira uma página interativa no claude.ai.
- **No PC:** abrir o `index.html` direto no navegador (duplo clique) — funciona
  offline, nada é enviado a lugar nenhum.

## Invariantes respeitados (não quebrar ao editar)

- Margem **bruta** sem taxa embutida; piso R$50 (~US$10) só para singles.
- NM-only e EN-only são invariantes de coleta — o painel apenas exibe.
- **Nunca inventa preço nem URL**: linha sem link fica `—`; fonte fallback é
  rotulada e cai em “validar”. O modo demonstração é explicitamente marcado
  como **dados fictícios**.
- O painel **não recomenda compra** — reporta margem, flags e fontes; a
  decisão de capital é do operador.
- A entrega oficial de um scan continua sendo a tabela gerada pela ferramenta
  de cada repo (`myp_summary.py` / `cardtrader_postprocess.py`); este painel é
  uma camada de exploração por cima do mesmo XLSX, não substitui o contrato.
