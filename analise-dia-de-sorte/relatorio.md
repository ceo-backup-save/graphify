# Dia de Sorte — Análise Estatística dos Últimos 100 Concursos

**Concursos 1238 a 1337 · 06/07/2026 a 01/11/2026 · fonte: API oficial Loterias Caixa**

| Item | Valor |
| --- | --- |
| Jogo | Dia de Sorte (31 dezenas, 7 sorteadas) |
| Janela analisada | últimos **100 concursos** (1238–1337) |
| Período | 06/07/2026 a 01/11/2026 |
| Fonte | API oficial Loterias Caixa — servicebus2.caixa.gov.br/portaldeloterias/api/diadesorte |
| Histórico disponível | 1.337 concursos |
| Universo de combinações | 2.629.575 jogos possíveis de 7 dezenas |

> **Observação sobre o arquivo enviado:** nenhum arquivo chegou junto à mensagem (o workspace não contém CSV/Excel/PDF de jogos). A análise foi feita diretamente sobre os resultados oficiais da Caixa — o que é mais confiável do que uma planilha manual. Se o arquivo era uma lista de jogos para conferência, reenvie que eu cruzo com este padrão.

## 1. Resumo executivo — padrão mais prevalente por tópico

| # | Tópico | Padrão mais prevalente | Concursos | % | Esperado por azar | Desvio |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Pares / Ímpares | 4 pares / 3 ímpares | 29 | 29,0% | 29,1% | -0,1 p.p. |
| 2 | Baixas / Altas | 3 baixas / 4 altas | 29 | 29,0% | 31,5% | -2,5 p.p. |
| 3 | Soma | 120–134 | 22 | 22,0% | 21,7% | 0,3 p.p. |
| 4 | Repetidas do concurso anterior | 1 repetida | 38 | 38,0% | 35,8% | 2,2 p.p. |
| 5 | Grupos em sequência | 3 no G1 (01–10) / 2 no G2 (11–20) / 2 no G3 (21–31) | 18 | 18,0% | 11,3% | 6,7 p.p. |
| 6 | Dezenas em sequência | 1 dupla | 44 | 44,0% | 40,4% | 3,6 p.p. |

## 2. Pares / ímpares

Distribuição da quantidade de dezenas **pares** em cada um dos 100 jogos (ímpares = 7 − pares). O universo 01–31 tem 15 pares e 16 ímpares.

| Rank | Padrão | Concursos | % | Esperado (azar) | Desvio |
| --- | --- | --- | --- | --- | --- |
| 1 | 4 pares / 3 ímpares | 29 | 29,0% | 29,1% | -0,1 p.p. |
| 2 | 3 pares / 4 ímpares | 25 | 25,0% | 31,5% | -6,5 p.p. |
| 3 | 5 pares / 2 ímpares | 21 | 21,0% | 13,7% | 7,3 p.p. |
| 4 | 2 pares / 5 ímpares | 17 | 17,0% | 17,4% | -0,4 p.p. |
| 5 | 6 pares / 1 ímpar | 4 | 4,0% | 3,0% | 0,9 p.p. |
| 6 | 1 par / 6 ímpares | 3 | 3,0% | 4,6% | -1,6 p.p. |
| 7 | 0 pares / 7 ímpares | 1 | 1,0% | 0,4% | 0,6 p.p. |
| 8 | 7 pares / 0 ímpares | 0 | 0,0% | 0,2% | -0,2 p.p. |

- **Padrão mais comum: 4 pares / 3 ímpares** — 29 concursos (29,0%).
- Equilíbrio (3 ou 4 pares) responde por **54,0%** dos concursos.
- 5 pares / 2 ímpares foi o 3º mais frequente (21,0%), acima do esperado por azar (13,7%).
- No total saíram 357 dezenas pares e 343 ímpares — praticamente meio a meio.

*Teste qui-quadrado: χ² = 5,24 · gl = 4 · p = 0,263 → sem desvio significativo ao nível de 5% (compatível com aleatoriedade).*

## 3. Baixas / altas

Baixas = 01–15 (15 dezenas); altas = 16–31 (16 dezenas).

