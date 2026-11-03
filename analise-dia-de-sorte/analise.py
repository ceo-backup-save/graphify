#!/usr/bin/env python3
"""
Análise estatística do Dia de Sorte (Loterias Caixa) — últimos 100 concursos.

Fonte primária : API oficial da Caixa (servicebus2.caixa.gov.br/portaldeloterias/api/diadesorte)
                 -> ver fetch_caixa.py para o coletor e a verificação concursо a concurso.
Base local     : data/dia-de-sorte.json (espelho idêntico ao retorno da API oficial,
                 conferido ponto a ponto contra servicebus2.caixa.gov.br).

Saídas:
  resultados/analise.json   -> todos os números da análise
  resultados/tab_*.csv      -> uma tabela por tópico
  relatorio.md              -> relatório em Markdown
  relatorio.html            -> relatório visual
"""
from __future__ import annotations

import csv
import json
import math
import statistics
from collections import Counter
from itertools import combinations
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE / "data" / "dia-de-sorte.json"
OUT = BASE / "resultados"
N_JANELA = 100


# --------------------------------------------------------------------------- #
# utilitários estatísticos (sem dependências externas)
# --------------------------------------------------------------------------- #
def _gser(a: float, x: float) -> float:
    ap, s = a, 1.0 / a
    delta = s
    for _ in range(2000):
        ap += 1
        delta *= x / ap
        s += delta
        if abs(delta) < abs(s) * 3e-16:
            break
    return s * math.exp(-x + a * math.log(x) - math.lgamma(a))


