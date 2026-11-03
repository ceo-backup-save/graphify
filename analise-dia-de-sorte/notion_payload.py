#!/usr/bin/env python3
"""Monta os blocos Notion (JSON) do resultado estatístico, em 3 partes."""
from __future__ import annotations

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
A = json.loads((BASE / "resultados" / "analise.json").read_text())
T, META, C = A["topicos"], A["meta"], A["padrao_composto"]
ES, REP, SEQ = (T["soma"]["estatisticas"], T["repetidas"]["estatisticas"],
                T["sequencias"]["estatisticas"])


def txt(s: str, bold=False, code=False, color="default") -> list:
    return [{"type": "text", "text": {"content": s},
             "annotations": {"bold": bold, "code": code, "color": color}}]


def par(s: str, bold=False, color="default") -> dict:
    return {"object": "block", "type": "paragraph",
            "paragraph": {"rich_text": txt(s, bold, color=color)}}


def h1(s: str) -> dict:
    return {"object": "block", "type": "heading_1", "heading_1": {"rich_text": txt(s)}}


def h2(s: str) -> dict:
    return {"object": "block", "type": "heading_2", "heading_2": {"rich_text": txt(s)}}


def bullet(s: str, bold_prefix: str | None = None) -> dict:
    rt = ([{"type": "text", "text": {"content": bold_prefix},
            "annotations": {"bold": True}}] if bold_prefix else []) + txt(s)
    return {"object": "block", "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": rt}}


def callout(s: str, emoji="🎲", color="gray_background") -> dict:
    return {"object": "block", "type": "callout",
            "callout": {"rich_text": txt(s),
                        "icon": {"type": "emoji", "emoji": emoji}, "color": color}}


def div() -> dict:
    return {"object": "block", "type": "divider", "divider": {}}


def tabela(cabecalho: list[str], linhas: list[list[str]], larguras: list[int] | None = None) -> dict:
    w = len(cabecalho)
    larguras = larguras or [1] * w
    rows = [{"object": "block", "type": "table_row",
             "table_row": {"cells": [txt(c, bold=True) for c in cabecalho]}}]
    for linha in linhas:
        rows.append({"object": "block", "type": "table_row",
                     "table_row": {"cells": [txt(str(c)) for c in linha]}})
    return {"object": "block", "type": "table",
            "table": {"table_width": w, "has_column_header": True,
                      "has_row_header": False, "children": rows}}


def linhas_tab(bloco: list[dict], limite: int = 6) -> list[list]:
    """Top N padrões + linha agregada do resto."""
    base = [[r["rank"], r["padrao"], r["freq"], f"{r['pct']:.0f}%".replace(".", ","),
             f"{r['esperado_pct']:.1f}%".replace(".", ",").replace(",0%", "%"),
             f"{r['desvio_pct']:+.1f}".replace(".", ",")] for r in bloco[:limite]]
    if len(bloco) > limite:
        resto = bloco[limite:]
        fq = sum(r["freq"] for r in resto)
        base.append(["—", f"demais {len(resto)} padrões", fq,
                     f"{100 * fq / 100:.0f}%", "—", "—"])
    return base


CAB = ["#", "Padrão", "Qtd", "%", "Esperado", "Desvio"]
P1: list[dict] = []
P2: list[dict] = []
P3: list[dict] = []

P1.append(callout(
    f"Fonte: API oficial Loterias Caixa (servicebus2.caixa.gov.br/portaldeloterias/api/diadesorte) · "
    f"janela: últimos {META['n_concursos']} concursos ({META['janela_concursos'][0]}–"
    f"{META['janela_concursos'][1]}, {META['periodo'][0]} a {META['periodo'][1]}) · "
    f"universo 01–31 com 7 dezenas · {META['combinacoes_possiveis']:,} combinações possíveis. "
    f"Coluna “Esperado” = frequência que o puro azar produziria (distribuição exata)."
    .replace(",", "."), "🎲"))
P1.append(par("Nenhum arquivo chegou junto à solicitação — a base usada são os resultados oficiais "
              "da Caixa, conferidos contra a API concurso a concurso.", color="gray"))