| Rank | Padrão | Concursos | % | Esperado (azar) | Desvio |
| --- | --- | --- | --- | --- | --- |
| 1 | 3 baixas / 4 altas | 29 | 29,0% | 31,5% | -2,5 p.p. |
| 2 | 4 baixas / 3 altas | 29 | 29,0% | 29,1% | -0,1 p.p. |
| 3 | 2 baixas / 5 altas | 21 | 21,0% | 17,4% | 3,6 p.p. |
| 4 | 5 baixas / 2 altas | 15 | 15,0% | 13,7% | 1,3 p.p. |
| 5 | 1 baixa / 6 altas | 3 | 3,0% | 4,6% | -1,6 p.p. |
| 6 | 6 baixas / 1 alta | 3 | 3,0% | 3,0% | -0,1 p.p. |
| 7 | 0 baixas / 7 altas | 0 | 0,0% | 0,4% | -0,4 p.p. |
| 8 | 7 baixas / 0 altas | 0 | 0,0% | 0,2% | -0,2 p.p. |

- **Padrão mais comum: 3 baixas / 4 altas e 4 baixas / 3 altas** — empatados com 29 concursos cada (29,0%).
- Equilíbrio (3 a 4 dezenas de cada lado) concentra **58,0%** dos casos.
- Jogos com maioria alta (≤3 baixas) = 53,0%; maioria baixa (≥4 baixas) = 47,0%.
- Extremos (0 ou 7 dezenas de um lado) **não ocorreram** no período.

*Teste qui-quadrado: χ² = 1,68 · gl = 4 · p = 0,794 → sem desvio significativo ao nível de 5% (compatível com aleatoriedade).*

## 4. Soma das 7 dezenas

Mínimo teórico 28 (1+2+…+7), máximo 196 (25+…+31), média teórica 112.

| Rank | Faixa de soma | Concursos | % | Esperado (azar) | Desvio |
| --- | --- | --- | --- | --- | --- |
| 1 | 120–134 | 22 | 22,0% | 21,7% | 0,3 p.p. |
| 2 | 90–104 | 21 | 21,0% | 21,7% | -0,7 p.p. |
| 3 | 105–119 | 19 | 19,0% | 27,1% | -8,1 p.p. |
| 4 | 135–149 | 18 | 18,0% | 10,9% | 7,0 p.p. |
| 5 | 75–89 | 12 | 12,0% | 10,9% | 1,1 p.p. |
| 6 | 60–74 | 5 | 5,0% | 3,3% | 1,7 p.p. |
| 7 | 150–164 | 3 | 3,0% | 3,3% | -0,3 p.p. |
| 8 | 165–179 | 0 | 0,0% | 0,5% | -0,5 p.p. |
| 9 | 180–196 | 0 | 0,0% | <0,1% | 0,0 p.p. |
| 10 | 28–44 | 0 | 0,0% | <0,1% | 0,0 p.p. |
| 11 | 45–59 | 0 | 0,0% | 0,5% | -0,5 p.p. |

| Estatística | Valor |
| --- | --- |
| Média observada | **112,61** |
| Mediana | 115,0 |
| Moda | 108 (apareceu 5x) |
| Desvio-padrão | 22,56 |
| Mínimo / máximo | 62 / 157 |
| P25 – P75 | 97,2 – 130,8 |
| Faixa ±1 desvio-padrão | 90,0 – 135,2 |
| Faixa central de 95% teórica | 71 – 153 (95 dos 100 concursos caíram dentro) |

- **Faixa de soma mais comum: 120–134** com 22 concursos (22,0%).
- 80,0% dos concursos tiveram soma entre **90 e 149**.
- Somam entre 90,0 e 135,2: faixa de 1 desvio-padrão em torno da média.

*Teste qui-quadrado: χ² = 7,11 · gl = 5 · p = 0,212 → sem desvio significativo ao nível de 5% (compatível com aleatoriedade).*

## 5. Repetidas do concurso anterior

Quantas das 7 dezenas sorteadas já haviam saído no concurso imediatamente anterior (base: concursos 1237–1337).

