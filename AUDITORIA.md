# Auditoria da versão gerada por IA

> ⚠️ **STATUS: PLACEHOLDER.** A versão em `gerada-por-ia/RESPOSTA-ORIGINAL/main.py` foi escrita pela equipe como stand-in para a Etapa 1; não é resposta real de assistente. **Antes de 25/11**: peçam ao ChatGPT/Claude com o prompt em `gerada-por-ia/PROMPT.md`, substituam o arquivo sem editar, rodem os 5 casos e reescrevam esta auditoria com os defeitos reais.

## Defeito 1 — Detecção de ciclo só olha auto-ciclo
**Descrição.** `tem_ciclo` verifica se um código aparece na própria lista de pré-requisitos. Pega A→A, não pega ciclo indireto.
**Entrada que revela.** `dados/caso2_ciclo.json` (CC0106→CC0109→CC0106).
**Saída obtida.** `"ciclo": null` e o programa segue respondendo 2–4. Esperado: `"ciclo": ["CC0106","CC0109","CC0106"]` e as outras três chaves `null`.
**Classificação primária:** Semântica do problema.
**Secundária:** Terminação ou robustez.
**Verificador mais barato:** teste automatizado (diff contra `saidas_esperadas.json`).

## Defeito 2 — Busca da maior grade ignora conflito de horário
**Descrição.** O laço de `combinations` filtra só por soma de CH ≤ teto. Não verifica sobreposição.
**Entrada que revela.** `dados/historico.json` (caso 1, teto 240).
**Saída obtida.** Inclui `["CC0104","CC0110","CC0112","CC0113"]` (240 h), que o enunciado marca explicitamente como inválida. Esperado: 4 grades de 210 h.
**Classificação primária:** Semântica do problema.
**Verificador mais barato:** teste automatizado.

## Defeito 3 — Robustez de entrada e `next()` sem default
**Descrição.** (a) O programa só aceita o formato unificado; o caso 1 vem em três arquivos e quebra. (b) `next(...)` sem default estoura `StopIteration` se a oferta tiver código fora da matriz.
**Classificação primária:** Terminação ou robustez.
**Secundária:** Suposição não declarada.
**Verificador mais barato:** revisão humana.