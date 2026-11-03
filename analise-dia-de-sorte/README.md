# Dia de Sorte — análise estatística dos últimos 100 concursos

Análise dos **concursos 1238 a 1337** (06/07/2026 → 01/11/2026), com base nos
resultados oficiais da **API das Loterias Caixa**.

## O que responder

| # | Tópico | Padrão mais prevalente | Concursos |
| --- | --- | --- | --- |
| 1 | Pares / ímpares | 4 pares / 3 ímpares | 29 (29%) |
| 2 | Baixas / altas | 3 baixas / 4 altas (empate com 4/3) | 29 (29%) |
| 3 | Soma | 120–134 | 22 (22%) |
| 4 | Repetidas do concurso anterior | 1 repetida | 38 (38%) |
| 5 | Grupos em sequência (01–10 / 11–20 / 21–31) | 3 / 2 / 2 | 18 (18%) |
| 6 | Dezenas em sequência | 1 dupla | 44 (44%) |

Cada tópico tem uma tabela completa (ordem decrescente de prevalência) no relatório,
com a coluna **“Esperado (azar)”** — a frequência exata que o puro azar produziria,
calculada avaliando as **2.629.575** combinações possíveis de 7 dezenas — e o teste
**qui-quadrado** de aderência. Nenhum tópico rejeitou a aleatoriedade (menor p = 0,055,
em grupos).

## Arquivos

```
analise.py           cálculo de todos os tópicos + distribuição teórica exata + CSVs
relatorio.py         gera relatorio.md e relatorio.html a partir de resultados/analise.json
fetch_caixa.py       coletor da API oficial (--verificar confere o espelho local)
notion_payload.py    monta os blocos usados na página do Notion
data/
  dia-de-sorte.json  1337 concursos (espelho do retorno da API oficial)
resultados/
  analise.json       todos os números da análise
  tab_1_pares_impares.csv
  tab_2_baixas_altas.csv
  tab_3_soma_faixas.csv
  tab_4_repetidas.csv
  tab_5_grupos.csv
  tab_6_sequencias.csv
  tab_concursos.csv  os 100 concursos classificados (pares, baixas, soma, grupos…)
relatorio.md/.html   relatório final
```

## Como reproduzir

```bash
python3 analise.py      # recalcula tudo (≈20 s, sem dependências externas)
python3 relatorio.py    # regenera os relatórios
python3 fetch_caixa.py --ultimos 100   # atualiza a base direto da API (requer acesso)
python3 fetch_caixa.py --verificar     # confere o espelho contra a API oficial
```

## Definições usadas

- **Pares / ímpares**: quantidade de dezenas pares no jogo (01–31 tem 15 pares, 16 ímpares).
- **Baixas / altas**: baixas = 01–15; altas = 16–31.
- **Soma**: soma aritmética das 7 dezenas (mínimo 28, máximo 196, média teórica 112).
- **Repetidas**: dezenas do concurso N que também saíram em N−1.
- **Grupos**: G1 = 01–10, G2 = 11–20, G3 = 21–31 (o desenho das faixas em que o Dia de Sorte é exibido).
- **Sequências**: dezenas consecutivas no mesmo jogo (12-13 = dupla, 05-06-07 = trio, …).

## Aviso

Loteria é entretenimento, não investimento: qualquer jogo de 7 dezenas tem sempre
1 chance em 2.629.575, independentemente do padrão. Os recortes acima servem para
organizar e filtrar jogos, não para prever resultados. 18+.
