#!/usr/bin/env python3
"""
Conferência mecânica de uma minuta antes de gerar o Word.

Uso:
    python conferir.py conteudo.json --peca inicial|contestacao|replica|crro|ro [--json]

Lê o mesmo conteudo.json que a skill minuta:documento usa e aponta:
    ERRO   o que impede a entrega (travessão, primeira pessoa, negrito aberto, "Súm.", "fls." onde é proibido,
           marcador de pendência no RO)
    AVISO  o que o advogado precisa ver (pendências, tópico sem pedido em negrito, marcadores do perfil sem
           preencher, parágrafo longo, hora no formato 7:30, "(a)" fora de "Relator(a)")

Sai com código 1 se houver ERRO. Não substitui a leitura: confere forma, não conteúdo jurídico.
"""
import argparse
import json
import re
import sys
import unicodedata

PECAS = ("inicial", "contestacao", "replica", "crro", "ro")

# "nós" só com acento: "nos" sem acento é contração ("nos termos do art. 59").
PRIMEIRA_PESSOA = re.compile(r"\b(nós|entendemos|requeremos|pedimos|pleiteamos|impugnamos|nossa|nosso|nossas|nossos)\b",
                             re.I)
SUM_ABREV = re.compile(r"\bS[úu]m\.\s*\d")
FOLHAS = re.compile(r"\b(fls?\.|folhas?)\s*\d", re.I)
PENDENCIA = re.compile(r"\[(PENDENTE|CONFIRMAR[^\]]*|DATA)[^\]]*\]|\((INSERIR JURISPRUD[ÊE]NCIA|SUGEST[ÃA]O DE TESE)[^)]*\)")
PERFIL = re.compile(r"\[(ADVOGADO|OAB|CIDADE|UF|HONOR[ÁA]RIOS)\]")
HORA_DOIS_PONTOS = re.compile(r"(?<![\w:/.])\d{1,2}:\d{2}(?![\w:])")
GENERO_A = re.compile(r"\w\(a\)", re.I)

# Títulos que organizam a peça e não são tópicos com pedido.
ESTRUTURAIS = re.compile(
    r"^(AO JU[IÍ]ZO|EXCELENT|RECLAMA[CÇ][AÃ]O TRABALHISTA|CONTESTA[CÇ][AÃ]O|R[EÉ]PLICA|CONTRARRAZ|RAZ[OÕ]ES|"
    r"PRELIMINARMENTE|NO M[EÉ]RITO|DO M[EÉ]RITO|DOS PEDIDOS|DO PEDIDO|DOS REQUERIMENTOS|DA CONCLUS|DA S[IÍ]NTESE|"
    r"SINOPSE|DOS FATOS|DO CONTRATO|DA COMPET[EÊ]NCIA|DA IMPUGNA[CÇ][AÃ]O AOS PEDIDOS|DA IMPUGNA[CÇ][AÃ]O AOS DOCUMENTOS|"
    r"DA IMPUGNA[CÇ][AÃ]O DOS DOCUMENTOS|DAS PRELIMINARES|ADMISS[AÃ]O|DA TEMPESTIVIDADE|RECORRENTE|PROCESSO)", re.I)


def textos(bloco):
    if "runs" in bloco:
        return "".join(r.get("text", "") for r in bloco["runs"])
    return bloco.get("text", "")


def tem_negrito(bloco):
    if "runs" in bloco:
        return any(r.get("bold") for r in bloco["runs"]) or "**" in textos(bloco)
    return "**" in bloco.get("text", "") or bool(bloco.get("bold"))


def conferir(blocos, peca):
    erros, avisos = [], []
    corpo = [b for b in blocos if b.get("type") not in ("config", "spacer")]

    for i, b in enumerate(corpo):
        t = textos(b)
        juris = b.get("type") in ("jurisprudencia", "jurisprudência")
        onde = f"bloco {i + 1}"
        if "—" in t:
            erros.append(f"{onde}: travessão (—)")
        if t.count("**") % 2 or t.count("[[") != t.count("]]"):
            erros.append(f"{onde}: negrito aberto (** ou [[ ]])")
        if juris:
            continue  # transcrição: não se mexe no texto do julgado
        m = PRIMEIRA_PESSOA.search(t)
        if m:
            erros.append(f"{onde}: primeira pessoa ('{m.group(0)}'); use a terceira pessoa")
        if SUM_ABREV.search(t):
            erros.append(f"{onde}: 'Súm.' abreviado; escreva 'Súmula' (o negrito automático não reconhece)")
        if peca in ("replica", "crro", "ro") and FOLHAS.search(t):
            erros.append(f"{onde}: cita folhas; nesta peça cite o Id do PJe")
        for p in PENDENCIA.finditer(t):
            if peca == "ro":
                erros.append(f"{onde}: marcador no RO ({p.group(0)[:60]}); o que não se confirma sai da peça")
            else:
                avisos.append(f"{onde}: pendência {p.group(0)[:80]}")
        for p in set(PERFIL.findall(t)):
            avisos.append(f"{onde}: [{p}] sem preencher (dado do perfil)")
        if HORA_DOIS_PONTOS.search(t) and b.get("type") != "heading":
            avisos.append(f"{onde}: hora no formato '{HORA_DOIS_PONTOS.search(t).group(0)}'; o padrão é 7h30")
        if GENERO_A.search(t) and "relator(a)" not in t.lower():
            avisos.append(f"{onde}: '(a)' para gênero; resolva o gênero")
        palavras = len(t.split())
        limite = 180 if peca in ("replica", "ro") else 250
        if b.get("type") == "paragraph" and palavras > limite:
            avisos.append(f"{onde}: parágrafo com {palavras} palavras; divida se for texto novo")

    # Cada tópico de mérito termina num parágrafo com o pedido em negrito.
    atual, paragrafos = None, []

    def fechar():
        if atual and paragrafos and not ESTRUTURAIS.match(atual.strip()):
            if not tem_negrito(paragrafos[-1]):
                avisos.append(f"tópico '{atual[:60]}': o último parágrafo não tem pedido em negrito")

    for b in corpo:
        if b.get("type") == "heading" and b.get("align", "center") != "center":
            fechar()
            atual, paragrafos = textos(b), []
        elif b.get("type") == "paragraph" and atual is not None:
            paragrafos.append(b)
    fechar()

    titulos = [unicodedata.normalize("NFKD", textos(b)).encode("ascii", "ignore").decode().upper()
               for b in corpo if b.get("type") == "heading"]
    if peca == "inicial" and not any(t.startswith(("DOS PEDIDOS", "DO PEDIDO")) for t in titulos):
        erros.append("inicial sem o tópico DOS PEDIDOS (rol)")
    if peca == "contestacao" and any(t.startswith("DOS PEDIDOS") for t in titulos):
        avisos.append("contestação com DOS PEDIDOS; contestação não tem rol")
    return erros, avisos


def main(argv=None):
    ap = argparse.ArgumentParser(description="Confere a forma de uma minuta (conteudo.json).")
    ap.add_argument("conteudo")
    ap.add_argument("--peca", choices=PECAS, required=True)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    with open(a.conteudo, encoding="utf-8") as f:
        blocos = json.load(f)
    erros, avisos = conferir(blocos, a.peca)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if a.json:
        print(json.dumps({"erros": erros, "avisos": avisos}, ensure_ascii=False, indent=1))
    else:
        for e in erros:
            print("ERRO  ", e)
        for v in avisos:
            print("AVISO ", v)
        print(f"{len(erros)} erro(s), {len(avisos)} aviso(s)")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