| Rank | Padrão | Concursos | % | Esperado (azar) | Desvio |
| --- | --- | --- | --- | --- | --- |
| 1 | 1 repetida | 38 | 38,0% | 35,8% | 2,2 p.p. |
| 2 | 2 repetidas | 36 | 36,0% | 33,9% | 2,1 p.p. |
| 3 | 3 repetidas | 12 | 12,0% | 14,1% | -2,1 p.p. |
| 4 | nenhuma repetida | 10 | 10,0% | 13,2% | -3,2 p.p. |
| 5 | 4 repetidas | 2 | 2,0% | 2,7% | -0,7 p.p. |
| 6 | 5 repetidas | 2 | 2,0% | 0,2% | 1,8 p.p. |
| 7 | 6 repetidas | 0 | 0,0% | <0,1% | 0,0 p.p. |
| 8 | 7 repetidas | 0 | 0,0% | <0,1% | 0,0 p.p. |

| Estatística | Valor |
| --- | --- |
| Média de repetidas por concurso | **1,64** (esperado por azar: 1,58) |
| Mediana | 2,0 |
| Desvio-padrão | 1,02 |
| Total de dezenas repetidas | 164 |
| Máximo / mínimo | 5 / 0 |

- **Padrão mais comum: 1 repetida** (38 concursos, 38,0%), seguido de perto por 2 repetidas (36,0%).
- **90,0%** dos concursos repetiram ao menos 1 dezena; 74,0% repetiram 1 ou 2.
- Repetir 3 dezenas: 12,0%; 4 repetidas: 2,0%; 5 repetidas: 2,0% (um caso raro: esperado por azar seria 0,2%).
- Jogos sem nenhuma repetida foram minoria (**10%**), e 6 ou 7 repetidas nunca ocorreram.

*Teste qui-quadrado: χ² = 1,74 · gl = 4 · p = 0,784 → sem desvio significativo ao nível de 5% (compatível com aleatoriedade).*

## 6. Grupos em sequência (faixas de dezenas)

Grupos fixos: **G1 = 01–10** (10 dezenas), **G2 = 11–20** (10 dezenas), **G3 = 21–31** (11 dezenas). A tabela mostra como as 7 dezenas se distribuem entre os grupos.

| Rank | Distribuição G1 / G2 / G3 | Concursos | % | Esperado (azar) | Desvio |
| --- | --- | --- | --- | --- | --- |
| 1 | 3 no G1 (01–10) / 2 no G2 (11–20) / 2 no G3 (21–31) | 18 | 18,0% | 11,3% | 6,7 p.p. |
| 2 | 2 no G1 (01–10) / 2 no G2 (11–20) / 3 no G3 (21–31) | 14 | 14,0% | 12,7% | 1,3 p.p. |
| 3 | 1 no G1 (01–10) / 2 no G2 (11–20) / 4 no G3 (21–31) | 9 | 9,0% | 5,7% | 3,4 p.p. |
| 4 | 2 no G1 (01–10) / 1 no G2 (11–20) / 4 no G3 (21–31) | 9 | 9,0% | 5,7% | 3,4 p.p. |
| 5 | 1 no G1 (01–10) / 3 no G2 (11–20) / 3 no G3 (21–31) | 8 | 8,0% | 7,5% | 0,5 p.p. |
| 6 | 2 no G1 (01–10) / 3 no G2 (11–20) / 2 no G3 (21–31) | 5 | 5,0% | 11,3% | -6,3 p.p. |
| 7 | 3 no G1 (01–10) / 1 no G2 (11–20) / 3 no G3 (21–31) | 5 | 5,0% | 7,5% | -2,5 p.p. |
| 8 | 4 no G1 (01–10) / 1 no G2 (11–20) / 2 no G3 (21–31) | 4 | 4,0% | 4,4% | -0,4 p.p. |
| 9 | 4 no G1 (01–10) / 2 no G2 (11–20) / 1 no G3 (21–31) | 4 | 4,0% | 4,0% | 0,1 p.p. |
| 10 | 1 no G1 (01–10) / 4 no G2 (11–20) / 2 no G3 (21–31) | 3 | 3,0% | 4,4% | -1,4 p.p. |
| 11 | 2 no G1 (01–10) / 4 no G2 (11–20) / 1 no G3 (21–31) | 3 | 3,0% | 4,0% | -0,9 p.p. |
| 12 | 0 no G1 (01–10) / 3 no G2 (11–20) / 4 no G3 (21–31) | 2 | 2,0% | 1,5% | 0,5 p.p. |
| 13º+ | outros 11 padrões (agrupados) | 16 | 16,0% | 16,4% | -0,4 p.p. |

