#!/usr/bin/env python3
"""
Coletor dos resultados oficiais do Dia de Sorte — API Loterias Caixa.

Endpoint oficial (JSON público):
    https://servicebus2.caixa.gov.br/portaldeloterias/api/diadesorte
    https://servicebus2.caixa.gov.br/portaldeloterias/api/diadesorte/<concurso>

Uso:
    python3 fetch_caixa.py                 # baixa o histórico completo (1..último)
    python3 fetch_caixa.py --ultimos 100   # baixa só os 100 últimos concursos
    python3 fetch_caixa.py --verificar     # confere o espelho local contra a API

Observação: a API da Caixa pode bloquear requisições de IPs de datacenter
(alguns ambientes só alcançam o endpoint por navegador/proxy). Nesse caso, use
`--verificar` a partir de uma máquina com acesso e compare com o espelho local.
"""
from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent
DESTINO = BASE / "data" / "dia-de-sorte.json"
URL = "https://servicebus2.caixa.gov.br/portaldeloterias/api/diadesorte"
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"),
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://loterias.caixa.gov.br/Paginas/Dia-de-Sorte.aspx",
}


def buscar(concurso: int | None = None, tentativas: int = 3) -> dict:
    url = URL if concurso is None else f"{URL}/{concurso}"
    for i in range(tentativas):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            if i == tentativas - 1:
                raise SystemExit(f"falha ao consultar {url}: {exc}")
            time.sleep(2 * (i + 1))
    raise AssertionError("inalcançável")


def normalizar(bruto: dict) -> dict:
    return {
        "concurso": bruto["numero"],
        "data": bruto["dataApuracao"],
        "resultado": list(bruto["listaDezenas"]),
        "mes_da_sorte": bruto.get("nomeTimeCoracaoMesSorte"),
        "proximo_concurso": bruto.get("numeroConcursoProximo"),
        "valor_estimado_proximo": bruto.get("valorEstimadoProximoConcurso"),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ultimos", type=int, default=0,
                    help="baixa apenas os N concursos mais recentes")
    ap.add_argument("--verificar", action="store_true",
                    help="confere o espelho local contra a API oficial")
    args = ap.parse_args()

    if args.verificar:
        local = {d["concurso"]: d for d in json.loads(DESTINO.read_text())}
        ultimo = buscar()["numero"]
        alvos = [ultimo, ultimo - 1, 1238, max(1, ultimo - 99)]
        for c in sorted(set(alvos)):
            api = normalizar(buscar(c))
            ok = sorted(api["resultado"]) == sorted(local[c]["resultado"])
            print(f"concurso {c}: {'OK' if ok else 'DIVERGENTE'} "
                  f"| api={sorted(api['resultado'])} local={sorted(local[c]['resultado'])}")
        return

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    ultimo = buscar()["numero"]
    primeiro = max(1, ultimo - args.ultimos + 1) if args.ultimos else 1
    print(f"baixando concursos {primeiro}..{ultimo}")
    dados = []
    for c in range(primeiro, ultimo + 1):
        dados.append(normalizar(buscar(c)))
        if c % 25 == 0:
            print(f"  {c}/{ultimo}")
        time.sleep(0.15)
    DESTINO.write_text(json.dumps(dados, ensure_ascii=False, indent=0))
    print(f"ok: {len(dados)} concursos em {DESTINO}")


if __name__ == "__main__":
    main()
