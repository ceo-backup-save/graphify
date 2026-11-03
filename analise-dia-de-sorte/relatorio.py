#!/usr/bin/env python3
"""Gera relatorio.md e relatorio.html a partir de resultados/analise.json."""
from __future__ import annotations

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
A = json.loads((BASE / "resultados" / "analise.json").read_text())

META = A["meta"]
T = A["topicos"]
DEZ = A["dezenas"]
C = A["padrao_composto"]


def n(x, casas=1):
    """Número no padrão brasileiro."""
    s = f"{x:,.{casas}f}" if isinstance(x, float) else f"{x:,}"
    return s.replace(",", "@").replace(".", ",").replace("@", ".")


def pct(x):
    return f"{n(float(x), 1)}%"


def esp_fmt(esperado_pct):
    if esperado_pct is None:
        return "—"
    return "<0,1%" if esperado_pct < 0.1 else pct(esperado_pct)


def desvio_fmt(d):
    return "0,0" if abs(d) < 0.05 else n(d, 1)


def limitar(linhas, n_max=12):
    """Corta tabelas longas, agrupando a cauda num único padrão."""
    if len(linhas) <= n_max:
        return linhas
    resto = linhas[n_max:]
    return linhas[:n_max] + [{
        "rank": f"{n_max + 1}º+",
        "padrao": f"outros {len(resto)} padrões (agrupados)",
        "freq": sum(r["freq"] for r in resto),
        "pct": round(sum(r["pct"] for r in resto), 1),
        "esperado_pct": round(sum(r["esperado_pct"] for r in resto), 2),
        "desvio_pct": round(sum(r["desvio_pct"] for r in resto), 1),
    }]


# ---------------------------------------------------------------- agregações
def soma_freq(linhas, cond):
    return sum(r["freq"] for r in linhas if cond(r["chave"]))

pi, ba, sm, rp = T["pares_impares"], T["baixas_altas"], T["soma"], T["repetidas"]
gr, sq = T["grupos"], T["sequencias"]

AGG = {
    "pi_maioria_par": soma_freq(pi["linhas"], lambda k: k >= 4),
    "pi_maioria_impar": soma_freq(pi["linhas"], lambda k: k <= 3),
    "ba_maioria_alta": soma_freq(ba["linhas"], lambda k: k <= 3),
    "ba_maioria_baixa": soma_freq(ba["linhas"], lambda k: k >= 4),
    "ba_equilibrio": soma_freq(ba["linhas"], lambda k: k in (3, 4)),
    "pi_equilibrio": soma_freq(pi["linhas"], lambda k: k in (3, 4)),
    "soma_central": soma_freq(sm["faixas"], lambda k: k in ("90–104", "105–119",
                                                             "120–134", "135–149")),
    "rep_ao_menos_1": soma_freq(rp["linhas"], lambda k: k >= 1),
    "rep_1_ou_2": soma_freq(rp["linhas"], lambda k: k in (1, 2)),
    "gr_tres": soma_freq(gr["ocupacao"], lambda k: k == 3),
    "seq_alguma": sq["estatisticas"]["com_alguma_sequencia"],
    "seq_dupla_ou_mais": soma_freq(sq["padroes"], lambda k: k != "Sem sequência"),
}
ES = sm["estatisticas"]
REP = rp["estatisticas"]
SEQ = sq["estatisticas"]

TITULO = "Dia de Sorte — Análise Estatística dos Últimos 100 Concursos"
SUBTITULO = (f"Concursos {META['janela_concursos'][0]} a {META['janela_concursos'][1]} · "
             f"{META['periodo'][0]} a {META['periodo'][1]} · fonte: API oficial Loterias Caixa")

# ---------------------------------------------------------------- markdown
md: list[str] = []
w = md.append

w(f"# {TITULO}\n")
w(f"**{SUBTITULO}**\n")
w("| Item | Valor |")
w("| --- | --- |")
w(f"| Jogo | {META['jogo']} (31 dezenas, 7 sorteadas) |")
w(f"| Janela analisada | últimos **{META['n_concursos']} concursos** "
  f"({META['janela_concursos'][0]}–{META['janela_concursos'][1]}) |")
w(f"| Período | {META['periodo'][0]} a {META['periodo'][1]} |")
w(f"| Fonte | {META['fonte']} |")
w(f"| Histórico disponível | {n(META['concursos_no_historico'])} concursos |")
w(f"| Universo de combinações | {n(META['combinacoes_possiveis'])} jogos possíveis de 7 dezenas |")
w("")

w("> **Observação sobre o arquivo enviado:** nenhum arquivo chegou junto à mensagem "
  "(o workspace não contém CSV/Excel/PDF de jogos). A análise foi feita diretamente sobre "
  "os resultados oficiais da Caixa — o que é mais confiável do que uma planilha manual. "
  "Se o arquivo era uma lista de jogos para conferência, reenvie que eu cruzo com este padrão.\n")

w("## 1. Resumo executivo — padrão mais prevalente por tópico\n")
w("| # | Tópico | Padrão mais prevalente | Concursos | % | Esperado por azar | Desvio |")
w("| --- | --- | --- | --- | --- | --- | --- |")