- **Padrão mais comum: 3 / 2 / 2** (3 dezenas em 01–10, 2 em 11–20, 2 em 21–31) — 18 concursos (18,0%), contra 11,3% esperados por azar: o desvio mais forte de toda a análise.
- Ocupação dos grupos: 88,0% dos concursos tiveram **os 3 grupos ocupados**.

**Quantas dezenas por grupo (média):**

| Grupo | Média observada | Esperado por azar |
| --- | --- | --- |
| G1 (01–10) | 2,32 | 2,26 |
| G2 (11–20) | 2,04 | 2,26 |
| G3 (21–31) | 2,64 | 2,48 |

**Grupos contíguos ocupados (leitura de sequência de faixas):**

| Rank | Padrão | Concursos | % | Esperado (azar) | Desvio |
| --- | --- | --- | --- | --- | --- |
| 1 | G1+G2+G3 (todos) | 88 | 88,0% | 88,2% | -0,2 p.p. |
| 2 | G1+G3 (sem G2) | 6 | 6,0% | 4,4% | 1,6 p.p. |
| 3 | G1+G2 (sem G3) | 4 | 4,0% | 2,9% | 1,1 p.p. |
| 4 | G2+G3 (sem G1) | 2 | 2,0% | 4,4% | -2,4 p.p. |
| 5 | só G1 | 0 | 0,0% | <0,1% | 0,0 p.p. |
| 6 | só G2 | 0 | 0,0% | <0,1% | 0,0 p.p. |
| 7 | só G3 | 0 | 0,0% | <0,1% | 0,0 p.p. |

*Contiguidade das faixas: χ² = 0,01 · gl = 1 · p = 0,943 → sem desvio significativo ao nível de 5% (compatível com aleatoriedade).*

- Em **88,0%** dos concursos há dezena em todas as faixas; o caso 'pulou um grupo' (G1+G3, sem G2) apareceu em 6,0%.
- Nunca houve concurso concentrado em **um único grupo**.

*Teste qui-quadrado: χ² = 15,24 · gl = 8 · p = 0,055 → sem desvio significativo ao nível de 5% (compatível com aleatoriedade).*

## 7. Dezenas em sequência (dupla / trio / quadra)

Sequência = dezenas consecutivas dentro do mesmo jogo (12-13 = dupla; 05-06-07 = trio; 04-05-06-07 = quadra…).

| Rank | Padrão de sequência no jogo | Concursos | % | Esperado (azar) | Desvio |
| --- | --- | --- | --- | --- | --- |
| 1 | 1 dupla | 44 | 44,0% | 40,4% | 3,6 p.p. |
| 2 | Sem sequência | 24 | 24,0% | 18,3% | 5,7 p.p. |
| 3 | 2 duplas | 12 | 12,0% | 20,2% | -8,2 p.p. |
| 4 | 1 trio | 11 | 11,0% | 10,1% | 0,9 p.p. |
| 5 | 1 trio + 1 dupla | 6 | 6,0% | 5,8% | 0,2 p.p. |
| 6 | 1 quadra | 1 | 1,0% | 1,9% | -0,9 p.p. |
| 7 | 1 trio + 2 duplas | 1 | 1,0% | 0,3% | 0,7 p.p. |
| 8 | 3 duplas | 1 | 1,0% | 1,9% | -0,9 p.p. |

**Maior sequência de cada concurso:**

| Rank | Maior sequência | Concursos | % | Esperado (azar) | Desvio |
| --- | --- | --- | --- | --- | --- |
| 1 | dupla (2 seguidas) | 57 | 57,0% | 62,5% | -5,5 p.p. |
| 2 | sem sequência | 24 | 24,0% | 18,3% | 5,7 p.p. |
| 3 | trio (3 seguidas) | 18 | 18,0% | 16,4% | 1,6 p.p. |
| 4 | quadra (4 seguidas) | 1 | 1,0% | 2,5% | -1,5 p.p. |
| 5 | 7 seguidas | 0 | 0,0% | <0,1% | 0,0 p.p. |
| 6 | quina (5 seguidas) | 0 | 0,0% | 0,3% | -0,3 p.p. |
| 7 | sena (6 seguidas) | 0 | 0,0% | <0,1% | 0,0 p.p. |

