#!/usr/bin/env python3
"""
Busca na base de teses do escritório (montada por montar_base.py).

Uso:
    python buscar_teses.py "horas extras intervalo" [--tipo inicial|contestacao] [--limite 10]
    python buscar_teses.py --mostrar t012 [--tipo ...]     texto literal da tese (versão mais recente e a anterior)
    python buscar_teses.py --pedidos "horas extras"         linhas de pedido do rol que mais se repetem
    python buscar_teses.py --listar                         todos os títulos, do mais usado ao menos usado
"""
import argparse
import json
import os
import re
import sys
import unicodedata
from pathlib import Path


def praxis_home():
    return Path(os.environ.get("PRAXIS_HOME") or Path.home() / ".claude" / "praxis")


def sem_acento(t):
    return unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()


def carregar(tipo, caminho=None):
    arq = Path(caminho) if caminho else praxis_home() / "teses" / tipo / "base-teses.json"
    if not arq.is_file():
        sys.exit(f"Base não encontrada em {arq}. Monte com montar_base.py (skill praxis:teses).")
    return json.loads(arq.read_text(encoding="utf-8"))


def texto(tese):
    return "\n".join(p["t"] for p in tese["vars"][0]["ps"])


def pontuar(tese, termos):
    titulo, corpo = sem_acento(tese["h"]), sem_acento(texto(tese))
    nota = 0
    for t in termos:
        if t in titulo:
            nota += 5
        nota += min(corpo.count(t), 5)
    return nota + (min(tese["n"], 20) / 20 if nota else 0)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("busca", nargs="?", default="")
    ap.add_argument("--tipo", choices=["inicial", "contestacao"], default="inicial")
    ap.add_argument("--base", help="caminho de um base-teses.json específico")
    ap.add_argument("--limite", type=int, default=10)
    ap.add_argument("--mostrar")
    ap.add_argument("--pedidos", action="store_true")
    ap.add_argument("--listar", action="store_true")
    a = ap.parse_args(argv)
    base = carregar(a.tipo, a.base)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if a.mostrar:
        tese = next((t for t in base["teses"] if t["id"] == a.mostrar), None)
        if not tese:
            sys.exit(f"Tese {a.mostrar} não existe.")
        print(f"# {tese['h']}  ({tese['id']}, usada em {tese['n']} petição(ões))\n")
        for i, v in enumerate(tese["vars"]):
            print(f"## Versão {i + 1}: {v['arq']}\n")
            for p in v["ps"]:
                print(("    " if p.get("q") else "") + p["t"] + "\n")
        return
    if a.listar:
        for t in base["teses"]:
            print(f"{t['id']}  {t['n']:>3}x  {'[preliminar] ' if t.get('pre') else ''}{t['h']}")
        return
    termos = [sem_acento(x) for x in re.findall(r"\w{3,}", a.busca)]
    if a.pedidos:
        achados = [p for p in base["pedidos"] if all(t in sem_acento(p["t"]) for t in termos)]
        for p in achados[: a.limite]:
            print(f"{p['n']:>3}x  {p['t']}")
        return
    if not termos:
        ap.error("informe o que buscar, ou use --listar")
    ranking = sorted(((pontuar(t, termos), t) for t in base["teses"]), key=lambda x: -x[0])
    ranking = [(n, t) for n, t in ranking if n > 0][: a.limite]
    if not ranking:
        print("Nada encontrado. Tente outras palavras ou --listar.")
    for n, t in ranking:
        trecho = re.sub(r"\s+", " ", texto(t))[:160]
        print(f"{t['id']}  {t['n']:>3}x  {t['h']}\n      {trecho}…")


if __name__ == "__main__":
    main()