P1.append(h1("1. Resumo executivo — padrão mais prevalente por tópico"))
P1.append(tabela(["Tópico", "Padrão dominante", "Qtd", "%", "Esperado", "Desvio"], [
    ["1. Pares / Ímpares", T["pares_impares"]["linhas"][0]["padrao"],
     T["pares_impares"]["linhas"][0]["freq"], "29%", "29,1%", "-0,1 p.p."],
    ["2. Baixas / Altas", T["baixas_altas"]["linhas"][0]["padrao"],
     T["baixas_altas"]["linhas"][0]["freq"], "29%", "31,5%", "-2,5 p.p."],
    ["3. Soma", "120–134", 22, "22%", "21,7%", "+0,3 p.p."],
    ["4. Repetidas do anterior", "1 repetida", 38, "38%", "35,8%", "+2,2 p.p."],
    ["5. Grupos em sequência", "3 / 2 / 2 (G1/G2/G3)", 18, "18%", "11,3%", "+6,7 p.p."],
    ["6. Dezenas em sequência", "1 dupla", 44, "44%", "40,4%", "+3,6 p.p."],
]))

P1.append(div())
P1.append(h1("2. Pares / ímpares"))
P1.append(par("Quantidade de dezenas pares em cada jogo (ímpares = 7 − pares). Universo 01–31: "
              "15 pares e 16 ímpares."))
P1.append(tabela(CAB, linhas_tab(T["pares_impares"]["linhas"], 6)))
P1.append(bullet(" 4 pares / 3 ímpares, com 29 concursos (29%) — exatamente o esperado por azar.",
                 "Mais comum:"))
P1.append(bullet(" 54% dos concursos tiveram 3 ou 4 dezenas pares.", "Equilíbrio:"))
P1.append(bullet(" χ² = 5,24 · p = 0,263 → sem desvio significativo (aleatório).", "Teste:"))

P2.append(h1("3. Baixas / altas"))
P2.append(par("Baixas = 01–15 (15 dezenas) · altas = 16–31 (16 dezenas)."))
P2.append(tabela(CAB, linhas_tab(T["baixas_altas"]["linhas"], 6)))
P2.append(bullet(" 3 baixas / 4 altas e 4 baixas / 3 altas, empatados com 29 concursos (29%) cada.",
                 "Mais comum:"))
P2.append(bullet(" 58% dos concursos ficaram entre 3 e 4 dezenas de cada lado; extremos (0 ou 7) "
                 "não ocorreram.", "Equilíbrio:"))
P2.append(bullet(" χ² = 1,68 · p = 0,794 → sem desvio significativo.", "Teste:"))

P2.append(h1("4. Soma das 7 dezenas"))
P2.append(par(f"Faixas de 15 pontos. Média observada {ES['media']:.2f} (teórica 112) · mediana "
              f"{ES['mediana']:.0f} · σ {ES['desvio_padrao']:.2f} · mín {ES['minimo']} · "
              f"máx {ES['maximo']} · moda {ES['moda'][0]} (5x).".replace(".", ",")))
P2.append(tabela(CAB, linhas_tab(T["soma"]["faixas"], 6)))
P2.append(bullet(" 120–134, com 22 concursos (22%).", "Faixa mais frequente:"))
P2.append(bullet(" 80% das somas caíram entre 90 e 149; 95% entre 71 e 153.", "Concentração:"))
P2.append(bullet(" χ² = 7,11 · p = 0,212 → sem desvio significativo.", "Teste:"))

P2.append(h1("5. Repetidas do concurso anterior"))
P2.append(par(f"Dezenas do concurso N que já haviam saído em N−1. Média de {REP['media']:.2f} "
              f"repetidas por concurso (azar: {REP['esperado_teorico']:.2f}).".replace(".", ",")))
P2.append(tabela(CAB, linhas_tab(T["repetidas"]["linhas"], 6)))
P2.append(bullet(" 1 repetida (38 concursos, 38%), seguida por 2 repetidas (36%).", "Mais comum:"))
P2.append(bullet(" 90% dos concursos repetiram ao menos 1 dezena; 74% repetiram 1 ou 2.", "Volume:"))
P2.append(bullet(" χ² = 1,74 · p = 0,784 → sem desvio significativo.", "Teste:"))

P3.append(h1("6. Grupos em sequência"))
P3.append(par("Grupos fixos: G1 = 01–10 (10 dezenas) · G2 = 11–20 (10) · G3 = 21–31 (11). "
              "Como as 7 dezenas se distribuem entre os grupos."))
P3.append(tabela(["#", "G1 / G2 / G3", "Qtd", "%", "Esperado", "Desvio"],
                 [["1", "3 / 2 / 2", 18, "18%", "11,3%", "+6,7 p.p."],
                  ["2", "2 / 2 / 3", 14, "14%", "12,7%", "+1,3 p.p."],
                  ["3", "1 / 2 / 4", 9, "9%", "5,7%", "+3,4 p.p."],
                  ["4", "2 / 1 / 4", 9, "9%", "5,7%", "+3,4 p.p."],
                  ["5", "1 / 3 / 3", 8, "8%", "7,5%", "+0,5 p.p."],
                  ["6", "2 / 3 / 2", 5, "5%", "11,3%", "-6,3 p.p."],
                  ["—", "demais 17 padrões", 37, "37%", "—", "—"]]))