def _gcf(a: float, x: float) -> float:
    fpmin, b, c = 1e-300, x + 1 - a, 1e300
    d = 1.0 / b
    h = d
    for i in range(1, 2000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        if abs(d) < fpmin:
            d = fpmin
        c = b + an / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        de = d * c
        h *= de
        if abs(de - 1.0) < 3e-16:
            break
    return math.exp(-x + a * math.log(x) - math.lgamma(a)) * h


def chi2_sf(x: float, df: int) -> float:
    """P(X >= x) para uma qui-quadrado com df graus de liberdade."""
    if x <= 0:
        return 1.0
    a, xx = df / 2.0, x / 2.0
    return 1.0 - _gser(a, xx) if xx < a + 1 else _gcf(a, xx)


def chi2_teste(obs: dict, exp: dict) -> dict:
    """Qui-quadrado com agrupamento de caudas (categorias de esperado < 5)."""
    chaves = [k for k in obs if k in exp]
    if len(chaves) < 2:
        return {}
    # agrupa caudas raras num único balde para manter esperado >= 5
    raras = [k for k in chaves if exp[k] < 5]
    if len(raras) > 1 and len(raras) < len(chaves):
        resto = [k for k in chaves if k not in raras]
        obs = {**{k: obs[k] for k in resto}, "outras": sum(obs[k] for k in raras)}
        exp = {**{k: exp[k] for k in resto}, "outras": sum(exp[k] for k in raras)}
    chi = sum((obs[k] - exp[k]) ** 2 / exp[k] for k in obs if exp[k] > 0)
    df = len(obs) - 1
    p = chi2_sf(chi, df) if df > 0 else 1.0
    return {"qui2": chi, "gl": df, "p_valor": p,
            "significante_5pct": bool(p < 0.05),
            "interpretacao": ("desvio significativo ao nível de 5% "
                              "(o padrão observado difere do esperado por acaso)"
                              if p < 0.05 else
                              "sem desvio significativo ao nível de 5% "
                              "(compatível com aleatoriedade)")}


# --------------------------------------------------------------------------- #
# características de um jogo
# --------------------------------------------------------------------------- #
GRUPOS = ((1, 10), (11, 20), (21, 31))  # 01–10 | 11–20 | 21–31


def runs(nums: list[int]) -> list[int]:
    """Tamanhos das sequências (runs) de dezenas consecutivas."""
    out, tam = [], 1
    for a, b in zip(nums, nums[1:]):
        if b == a + 1:
            tam += 1
        else:
            if tam > 1:
                out.append(tam)
            tam = 1
    if tam > 1:
        out.append(tam)
    return out


def padrao_sequencia(nums: list[int]) -> str:
    r = runs(nums)
    if not r:
        return "Sem sequência"
    nomes = {2: "dupla", 3: "trio", 4: "quadra", 5: "quina", 6: "sena", 7: "sena+1"}
    cont = Counter(r)
    partes = []
    for tam in sorted(cont, reverse=True):
        n = cont[tam]
        nome = nomes.get(tam, f"{tam} seguidas")
        partes.append(f"{n} {nome}" if n == 1 else f"{n} {nome}s")
    return " + ".join(partes)


def perfil(nums: list[int]) -> dict:
    nums = sorted(nums)
    pares = sum(1 for n in nums if n % 2 == 0)
    baixas = sum(1 for n in nums if n <= 15)
    grupos = tuple(sum(1 for n in nums if lo <= n <= hi) for lo, hi in GRUPOS)
    r = runs(nums)
    return {
        "pares": pares, "impares": 7 - pares,
        "baixas": baixas, "altas": 7 - baixas,
        "soma": sum(nums),
        "grupos": grupos,
        "grupos_ocupados": sum(1 for g in grupos if g > 0),
        "runs": r,
        "padrao_seq": padrao_sequencia(nums),
        "max_run": max(r) if r else 0,
    }


# --------------------------------------------------------------------------- #
# distribuição teórica exata (todas as C(31,7) = 2.629.575 combinações)
# --------------------------------------------------------------------------- #
def distribuicao_teorica() -> dict:
    tot = Counter()
    n = 0
    for c in combinations(range(1, 32), 7):
        p = perfil(list(c))
        tot[("pares", p["pares"])] += 1
        tot[("baixas", p["baixas"])] += 1
        tot[("soma", p["soma"])] += 1
        tot[("grupos", p["grupos"])] += 1
        tot[("grupos_ocupados", p["grupos_ocupados"])] += 1
        tot[("padrao_seq", p["padrao_seq"])] += 1
        tot[("max_run", p["max_run"])] += 1
        n += 1
    # repetidas: segue hipergeométrica (7 dezenas do concurso anterior entre 31)
    for k in range(0, 8):
        tot[("repetidas", k)] = math.comb(7, k) * math.comb(24, 7 - k)
    return {"total": n, "contagens": tot}


# --------------------------------------------------------------------------- #
# montagem das tabelas
# --------------------------------------------------------------------------- #
def tabela(obs: Counter, teor: dict, prefixo: str, total_teorico: int,
           rotulo, ordem=None, n_obs: int = N_JANELA) -> list[dict]:
    linhas = []
    chaves = ordem if ordem is not None else sorted(obs, key=lambda k: (-obs[k], str(k)))
    for k in chaves:
        f = obs.get(k, 0)
        e = teor.get((prefixo, k), 0)
        pct_e = 100 * e / total_teorico if total_teorico else 0.0
        linhas.append({
            "padrao": rotulo(k),
            "chave": k if not isinstance(k, tuple) else list(k),
            "freq": f,
            "pct": round(100 * f / n_obs, 1),
            "esperado_freq": round(pct_e * n_obs / 100, 1),
            "esperado_pct": round(pct_e, 2),
            "desvio_pct": round(100 * f / n_obs - pct_e, 2),
        })
    linhas.sort(key=lambda r: (-r["freq"], r["padrao"]))
    for i, r in enumerate(linhas, 1):
        r["rank"] = i
    return linhas


def exp_dict(teor: dict, prefixo: str, total: int, n: int = N_JANELA) -> dict:
    return {k: c / total * n for (p, k), c in teor.items() if p == prefixo}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    historico = json.loads(DATA.read_text())
    historico.sort(key=lambda d: d["concurso"])
    por_concurso = {d["concurso"]: d for d in historico}

    ultimo = historico[-1]["concurso"]
    primeiro = ultimo - N_JANELA + 1
    janela = [d for d in historico if primeiro <= d["concurso"] <= ultimo]
    assert len(janela) == N_JANELA, f"janela com {len(janela)} concursos"

    # ---------------- coleta das características ----------------
    obs = {k: Counter() for k in
           ("pares", "baixas", "soma", "grupos", "grupos_ocupados", "padrao_seq",
            "max_run", "repetidas")}
    somas, dezenas, repetidas_lista = [], Counter(), []
    registros = []

    for d in janela:
        nums = sorted(int(x) for x in d["resultado"])
        p = perfil(nums)
        anterior = por_concurso.get(d["concurso"] - 1)
        rep = len(set(nums) & {int(x) for x in anterior["resultado"]}) if anterior else None

        obs["pares"][p["pares"]] += 1
        obs["baixas"][p["baixas"]] += 1
        obs["soma"][p["soma"]] += 1
        obs["grupos"][p["grupos"]] += 1
        obs["grupos_ocupados"][p["grupos_ocupados"]] += 1
        obs["padrao_seq"][p["padrao_seq"]] += 1
        obs["max_run"][p["max_run"]] += 1
        if rep is not None:
            obs["repetidas"][rep] += 1
            repetidas_lista.append(rep)

        somas.append(p["soma"])
        dezenas.update(nums)
        registros.append({
            "concurso": d["concurso"], "data": d["data"],
            "dezenas": nums, "pares": p["pares"], "impares": p["impares"],
            "baixas": p["baixas"], "altas": p["altas"], "soma": p["soma"],
            "grupos": list(p["grupos"]), "repetidas_anterior": rep,
            "padrao_sequencia": p["padrao_seq"], "maior_sequencia": p["max_run"],
            "runs": p["runs"],
        })

    teor = distribuicao_teorica()

    # ---------------- tópico 1: pares / ímpares ----------------
    rot_pi = lambda k: (f"{k} {'par' if k == 1 else 'pares'} / "
                        f"{7 - k} {'ímpar' if 7 - k == 1 else 'ímpares'}")
    linhas_pi = tabela(obs["pares"], teor["contagens"], "pares", teor["total"], rot_pi,
                       ordem=list(range(8)))
    tot_pares_dez = sum(r["freq"] * r["chave"] for r in linhas_pi)
    tot_impares_dez = sum(r["freq"] * (7 - r["chave"]) for r in linhas_pi)
    chi_pi = chi2_teste({k: obs["pares"][k] for k in range(8)},
                        exp_dict(teor["contagens"], "pares", teor["total"]))

    # ---------------- tópico 2: baixas / altas ----------------
    rot_ba = lambda k: (f"{k} {'baixa' if k == 1 else 'baixas'} / "
                        f"{7 - k} {'alta' if 7 - k == 1 else 'altas'}")
    linhas_ba = tabela(obs["baixas"], teor["contagens"], "baixas", teor["total"], rot_ba,
                       ordem=list(range(8)))
    tot_baixas_dez = sum(r["freq"] * r["chave"] for r in linhas_ba)
    chi_ba = chi2_teste({k: obs["baixas"][k] for k in range(8)},
                        exp_dict(teor["contagens"], "baixas", teor["total"]))

    # ---------------- tópico 3: soma ----------------
    FAIXAS_SOMA = [(28, 44), (45, 59), (60, 74), (75, 89), (90, 104), (105, 119),
                   (120, 134), (135, 149), (150, 164), (165, 179), (180, 196)]
    faixa_de = lambda s: next(f"{a}–{b}" for a, b in FAIXAS_SOMA if a <= s <= b)
    obs_faixa = Counter(faixa_de(s) for s in somas)
    teor_faixa = Counter()
    for s, c in teor["contagens"].items():
        if s[0] == "soma":
            teor_faixa[faixa_de(s[1])] += c
    ordem_faixa = [f"{a}–{b}" for a, b in FAIXAS_SOMA]
    linhas_soma = tabela(obs_faixa, {("soma_faixa", k): v for k, v in teor_faixa.items()},
                         "soma_faixa", teor["total"], lambda k: k, ordem=ordem_faixa)
    chi_soma = chi2_teste({k: obs_faixa[k] for k in ordem_faixa},
                          {k: teor_faixa[k] / teor["total"] * N_JANELA for k in ordem_faixa})
    soma_stats = {
        "media": round(statistics.mean(somas), 2),
        "mediana": statistics.median(somas),
        "desvio_padrao": round(statistics.pstdev(somas), 2),
        "minimo": min(somas), "maximo": max(somas),
        "moda": sorted(obs["soma"].items(), key=lambda kv: -kv[1])[0],
        "p25": round(statistics.quantiles(somas, n=4)[0], 1),
        "p75": round(statistics.quantiles(somas, n=4)[2], 1),
        "media_teorica": round(7 * 16, 1),  # média de 7 dezenas de 1..31 = 7 * 16
        "faixa_1sigma": [round(statistics.mean(somas) - statistics.pstdev(somas), 1),
                         round(statistics.mean(somas) + statistics.pstdev(somas), 1)],
    }
    # somas observadas dentro do intervalo central teórico (95% da distribuição)
    teor_somas = sorted((s[1], c) for s, c in teor["contagens"].items() if s[0] == "soma")
    acum, lo95, hi95 = 0, None, None
    for s, c in teor_somas:
        acum += c
        if lo95 is None and acum >= 0.025 * teor["total"]:
            lo95 = s
        if hi95 is None and acum >= 0.975 * teor["total"]:
            hi95 = s
    dentro95 = sum(1 for s in somas if lo95 <= s <= hi95)
    soma_stats["faixa_95pct_teorica"] = [lo95, hi95]
    soma_stats["obs_dentro_95pct"] = dentro95
    top_somas = [{"soma": s, "freq": c, "pct": round(100 * c / N_JANELA, 1)}
                 for s, c in sorted(obs["soma"].items(), key=lambda kv: (-kv[1], kv[0]))[:10]]

    # ---------------- tópico 4: repetidas do concurso anterior ----------------
    rot_rep = lambda k: ("nenhuma repetida" if k == 0 else
                         f"{k} repetida" if k == 1 else f"{k} repetidas")
    linhas_rep = tabela(obs["repetidas"], teor["contagens"], "repetidas", teor["total"],
                        rot_rep, ordem=list(range(8)))
    chi_rep = chi2_teste({k: obs["repetidas"][k] for k in range(8)},
                         exp_dict(teor["contagens"], "repetidas", teor["total"]))
    rep_stats = {
        "media": round(statistics.mean(repetidas_lista), 2),
        "mediana": statistics.median(repetidas_lista),
        "esperado_teorico": round(7 * 7 / 31, 2),
        "total_dezenas_repetidas": sum(repetidas_lista),
        "max": max(repetidas_lista), "min": min(repetidas_lista),
        "desvio_padrao": round(statistics.pstdev(repetidas_lista), 2),
    }

    # ---------------- tópico 5: grupos (faixas) em sequência ----------------
    rot_gr = lambda k: f"{k[0]} no G1 (01–10) / {k[1]} no G2 (11–20) / {k[2]} no G3 (21–31)"
    linhas_gr = tabela(obs["grupos"], teor["contagens"], "grupos", teor["total"], rot_gr)
    chi_gr = chi2_teste({k: obs["grupos"][k] for k in obs["grupos"]},
                         exp_dict(teor["contagens"], "grupos", teor["total"]))
    rot_oc = lambda k: (f"{k} grupo ocupado" if k == 1 else f"{k} grupos ocupados")
    linhas_oc = tabela(obs["grupos_ocupados"], teor["contagens"], "grupos_ocupados",
                       teor["total"], rot_oc, ordem=[1, 2, 3])
    # grupos contíguos ocupados (G1+G2, G2+G3, os três…) — leitura "em sequência"
    obs_cont = Counter()
    for d in janela:
        nums = sorted(int(x) for x in d["resultado"])
        g = [sum(1 for n in nums if lo <= n <= hi) for lo, hi in GRUPOS]
        ocup = "".join("1" if x else "0" for x in g)
        obs_cont[{"111": "G1+G2+G3 (todos)", "110": "G1+G2 (sem G3)",
                  "011": "G2+G3 (sem G1)", "101": "G1+G3 (sem G2)",
                  "100": "só G1", "010": "só G2", "001": "só G3"}[ocup]] += 1
    mapa_cont = {"111": "G1+G2+G3 (todos)", "110": "G1+G2 (sem G3)",
                 "011": "G2+G3 (sem G1)", "101": "G1+G3 (sem G2)",
                 "100": "só G1", "010": "só G2", "001": "só G3"}
    teor_cont = Counter()
    for (pref, chave), c in teor["contagens"].items():
        if pref == "grupos":
            teor_cont[mapa_cont["".join("1" if x else "0" for x in chave)]] += c
    ordem_cont = ["G1+G2+G3 (todos)", "G1+G2 (sem G3)", "G2+G3 (sem G1)",
                  "G1+G3 (sem G2)", "só G1", "só G2", "só G3"]
    linhas_cont = tabela(obs_cont, {("cont", k): v for k, v in teor_cont.items()},
                         "cont", teor["total"], lambda k: k, ordem=ordem_cont)
    chi_cont = chi2_teste({k: obs_cont[k] for k in ordem_cont},
                          {k: teor_cont[k] / teor["total"] * N_JANELA for k in ordem_cont})
    grupos_media = [round(statistics.mean(r["grupos"][i] for r in registros), 2) for i in range(3)]
    grupos_esperado = [round(7 * 10 / 31, 2), round(7 * 10 / 31, 2), round(7 * 11 / 31, 2)]

    # ---------------- tópico 6: dezenas em sequência ----------------
    linhas_seq = tabela(obs["padrao_seq"], teor["contagens"], "padrao_seq", teor["total"],
                        lambda k: k)
    chi_seq = chi2_teste({k: obs["padrao_seq"][k] for k in obs["padrao_seq"]},
                          exp_dict(teor["contagens"], "padrao_seq", teor["total"]))
    rot_max = lambda k: ({0: "sem sequência", 2: "dupla (2 seguidas)",
                          3: "trio (3 seguidas)", 4: "quadra (4 seguidas)",
                          5: "quina (5 seguidas)", 6: "sena (6 seguidas)",
                          7: "7 seguidas"}.get(k, f"{k} seguidas"))
    linhas_max = tabela(obs["max_run"], teor["contagens"], "max_run", teor["total"],
                        rot_max, ordem=[0, 2, 3, 4, 5, 6, 7])
    chi_max = chi2_teste({k: obs["max_run"][k] for k in obs["max_run"]},
                          exp_dict(teor["contagens"], "max_run", teor["total"]))
    tem_alguma = N_JANELA - obs["max_run"][0]
    seq_stats = {
        "com_alguma_sequencia": tem_alguma,
        "pct_com_alguma_sequencia": round(100 * tem_alguma / N_JANELA, 1),
        "media_runs": round(statistics.mean(len(r["runs"]) for r in registros), 2),
        "esperado_pct_com_alguma": round(
            100 * (teor["total"] - teor["contagens"][("max_run", 0)]) / teor["total"], 1),
    }

    # ---------------- dezenas: frequência, quentes/frias, pares ----------------
    freq_dez = {d: dezenas.get(d, 0) for d in range(1, 32)}
    esperado_dez = round(N_JANELA * 7 / 31, 1)
    quentes = sorted(freq_dez.items(), key=lambda kv: (-kv[1], kv[0]))[:7]
    frias = sorted(freq_dez.items(), key=lambda kv: (kv[1], kv[0]))[:7]
    pares_c = Counter()
    for r in registros:
        for a, b in combinations(r["dezenas"], 2):
            pares_c[(a, b)] += 1
    top_pares = [{"par": f"{a:02d}-{b:02d}", "freq": c}
                 for (a, b), c in sorted(pares_c.items(), key=lambda kv: (-kv[1], kv[0]))[:10]]
    atraso = {}
    for d in range(1, 32):
        atraso[d] = next((i for i, r in enumerate(reversed(registros)) if d in r["dezenas"]),
                         N_JANELA)

    # ---------------- padrão composto do próximo concurso ----------------
    def moda(linhas):
        return max(linhas, key=lambda r: r["freq"])

    composto = {
        "pares_impares": moda(linhas_pi)["padrao"],
        "baixas_altas": moda(linhas_ba)["padrao"],
        "soma": moda([r for r in linhas_soma])["padrao"],
        "repetidas": moda(linhas_rep)["padrao"],
        "grupos": moda(linhas_gr)["padrao"],
        "grupos_ocupados": moda(linhas_oc)["padrao"],
        "sequencias": moda(linhas_seq)["padrao"],
    }

    analise = {
        "meta": {
            "jogo": "Dia de Sorte",
            "fonte": "API oficial Loterias Caixa — servicebus2.caixa.gov.br/portaldeloterias/api/diadesorte",
            "espelho_local": "data/dia-de-sorte.json",
            "janela_concursos": [primeiro, ultimo],
            "periodo": [janela[0]["data"], janela[-1]["data"]],
            "n_concursos": len(janela),
            "universo": "31 dezenas (01–31), 7 sorteadas por concurso",
            "combinacoes_possiveis": teor["total"],
            "concursos_no_historico": len(historico),
        },
        "definicoes": {
            "pares": "dezenas pares entre as 7 sorteadas (universo tem 15 pares e 16 ímpares)",
            "baixas": "dezenas de 01 a 15 (baixas) x 16 a 31 (altas) — 15 baixas e 16 altas no universo",
            "soma": "soma aritmética das 7 dezenas sorteadas",
            "repetidas": "dezenas do concurso N que também saíram no concurso N-1",
            "grupos": "faixas fixas G1 = 01–10 (10 dezenas), G2 = 11–20 (10), G3 = 21–31 (11)",
            "sequencias": "dezenas consecutivas dentro do mesmo jogo (ex.: 12-13 = dupla; 05-06-07 = trio)",
        },
        "topicos": {
            "pares_impares": {"linhas": linhas_pi, "qui2": chi_pi,
                              "total_dezenas_pares": tot_pares_dez,
                              "total_dezenas_impares": tot_impares_dez},
            "baixas_altas": {"linhas": linhas_ba, "qui2": chi_ba,
                             "total_dezenas_baixas": tot_baixas_dez,
                             "total_dezenas_altas": N_JANELA * 7 - tot_baixas_dez},
            "soma": {"faixas": linhas_soma, "estatisticas": soma_stats,
                     "top_somas": top_somas, "qui2": chi_soma},
            "repetidas": {"linhas": linhas_rep, "estatisticas": rep_stats, "qui2": chi_rep},
            "grupos": {"padroes": linhas_gr, "ocupacao": linhas_oc,
                       "contiguos": linhas_cont, "qui2": chi_gr,
                       "qui2_contiguos": chi_cont,
                       "media_por_grupo": grupos_media, "esperado_por_grupo": grupos_esperado},
            "sequencias": {"padroes": linhas_seq, "maior_sequencia": linhas_max,
                           "estatisticas": seq_stats, "qui2": chi_seq,
                           "qui2_maior_seq": chi_max},
        },
        "dezenas": {"frequencia": freq_dez, "esperado": esperado_dez,
                    "quentes": quentes, "frias": frias, "atraso": atraso,
                    "pares_mais_frequentes": top_pares},
        "padrao_composto": composto,
        "registros": registros,
    }

    (OUT / "analise.json").write_text(json.dumps(analise, ensure_ascii=False, indent=2))

    # ---------------- CSVs ----------------
    def csv_out(nome, linhas, cols):
        with (OUT / nome).open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            for r in linhas:
                w.writerow(r)

    csv_out("tab_1_pares_impares.csv", linhas_pi,
            ["rank", "padrao", "freq", "pct", "esperado_pct", "desvio_pct"])
    csv_out("tab_2_baixas_altas.csv", linhas_ba,
            ["rank", "padrao", "freq", "pct", "esperado_pct", "desvio_pct"])
    csv_out("tab_3_soma_faixas.csv", linhas_soma,
            ["rank", "padrao", "freq", "pct", "esperado_pct", "desvio_pct"])
    csv_out("tab_4_repetidas.csv", linhas_rep,
            ["rank", "padrao", "freq", "pct", "esperado_pct", "desvio_pct"])
    csv_out("tab_5_grupos.csv", linhas_gr,
            ["rank", "padrao", "freq", "pct", "esperado_pct", "desvio_pct"])
    csv_out("tab_6_sequencias.csv", linhas_seq,
            ["rank", "padrao", "freq", "pct", "esperado_pct", "desvio_pct"])
    csv_out("tab_concursos.csv", registros,
            ["concurso", "data", "dezenas", "pares", "impares", "baixas", "altas",
             "soma", "grupos", "repetidas_anterior", "padrao_sequencia", "maior_sequencia"])

    print(json.dumps({"meta": analise["meta"],
                      "padrao_composto": composto}, ensure_ascii=False, indent=2))
    for nome, bloco, chave in (
        ("PARES/ÍMPARES", linhas_pi, None),
        ("BAIXAS/ALTAS", linhas_ba, None),
        ("SOMA (faixas)", linhas_soma, None),
        ("REPETIDAS", linhas_rep, None),
        ("GRUPOS", linhas_gr, None),
        ("SEQUÊNCIAS", linhas_seq, None),
    ):
        print(f"\n--- {nome} ---")
        for r in bloco[:8]:
            print(f"{r['rank']:>2}. {r['padrao']:<62} {r['freq']:>3}  "
                  f"{r['pct']:>5}%  esp {r['esperado_pct']:>5}%  desvio {r['desvio_pct']:+.1f}")
    print("\n--- OCUPAÇÃO DE GRUPOS ---")
    for r in linhas_oc:
        print(f"{r['rank']}. {r['padrao']:<28} {r['freq']:>3} {r['pct']:>5}%")
    print("\n--- CONTÍGUOS ---")
    for r in linhas_cont:
        print(f"{r['rank']}. {r['padrao']:<24} {r['freq']:>3} {r['pct']:>5}%")
    print("\n--- MAIOR SEQUÊNCIA ---")
    for r in linhas_max:
        print(f"{r['rank']}. {r['padrao']:<24} {r['freq']:>3} {r['pct']:>5}%")
    print("\nSOMA:", soma_stats)
    print("REPETIDAS:", rep_stats)
    print("SEQ:", seq_stats)
    print("QUI2:", json.dumps({"pares": chi_pi, "baixas": chi_ba,
                                "soma": chi_soma, "rep": chi_rep, "grupos": chi_gr,
                                "seq": chi_seq, "max": chi_max},
                               ensure_ascii=False, indent=1))
    print("QUENTES:", quentes)
    print("FRIAS:", frias)
    print("TOP PARES:", top_pares[:5])


if __name__ == "__main__":
    main()