def top(linhas):
    m = max(linhas, key=lambda r: r["freq"])
    return m


resumo = [
    ("1", "Pares / Ímpares", top(pi["linhas"])),
    ("2", "Baixas / Altas", top(ba["linhas"])),
    ("3", "Soma", top(sm["faixas"])),
    ("4", "Repetidas do concurso anterior", top(rp["linhas"])),
    ("5", "Grupos em sequência", top(gr["padroes"])),
    ("6", "Dezenas em sequência", top(sq["padroes"])),
]
for num, nome, r in resumo:
    w(f"| {num} | {nome} | {r['padrao']} | {r['freq']} | {pct(r['pct'])} | "
      f"{esp_fmt(r['esperado_pct'])} | {desvio_fmt(r['desvio_pct'])} p.p. |")
w("")

# ------------------------------------------------- tabelas por tópico (md)
def tabela_md(linhas, col1="Padrão", extra=None):
    w(f"| Rank | {col1} | Concursos | % | Esperado (azar) | Desvio |")
    w("| --- | --- | --- | --- | --- | --- |")
    for r in linhas:
        w(f"| {r['rank']} | {r['padrao']} | {r['freq']} | {pct(r['pct'])} | "
          f"{esp_fmt(r['esperado_pct'])} | {desvio_fmt(r['desvio_pct'])} p.p. |")
    w("")


def qui2_md(bloco, rotulo="Teste qui-quadrado"):
    q = bloco["qui2"]
    w(f"*{rotulo}: χ² = {n(q['qui2'], 2)} · gl = {q['gl']} · p = {n(q['p_valor'], 3)} → "
      f"{q['interpretacao']}.*\n")


w("## 2. Pares / ímpares\n")
w(f"Distribuição da quantidade de dezenas **pares** em cada um dos 100 jogos "
  f"(ímpares = 7 − pares). O universo 01–31 tem 15 pares e 16 ímpares.\n")
tabela_md(pi["linhas"])
w(f"- **Padrão mais comum: {top(pi['linhas'])['padrao']}** — {top(pi['linhas'])['freq']} concursos "
  f"({pct(top(pi['linhas'])['pct'])}).")
w(f"- Equilíbrio (3 ou 4 pares) responde por **{pct(AGG['pi_equilibrio'])}** dos concursos.")
w(f"- 5 pares / 2 ímpares foi o 3º mais frequente ({pct(pi['linhas'][2]['pct'])}), "
  f"acima do esperado por azar ({pct(pi['linhas'][2]['esperado_pct'])}).")
w(f"- No total saíram {pi['total_dezenas_pares']} dezenas pares e "
  f"{pi['total_dezenas_impares']} ímpares — praticamente meio a meio.\n")
qui2_md(pi)

w("## 3. Baixas / altas\n")
w("Baixas = 01–15 (15 dezenas); altas = 16–31 (16 dezenas).\n")
tabela_md(ba["linhas"])
w(f"- **Padrão mais comum: 3 baixas / 4 altas e 4 baixas / 3 altas** — empatados com "
  f"{top(ba['linhas'])['freq']} concursos cada ({pct(top(ba['linhas'])['pct'])}).")
w(f"- Equilíbrio (3 a 4 dezenas de cada lado) concentra **{pct(AGG['ba_equilibrio'])}** dos casos.")
w(f"- Jogos com maioria alta (≤3 baixas) = {pct(AGG['ba_maioria_alta'])}; maioria baixa "
  f"(≥4 baixas) = {pct(AGG['ba_maioria_baixa'])}.")
w(f"- Extremos (0 ou 7 dezenas de um lado) **não ocorreram** no período.\n")
qui2_md(ba)

w("## 4. Soma das 7 dezenas\n")
w(f"Mínimo teórico 28 (1+2+…+7), máximo 196 (25+…+31), média teórica {n(ES['media_teorica'])}.\n")
tabela_md(sm["faixas"], "Faixa de soma")
w(f"| Estatística | Valor |")
w("| --- | --- |")
w(f"| Média observada | **{n(ES['media'], 2)}** |")
w(f"| Mediana | {n(ES['mediana'])} |")
w(f"| Moda | {ES['moda'][0]} (apareceu {ES['moda'][1]}x) |")
w(f"| Desvio-padrão | {n(ES['desvio_padrao'], 2)} |")
w(f"| Mínimo / máximo | {ES['minimo']} / {ES['maximo']} |")
w(f"| P25 – P75 | {n(ES['p25'])} – {n(ES['p75'])} |")
w(f"| Faixa ±1 desvio-padrão | {n(ES['faixa_1sigma'][0])} – {n(ES['faixa_1sigma'][1])} |")
w(f"| Faixa central de 95% teórica | {ES['faixa_95pct_teorica'][0]} – {ES['faixa_95pct_teorica'][1]} "
  f"({ES['obs_dentro_95pct']} dos 100 concursos caíram dentro) |")