- **76,0% dos concursos tiveram pelo menos uma sequência** (76 de 100); o esperado por azar seria 81,7%.
- **Padrão mais comum: exatamente 1 dupla** — 44 concursos (44,0%).
- Duas duplas apareceram 12,0% (abaixo dos 20,2% esperados); trio em 11,0%; trio + dupla em 6,0%.
- Quadra apareceu 1 vez (1%); **quina ou mais: nenhuma vez** no período.
- Média de 0,98 sequência por concurso.

*Teste qui-quadrado: χ² = 5,83 · gl = 5 · p = 0,323 → sem desvio significativo ao nível de 5% (compatível com aleatoriedade).*

## 8. Complementos úteis

### Frequência das dezenas (esperado ≈ 22,6 aparições em 100 concursos)

| Dezena | Aparições | | Dezena | Aparições | | Dezena | Aparições |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 01 | 24 | | 12 | 20 | | 23 | 23 |
| 02 | 30 | | 13 | 17 | | 24 | 24 |
| 03 | 19 | | 14 | 22 | | 25 | 26 |
| 04 | 28 | | 15 | 21 | | 26 | 27 |
| 05 | 16 | | 16 | 21 | | 27 | 24 |
| 06 | 28 | | 17 | 13 | | 28 | 28 |
| 07 | 20 | | 18 | 17 | | 29 | 25 |
| 08 | 25 | | 19 | 19 | | 30 | 19 |
| 09 | 23 | | 20 | 25 | | 31 | 26 |
| 10 | 19 | | 21 | 18 | |  |  |
| 11 | 29 | | 22 | 24 | |  |  |

**Mais sorteadas (top 7):** 02 (30x), 11 (29x), 04 (28x), 06 (28x), 28 (28x), 26 (27x), 25 (26x)

**Menos sorteadas (7 últimas):** 17 (13x), 05 (16x), 13 (17x), 18 (17x), 21 (18x), 03 (19x), 10 (19x)

**Pares de dezenas que mais saíram juntos:** 06-26 (10x), 25-31 (10x), 27-31 (10x), 28-31 (10x), 01-06 (9x)

### Perfil composto mais provável (combinação dos padrões dominantes)

| Tópico | Padrão dominante |
| --- | --- |
| Pares / ímpares | 4 pares / 3 ímpares |
| Baixas / altas | 3 baixas / 4 altas |
| Soma | 120–134 |
| Repetidas do anterior | 1 repetida |
| Grupos (G1/G2/G3) | 3 no G1 (01–10) / 2 no G2 (11–20) / 2 no G3 (21–31) |
| Grupos ocupados | 3 grupos ocupados |
| Dezenas em sequência | 1 dupla |

**Leitura do perfil:** um jogo com 4 pares/3 ímpares, 3 baixas/4 altas, soma entre 120–134, 1 dezena repetida do concurso anterior, distribuição 3-2-2 entre os grupos e exatamente 1 dupla de dezenas consecutivas.

> ⚠️ **Limite estatístico:** nenhum desses padrões aumenta a chance de acerto. Cada combinação de 7 dezenas tem sempre 1 em 2.629.575 de chance. Os testes de qui-quadrado desta análise **não rejeitaram a hipótese de aleatoriedade** em nenhum tópico (todos com p > 0,05 — o caso mais próximo foi o de grupos, p = 0,055). Os padrões servem para **organizar e filtrar jogos**, não para prever resultados.

## 9. Metodologia

- Base: resultados oficiais da API da Caixa (`servicebus2.caixa.gov.br/portaldeloterias/api/diadesorte`), 100 últimos concursos (1238 a 1337). Arquivo espelho em `data/dia-de-sorte.json`.
- Para cada um dos 2.629.575 jogos possíveis de 7 dezenas foi calculada a mesma métrica de cada tópico: isso gera a coluna **“esperado por azar”** (distribuição exata, não aproximada).
- Teste de aderência **qui-quadrado** comparando observado × esperado, com agrupamento de caudas raras (esperado < 5) e significância de 5%.
- Repetidas usam o concurso imediatamente anterior a cada sorteio (inclusive o 1237, fora da janela, para o primeiro concurso analisado).
- Soma: faixas de 15 pontos; complementadas por média, mediana, moda, desvio-padrão e percentis.