P3.append(bullet(" 3 dezenas em 01–10, 2 em 11–20 e 2 em 21–31 (18 concursos, 18% contra 11,3% "
                 "esperados) — o maior desvio de toda a análise.", "Mais comum:"))
P3.append(bullet(" 88% dos concursos ocuparam os 3 grupos; nenhum ficou restrito a um grupo só. "
                 "Pular o G2 (G1+G3) ocorreu em 6%.", "Ocupação:"))
P3.append(bullet(" média por grupo: G1 2,32 · G2 2,04 · G3 2,64 (azar: 2,26 / 2,26 / 2,48).",
                 "Média:"))
P3.append(bullet(" χ² = 15,24 · p = 0,055 → no limite, mas ainda sem significância a 5%.",
                 "Teste:"))

P3.append(h1("7. Dezenas em sequência (dupla / trio / quadra)"))
P3.append(par("Dezenas consecutivas dentro do mesmo jogo: 12-13 = dupla · 05-06-07 = trio · "
              "04-05-06-07 = quadra."))
P3.append(tabela(CAB, linhas_tab(T["sequencias"]["padroes"], 6)))
P3.append(bullet(" exatamente 1 dupla — 44 concursos (44%, contra 40,4% esperados).", "Mais comum:"))
P3.append(bullet(f" {SEQ['pct_com_alguma_sequencia']:.0f}% dos concursos tiveram alguma sequência "
                 f"(azar: {SEQ['esperado_pct_com_alguma']:.1f}%), com média de "
                 f"{SEQ['media_runs']:.2f} sequência por jogo.".replace(".", ","), "Presença:"))
P3.append(bullet(" 1 quadra em 100 concursos; quina ou maior, nenhuma.", "Raros:"))
P3.append(bullet(" χ² = 5,83 · p = 0,323 → sem desvio significativo.", "Teste:"))

P3.append(div())
P3.append(h1("8. Perfil composto mais provável"))
P3.append(tabela(["Tópico", "Padrão dominante"], [
    ["Pares / ímpares", C["pares_impares"]],
    ["Baixas / altas", C["baixas_altas"]],
    ["Soma", C["soma"]],
    ["Repetidas do anterior", C["repetidas"]],
    ["Grupos (G1/G2/G3)", "3 / 2 / 2"],
    ["Grupos ocupados", C["grupos_ocupados"]],
    ["Dezenas em sequência", C["sequencias"]],
]))
P3.append(callout("Um jogo aderente ao histórico: 4 pares / 3 ímpares · 3 baixas / 4 altas · "
                  "soma 120–134 · 1 dezena repetida do concurso anterior · 3 dezenas em 01–10, "
                  "2 em 11–20 e 2 em 21–31 · exatamente 1 dupla de consecutivas.", "✅",
                  "green_background"))
P3.append(h2("Metodologia"))
P3.append(bullet(" 2.629.575 combinações possíveis de 7 dezenas foram avaliadas para gerar a "
                 "coluna “Esperado” (distribuição exata do azar, não aproximação).", "Base exata:"))
P3.append(bullet(" qui-quadrado com agrupamento de caudas raras (esperado < 5), nível de 5%. "
                 "Nenhum tópico rejeitou a aleatoriedade (menor p: 0,055 em grupos).", "Teste:"))
P3.append(bullet(" relatorio.html e relatorio.md (relatório completo), resultados/analise.json, "
                 "resultados/tab_1..6_*.csv (uma tabela por tópico), analise.py e fetch_caixa.py.",
                 "Arquivos:"))
P3.append(callout("Nenhum desses padrões aumenta a chance de acerto: qualquer jogo de 7 dezenas "
                  "tem 1 chance em 2.629.575. Os padrões servem para organizar e filtrar jogos, "
                  "não para prever resultados. Jogue com responsabilidade (18+).", "⚠️",
                  "yellow_background"))

for nome, parte in (("p1", P1), ("p2", P2), ("p3", P3)):
    (BASE / "resultados" / f"notion_{nome}.json").write_text(
        json.dumps({"children": parte}, ensure_ascii=False))
    print(nome, "blocos:", len(parte), "bytes:", len(json.dumps(parte, ensure_ascii=False)))