w("")
w(f"- **Faixa de soma mais comum: {top(sm['faixas'])['padrao']}** com "
  f"{top(sm['faixas'])['freq']} concursos ({pct(top(sm['faixas'])['pct'])}).")
w(f"- {pct(AGG['soma_central'])} dos concursos tiveram soma entre **90 e 149**.")
w(f"- Somam entre {n(ES['faixa_1sigma'][0])} e {n(ES['faixa_1sigma'][1])}: "
  f"faixa de 1 desvio-padrão em torno da média.\n")
qui2_md(sm)

w("## 5. Repetidas do concurso anterior\n")
w("Quantas das 7 dezenas sorteadas já haviam saído no concurso imediatamente anterior "
  "(base: concursos 1237–1337).\n")
tabela_md(rp["linhas"])
w(f"| Estatística | Valor |")
w("| --- | --- |")
w(f"| Média de repetidas por concurso | **{n(REP['media'], 2)}** (esperado por azar: {n(REP['esperado_teorico'], 2)}) |")
w(f"| Mediana | {n(REP['mediana'])} |")
w(f"| Desvio-padrão | {n(REP['desvio_padrao'], 2)} |")
w(f"| Total de dezenas repetidas | {REP['total_dezenas_repetidas']} |")
w(f"| Máximo / mínimo | {REP['max']} / {REP['min']} |")
w("")
w(f"- **Padrão mais comum: 1 repetida** ({top(rp['linhas'])['freq']} concursos, "
  f"{pct(top(rp['linhas'])['pct'])}), seguido de perto por 2 repetidas "
  f"({pct(rp['linhas'][1]['pct'])}).")
w(f"- **{pct(AGG['rep_ao_menos_1'])}** dos concursos repetiram ao menos 1 dezena; "
  f"{pct(AGG['rep_1_ou_2'])} repetiram 1 ou 2.")
w(f"- Repetir 3 dezenas: {pct(rp['linhas'][2]['pct'])}; 4 repetidas: "
  f"{pct(rp['linhas'][4]['pct'])}; 5 repetidas: {pct(rp['linhas'][5]['pct'])} "
  f"(um caso raro: esperado por azar seria 0,2%).")
w("- Jogos sem nenhuma repetida foram minoria (**10%**), e 6 ou 7 repetidas nunca ocorreram.\n")
qui2_md(rp)

w("## 6. Grupos em sequência (faixas de dezenas)\n")
w("Grupos fixos: **G1 = 01–10** (10 dezenas), **G2 = 11–20** (10 dezenas), "
  "**G3 = 21–31** (11 dezenas). A tabela mostra como as 7 dezenas se distribuem entre os grupos.\n")
tabela_md(limitar(gr["padroes"], 12), "Distribuição G1 / G2 / G3")
w(f"- **Padrão mais comum: 3 / 2 / 2** (3 dezenas em 01–10, 2 em 11–20, 2 em 21–31) — "
  f"{top(gr['padroes'])['freq']} concursos ({pct(top(gr['padroes'])['pct'])}), contra "
  f"{pct(top(gr['padroes'])['esperado_pct'])} esperados por azar: o desvio mais forte de toda a análise.")
w(f"- Ocupação dos grupos: {pct(AGG['gr_tres'])} dos concursos tiveram **os 3 grupos ocupados**.\n")
w("**Quantas dezenas por grupo (média):**\n")
w("| Grupo | Média observada | Esperado por azar |")
w("| --- | --- | --- |")
for i, (nome, obs, esp) in enumerate(zip(["G1 (01–10)", "G2 (11–20)", "G3 (21–31)"],
                                         gr["media_por_grupo"], gr["esperado_por_grupo"])):
    w(f"| {nome} | {n(obs, 2)} | {n(esp, 2)} |")
w("")
w("**Grupos contíguos ocupados (leitura de sequência de faixas):**\n")
tabela_md(gr["contiguos"])
qui2_md({"qui2": gr["qui2_contiguos"]}, "Contiguidade das faixas")
w(f"- Em **{pct(AGG['gr_tres'])}** dos concursos há dezena em todas as faixas; o caso "
  f"'pulou um grupo' (G1+G3, sem G2) apareceu em {pct(gr['contiguos'][1]['pct'])}.")
w(f"- Nunca houve concurso concentrado em **um único grupo**.\n")
qui2_md(gr)

w("## 7. Dezenas em sequência (dupla / trio / quadra)\n")
w("Sequência = dezenas consecutivas dentro do mesmo jogo (12-13 = dupla; 05-06-07 = trio; "
  "04-05-06-07 = quadra…).\n")
tabela_md(sq["padroes"], "Padrão de sequência no jogo")
w("**Maior sequência de cada concurso:**\n")
tabela_md(sq["maior_sequencia"], "Maior sequência")
w(f"- **{pct(SEQ['pct_com_alguma_sequencia'])} dos concursos tiveram pelo menos uma sequência** "
  f"({SEQ['com_alguma_sequencia']} de 100); o esperado por azar seria {pct(SEQ['esperado_pct_com_alguma'])}.")
w(f"- **Padrão mais comum: exatamente 1 dupla** — {top(sq['padroes'])['freq']} concursos "
  f"({pct(top(sq['padroes'])['pct'])}).")
w(f"- Duas duplas apareceram {pct(sq['padroes'][2]['pct'])} (abaixo dos {pct(sq['padroes'][2]['esperado_pct'])} esperados); "
  f"trio em {pct(sq['padroes'][3]['pct'])}; trio + dupla em {pct(sq['padroes'][4]['pct'])}.")
w(f"- Quadra apareceu 1 vez (1%); **quina ou mais: nenhuma vez** no período.")
w(f"- Média de {n(SEQ['media_runs'], 2)} sequência por concurso.\n")
qui2_md(sq)

w("## 8. Complementos úteis\n")
w(f"### Frequência das dezenas (esperado ≈ {n(DEZ['esperado'])} aparições em 100 concursos)\n")
w("| Dezena | Aparições | | Dezena | Aparições | | Dezena | Aparições |")
w("| --- | --- | --- | --- | --- | --- | --- | --- |")
f = DEZ["frequencia"]
linhas_f = []
for i in range(1, 12):
    a = f[str(i)]
    b_col, b_val = (i + 11, f[str(i + 11)]) if i + 11 <= 22 else ("", "")
    c_col, c_val = (i + 22, f[str(i + 22)]) if i + 22 <= 31 else ("", "")
    b_cell = f"{b_col:02d} | {b_val}" if isinstance(b_col, int) else " | "
    c_cell = f"{c_col:02d} | {c_val}" if isinstance(c_col, int) else " | "
    linhas_f.append(f"| {i:02d} | {a} | | {b_cell} | | {c_cell} |")
md.extend(linhas_f)
w("")
w("**Mais sorteadas (top 7):** " +
  ", ".join(f"{d:02d} ({q}x)" for d, q in DEZ["quentes"]) + "\n")
w("**Menos sorteadas (7 últimas):** " +
  ", ".join(f"{d:02d} ({q}x)" for d, q in DEZ["frias"]) + "\n")
w("**Pares de dezenas que mais saíram juntos:** " +
  ", ".join(f"{p['par']} ({p['freq']}x)" for p in DEZ["pares_mais_frequentes"][:5]) + "\n")
w("### Perfil composto mais provável (combinação dos padrões dominantes)\n")
w("| Tópico | Padrão dominante |")
w("| --- | --- |")
for k, rot in [("pares_impares", "Pares / ímpares"), ("baixas_altas", "Baixas / altas"),
               ("soma", "Soma"), ("repetidas", "Repetidas do anterior"),
               ("grupos", "Grupos (G1/G2/G3)"), ("grupos_ocupados", "Grupos ocupados"),
               ("sequencias", "Dezenas em sequência")]:
    w(f"| {rot} | {C[k]} |")
w("")
w("**Leitura do perfil:** um jogo com 4 pares/3 ímpares, 3 baixas/4 altas, soma entre 120–134, "
  "1 dezena repetida do concurso anterior, distribuição 3-2-2 entre os grupos e exatamente "
  "1 dupla de dezenas consecutivas.\n")
w("> ⚠️ **Limite estatístico:** nenhum desses padrões aumenta a chance de acerto. "
  "Cada combinação de 7 dezenas tem sempre 1 em 2.629.575 de chance. Os testes de "
  "qui-quadrado desta análise **não rejeitaram a hipótese de aleatoriedade** em nenhum tópico "
  "(todos com p > 0,05 — o caso mais próximo foi o de grupos, p = 0,055). "
  "Os padrões servem para **organizar e filtrar jogos**, não para prever resultados.\n")

w("## 9. Metodologia\n")
w("- Base: resultados oficiais da API da Caixa (`servicebus2.caixa.gov.br/portaldeloterias/api/diadesorte`), "
  "100 últimos concursos (1238 a 1337). Arquivo espelho em `data/dia-de-sorte.json`.")
w("- Para cada um dos 2.629.575 jogos possíveis de 7 dezenas foi calculada a mesma métrica "
  "de cada tópico: isso gera a coluna **“esperado por azar”** (distribuição exata, não aproximada).")
w("- Teste de aderência **qui-quadrado** comparando observado × esperado, com agrupamento de "
  "caudas raras (esperado < 5) e significância de 5%.")
w("- Repetidas usam o concurso imediatamente anterior a cada sorteio (inclusive o 1237, "
  "fora da janela, para o primeiro concurso analisado).")
w("- Soma: faixas de 15 pontos; complementadas por média, mediana, moda, desvio-padrão e percentis.")
w("")

(BASE / "relatorio.md").write_text("\n".join(md), encoding="utf-8")

# ---------------------------------------------------------------- HTML
CSS = """
:root{
  --bg:#0d1117;--panel:#161b22;--panel2:#1c2330;--line:#2b3444;--txt:#e6edf3;
  --dim:#9aa7b8;--accent:#37d67a;--accent2:#f5b642;--hot:#ff6b6b;--cold:#4aa8ff;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--txt);
  font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
.wrap{max-width:1080px;margin:0 auto;padding:40px 24px 80px}
header.hero{border:1px solid var(--line);border-radius:16px;padding:28px 30px;
  background:linear-gradient(135deg,#17223a 0%,#131a26 55%,#1a1526 100%);margin-bottom:28px}
h1{font-size:29px;line-height:1.25;margin:0 0 8px}
.sub{color:var(--dim);font-size:14px}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}
.chip{background:#0f1620;border:1px solid var(--line);border-radius:999px;
  padding:5px 12px;font-size:12.5px;color:#c3ced9}
.chip b{color:#fff;font-weight:600}
h2{font-size:21px;margin:38px 0 6px;padding-bottom:8px;border-bottom:1px solid var(--line)}
h3{font-size:16px;margin:26px 0 8px;color:#cfd9e4}
p.note{color:var(--dim);font-size:14px;margin:6px 0 16px}
.alert{border-left:3px solid var(--accent2);background:#211d12;padding:12px 16px;
  border-radius:8px;font-size:13.5px;color:#e8dcc0;margin:18px 0}
.spoiler{border-left:3px solid var(--cold);background:#121b26;padding:12px 16px;
  border-radius:8px;font-size:13.5px;color:#c8ddf2;margin:14px 0}
table{width:100%;border-collapse:collapse;margin:14px 0 6px;font-size:13.5px}
th,td{padding:9px 10px;text-align:left;border-bottom:1px solid var(--line)}
th{background:#131a24;color:#9fb0c3;font-weight:600;font-size:12px;text-transform:uppercase;
  letter-spacing:.04em}
tr:hover td{background:#131a23}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
tr.top td{background:#12251a}
tr.top td:first-child{box-shadow:inset 3px 0 0 var(--accent)}
.badge{display:inline-block;background:#0f1620;border:1px solid var(--line);border-radius:6px;
  padding:1px 7px;font-size:11.5px;color:#9fb0c3;margin-left:6px}
.bar{height:7px;border-radius:4px;background:#1f2836;overflow:hidden;min-width:60px}
.bar>span{display:block;height:100%;background:linear-gradient(90deg,#2ea86a,#37d67a)}
.up{color:var(--accent)}.down{color:var(--hot)}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin:16px 0}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.card .k{font-size:11.5px;text-transform:uppercase;letter-spacing:.05em;color:var(--dim)}
.card .v{font-size:22px;font-weight:650;margin-top:4px}
.card .s{font-size:12px;color:var(--dim);margin-top:2px}
.grid-dez{display:grid;grid-template-columns:repeat(10,1fr);gap:7px;margin:14px 0}
.dez{border-radius:8px;padding:8px 0;text-align:center;font-size:12.5px;border:1px solid var(--line)}
.dez b{display:block;font-size:14px}
.legend{font-size:12px;color:var(--dim);margin:6px 0 18px}
code{background:#0f1620;border:1px solid var(--line);border-radius:5px;padding:1px 6px;font-size:12.5px}
footer{margin-top:44px;color:var(--dim);font-size:12.5px;border-top:1px solid var(--line);padding-top:16px}
.foot-note{color:#7f8b9c}
"""


def tabela_html(linhas, col="Padrão", destacar_top=True, largura_barra=True):
    maior = max(r["freq"] for r in linhas) or 1
    out = ['<table><thead><tr><th style="width:52px">Rank</th>'
           f"<th>{col}</th><th class='num'>Concursos</th><th class='num'>%</th>"
           "<th class='num'>Esperado (azar)</th><th class='num'>Desvio</th>"
           + ("<th style='width:150px'>Peso</th>" if largura_barra else "")
           + "</tr></thead><tbody>"]
    for r in linhas:
        cls = ' class="top"' if destacar_top and r["rank"] == 1 else ""
        desvio = r["desvio_pct"]
        cls_d = "up" if desvio > 0 else ("down" if desvio < 0 else "")
        seta = "▲" if desvio > 0.05 else ("▼" if desvio < -0.05 else "≈")
        barra = (f'<td><div class="bar"><span style="width:{100 * r["freq"] / maior:.0f}%">'
                 "</span></div></td>") if largura_barra else ""
        esp = esp_fmt(r["esperado_pct"])
        out.append(
            f"<tr{cls}><td>{r['rank']}º</td><td>{r['padrao']}"
            + ("<span class='badge'>padrão dominante</span>" if r["rank"] == 1 and destacar_top else "")
            + f"</td><td class='num'><b>{r['freq']}</b></td><td class='num'>{pct(r['pct'])}</td>"
            f"<td class='num'>{esp}</td>"
            f"<td class='num {cls_d}'>{seta} {desvio_fmt(desvio)} p.p.</td>{barra}</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def qui2_html(bloco):
    q = bloco["qui2"]
    ok = not q["significante_5pct"]
    cor = "var(--accent)" if ok else "var(--hot)"
    return (f'<p class="note">Teste qui-quadrado: χ² = {n(q["qui2"], 2)} · gl = {q["gl"]} · '
            f'<b>p = {n(q["p_valor"], 3)}</b> · <span style="color:{cor}">{q["interpretacao"]}</span></p>')


h: list[str] = []
add = h.append
add(f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{TITULO}</title><style>{CSS}</style></head><body><div class="wrap">
<header class="hero">
  <h1>{TITULO}</h1>
  <div class="sub">{SUBTITULO}</div>
  <div class="chips">
    <span class="chip">Janela <b>{META['janela_concursos'][0]}–{META['janela_concursos'][1]}</b></span>
    <span class="chip"><b>{META['n_concursos']}</b> concursos</span>
    <span class="chip">Universo <b>01–31</b> · 7 dezenas</span>
    <span class="chip">Combinações <b>{n(META['combinacoes_possiveis'])}</b></span>
    <span class="chip">Fonte <b>API oficial Caixa</b></span>
  </div>
</header>""")

add(f"""<div class="alert"><b>Nota sobre o arquivo enviado:</b> nenhum arquivo chegou com a mensagem
(workspace sem CSV/Excel/PDF de jogos). A análise roda direto sobre os resultados oficiais da
Caixa — base mais confiável que uma planilha manual. Se o arquivo era uma lista de jogos para
conferência, reenvie que eu cruzo os jogos com o padrão abaixo.</div>""")

# resumo executivo
add("<h2>1. Resumo executivo</h2>")
add('<p class="note">O padrão mais prevalente de cada tópico, do mais para o menos comum, '
    "com o quanto ele se afasta do que o puro azar produziria.</p>")
add("<table><thead><tr><th style='width:38px'>#</th><th>Tópico</th><th>Padrão dominante</th>"
    "<th class='num'>Concursos</th><th class='num'>%</th><th class='num'>Esperado</th>"
    "<th class='num'>Desvio</th></tr></thead><tbody>")
for num, nome, r in resumo:
    desvio = r["desvio_pct"]
    cls_d = "up" if desvio > 0 else "down"
    esp = esp_fmt(r["esperado_pct"])
    add(f"<tr><td>{num}</td><td><b>{nome}</b></td><td>{r['padrao']}</td>"
        f"<td class='num'><b>{r['freq']}</b></td><td class='num'>{pct(r['pct'])}</td>"
        f"<td class='num'>{esp}</td>"
        f"<td class='num {cls_d}'>{n(desvio, 1)} p.p.</td></tr>")
add("</tbody></table>")

# tema 1
add("<h2>2. Pares / ímpares</h2>")
add("<p class='note'>Quantidade de dezenas <b>pares</b> em cada jogo (ímpares = 7 − pares). "
    "O universo 01–31 tem 15 pares e 16 ímpares.</p>")
add(tabela_html(pi["linhas"]))
add(qui2_html(pi))
add(f"""<div class="cards">
<div class="card"><div class="k">Padrão dominante</div><div class="v">{top(pi['linhas'])['padrao']}</div>
<div class="s">{top(pi['linhas'])['freq']} de 100 concursos</div></div>
<div class="card"><div class="k">Equilíbrio (3–4 pares)</div><div class="v">{pct(AGG['pi_equilibrio'])}</div>
<div class="s">dos concursos</div></div>
<div class="card"><div class="k">Dezenas pares sorteadas</div><div class="v">{pi['total_dezenas_pares']}</div>
<div class="s">de {pi['total_dezenas_pares'] + pi['total_dezenas_impares']} no total</div></div></div>""")

# tema 2
add("<h2>3. Baixas / altas</h2>")
add("<p class='note'>Baixas = 01–15 (15 dezenas) · altas = 16–31 (16 dezenas).</p>")
add(tabela_html(ba["linhas"]))
add(qui2_html(ba))
add(f"""<div class="cards">
<div class="card"><div class="k">Padrão dominante</div><div class="v">3 baixas / 4 altas</div>
<div class="s">empate técnico com 4 baixas / 3 altas (29 cada)</div></div>
<div class="card"><div class="k">Equilíbrio (3–4 de cada)</div><div class="v">{pct(AGG['ba_equilibrio'])}</div>
<div class="s">dos concursos</div></div>
<div class="card"><div class="k">Extremos (0 ou 7)</div><div class="v">0</div>
<div class="s">não ocorreram no período</div></div></div>""")

# tema 3 — soma
add("<h2>4. Soma das 7 dezenas</h2>")
add(f"<p class='note'>Mínimo teórico 28 · máximo 196 · média teórica {n(ES['media_teorica'])}. "
    "Faixas de 15 pontos, ordenadas da mais frequente para a menos frequente.</p>")
add(tabela_html(sm["faixas"], "Faixa de soma"))
add(qui2_html(sm))
add(f"""<div class="cards">
<div class="card"><div class="k">Faixa dominante</div><div class="v">{top(sm['faixas'])['padrao']}</div>
<div class="s">{pct(top(sm['faixas'])['pct'])} dos concursos</div></div>
<div class="card"><div class="k">Média observada</div><div class="v">{n(ES['media'], 2)}</div>
<div class="s">mediana {n(ES['mediana'])} · σ {n(ES['desvio_padrao'], 2)}</div></div>
<div class="card"><div class="k">Soma mais repetida</div><div class="v">{ES['moda'][0]}</div>
<div class="s">apareceu {ES['moda'][1]} vezes</div></div>
<div class="card"><div class="k">Faixa 90–149</div><div class="v">{pct(AGG['soma_central'])}</div>
<div class="s">concentração central observada</div></div>
<div class="card"><div class="k">Mín / máx</div><div class="v">{ES['minimo']} / {ES['maximo']}</div>
<div class="s">P25 {n(ES['p25'])} · P75 {n(ES['p75'])}</div></div></div>""")

# tema 4 — repetidas
add("<h2>5. Repetidas do concurso anterior</h2>")
add("<p class='note'>Quantas das 7 dezenas já haviam saído no concurso imediatamente anterior.</p>")
add(tabela_html(rp["linhas"]))
add(qui2_html(rp))
add(f"""<div class="cards">
<div class="card"><div class="k">Padrão dominante</div><div class="v">1 repetida</div>
<div class="s">{top(rp['linhas'])['freq']} concursos · 2 repetidas logo atrás ({pct(rp['linhas'][1]['pct'])})</div></div>
<div class="card"><div class="k">Média de repetidas</div><div class="v">{n(REP['media'], 2)}</div>
<div class="s">esperado por azar: {n(REP['esperado_teorico'], 2)}</div></div>
<div class="card"><div class="k">Repetiu ≥ 1</div><div class="v">{pct(AGG['rep_ao_menos_1'])}</div>
<div class="s">dos concursos</div></div>
<div class="card"><div class="k">Dezenas repetidas</div><div class="v">{REP['total_dezenas_repetidas']}</div>
<div class="s">máx {REP['max']} · mín {REP['min']}</div></div></div>""")

# tema 5 — grupos
add("<h2>6. Grupos em sequência</h2>")
add("<p class='note'>Grupos fixos: <b>G1 = 01–10</b> (10 dezenas) · <b>G2 = 11–20</b> (10) · "
    "<b>G3 = 21–31</b> (11). Como as 7 dezenas se distribuem entre os grupos.</p>")
add(tabela_html(limitar(gr["padroes"], 12), "Distribuição G1 / G2 / G3"))
add(qui2_html(gr))
add("<h3>Média de dezenas por grupo</h3>")
add("<table><thead><tr><th>Grupo</th><th class='num'>Média observada</th>"
    "<th class='num'>Esperado por azar</th><th class='num'>Desvio</th></tr></thead><tbody>")
for nome, obs, esp in zip(["G1 (01–10)", "G2 (11–20)", "G3 (21–31)"],
                          gr["media_por_grupo"], gr["esperado_por_grupo"]):
    add(f"<tr><td>{nome}</td><td class='num'><b>{n(obs, 2)}</b></td>"
        f"<td class='num'>{n(esp, 2)}</td>"
        f"<td class='num'>{'+' if obs - esp > 0 else ''}{n(round(obs - esp, 2), 2)}</td></tr>")
add("</tbody></table>")
add("<h3>Grupos ocupados / contiguidade</h3>")
add(tabela_html(gr["ocupacao"]))
add(tabela_html(gr["contiguos"], "Faixas ocupadas"))
add(qui2_html({"qui2": gr["qui2_contiguos"]}))
add(f"""<div class="cards">
<div class="card"><div class="k">Padrão dominante</div><div class="v">3 / 2 / 2</div>
<div class="s">{top(gr['padroes'])['freq']} concursos ({pct(top(gr['padroes'])['pct'])})</div></div>
<div class="card"><div class="k">3 grupos ocupados</div><div class="v">{pct(AGG['gr_tres'])}</div>
<div class="s">dos concursos</div></div>
<div class="card"><div class="k">Um grupo só</div><div class="v">0</div>
<div class="s">nunca ocorreu</div></div></div>""")

# tema 6 — sequências
add("<h2>7. Dezenas em sequência</h2>")
add("<p class='note'>Sequência = dezenas consecutivas no mesmo jogo (12-13 = dupla; "
    "05-06-07 = trio; 04-05-06-07 = quadra…).</p>")
add(tabela_html(sq["padroes"], "Padrão de sequência no jogo"))
add(qui2_html(sq))
add("<h3>Maior sequência de cada concurso</h3>")
add(tabela_html(sq["maior_sequencia"], "Maior sequência"))
add(f"""<div class="cards">
<div class="card"><div class="k">Padrão dominante</div><div class="v">1 dupla</div>
<div class="s">{top(sq['padroes'])['freq']} concursos ({pct(top(sq['padroes'])['pct'])})</div></div>
<div class="card"><div class="k">Com alguma sequência</div><div class="v">{pct(SEQ['pct_com_alguma_sequencia'])}</div>
<div class="s">esperado por azar: {pct(SEQ['esperado_pct_com_alguma'])}</div></div>
<div class="card"><div class="k">Sem sequência</div><div class="v">{pct(100 - SEQ['pct_com_alguma_sequencia'])}</div>
<div class="s">{100 - SEQ['com_alguma_sequencia']} concursos</div></div>
<div class="card"><div class="k">Quadra / quina+</div><div class="v">1 / 0</div>
<div class="s">no período analisado</div></div></div>""")

# complementos: dezenas
add("<h2>8. Complementos — dezenas</h2>")
add(f"<p class='note'>Aparições de cada dezena nos 100 concursos "
    f"(esperado por azar ≈ {n(DEZ['esperado'])}). Cor mais quente = mais sorteada.</p>")
mx, mn = max(f.values()), min(f.values())
add('<div class="grid-dez">')
for d in range(1, 32):
    q = f[str(d)]
    t = (q - mn) / max(mx - mn, 1)
    cor = f"rgba(255,107,107,{0.10 + 0.55 * t:.2f})" if t >= 0.5 else \
          f"rgba(74,168,255,{0.10 + 0.55 * (1 - t):.2f})"
    add(f'<div class="dez" style="background:{cor}"><b>{d:02d}</b>{q}x</div>')
add("</div>")
add("<div class='legend'>Vermelho = mais sorteada · azul = menos sorteada.</div>")
add("<table><thead><tr><th>Top 7 mais sorteadas</th><th class='num'>x</th>"
    "<th>7 menos sorteadas</th><th class='num'>x</th></tr></thead><tbody>")
for (q1, v1), (q2, v2) in zip(DEZ["quentes"], DEZ["frias"]):
    add(f"<tr><td>{q1:02d}</td><td class='num'>{v1}</td><td>{q2:02d}</td><td class='num'>{v2}</td></tr>")
add("</tbody></table>")
add("<h3>Pares de dezenas que mais saíram juntos</h3><p class='note'>" +
    " · ".join(f"<code>{p['par']}</code> {p['freq']}x" for p in DEZ["pares_mais_frequentes"][:10]) +
    "</p>")

# perfil composto
add("<h2>9. Perfil composto mais provável</h2>")
add('<p class="note">Combinação dos padrões dominantes de cada tópico — o "retrato" mais '
    "aderente ao histórico dos últimos 100 concursos.</p>")
add("<table><thead><tr><th>Tópico</th><th>Padrão dominante</th></tr></thead><tbody>")
for k, rot in [("pares_impares", "Pares / ímpares"), ("baixas_altas", "Baixas / altas"),
               ("soma", "Soma"), ("repetidas", "Repetidas do anterior"),
               ("grupos", "Grupos (G1 / G2 / G3)"), ("grupos_ocupados", "Grupos ocupados"),
               ("sequencias", "Dezenas em sequência")]:
    add(f"<tr><td><b>{rot}</b></td><td>{C[k]}</td></tr>")
add("</tbody></table>")
add("""<div class="spoiler"><b>Como usar:</b> 4 pares / 3 ímpares · 3 baixas / 4 altas ·
soma 120–134 · 1 dezena repetida do concurso anterior · distribuição 3-2-2 entre os grupos ·
exatamente 1 dupla de dezenas consecutivas. Jogos que seguem esse perfil não têm mais chance
de acerto — apenas se parecem mais com o que a loteria efetivamente sorteia.</div>""")
add("""<div class="alert"><b>Limite estatístico:</b> toda combinação de 7 dezenas tem sempre
1 chance em 2.629.575. Os testes qui-quadrado desta análise <b>não rejeitaram a aleatoriedade</b>
em nenhum tópico (p &gt; 0,05 em todos; o mais próximo foi grupos, p = 0,055). Os padrões servem
para organizar e filtrar jogos, não para prever o resultado.</div>""")

# metodologia
add(f"""<h2>10. Metodologia</h2>
<ul class="note">
<li>Base: API oficial da Caixa (<code>servicebus2.caixa.gov.br/portaldeloterias/api/diadesorte</code>),
concursos {META['janela_concursos'][0]} a {META['janela_concursos'][1]}
({META['periodo'][0]} a {META['periodo'][1]}); espelho local em <code>data/dia-de-sorte.json</code>.</li>
<li>"Esperado (azar)" = distribuição <b>exata</b> obtida avaliando todas as
{n(META['combinacoes_possiveis'])} combinações possíveis de 7 dezenas — não é aproximação.</li>
<li>Aderência verificada por <b>qui-quadrado</b> com agrupamento de caudas raras (esperado &lt; 5),
significância de 5%.</li>
<li>Repetidas comparam cada concurso com o imediatamente anterior (o concurso
{META['janela_concursos'][0] - 1} entra apenas como referência).</li>
<li>Arquivos: <code>relatorio.html</code>, <code>relatorio.md</code>, <code>resultados/analise.json</code>,
<code>resultados/tab_*.csv</code>, <code>analise.py</code>, <code>fetch_caixa.py</code>.</li>
</ul>
<footer>Gerado em {META['periodo'][1]} · dados oficiais Loterias Caixa ·
análise descritiva/exploratória. Jogue com responsabilidade.
<span class="foot-note">18+ · loteria é entretenimento, não investimento.</span></footer>
</div></body></html>""")

(BASE / "relatorio.html").write_text("\n".join(h), encoding="utf-8")
print("ok:", (BASE / "relatorio.md").stat().st_size, (BASE / "relatorio.html").stat().st_size)
