#!/usr/bin/env python3
"""
Gera um .docx sobre o TIMBRADO DO PRÓPRIO ESCRITÓRIO, com a formatação de peça trabalhista.

Uso:
    python gerar_docx.py conteudo.json saida.docx [--timbrado caminho.docx] [--perfil caminho.md]
    python gerar_docx.py --testar saida.docx [--timbrado caminho.docx]   (página de teste do timbrado)

De onde vem o timbrado, nesta ordem:
    1. --timbrado
    2. campo "timbrado:" no topo do perfil (~/.claude/praxis/perfil.md)
    3. ~/.claude/praxis/timbrado.docx
    4. nenhum: folha em branco, com as margens do perfil
A pasta ~/.claude/praxis pode ser trocada pela variável de ambiente PRAXIS_HOME.

O timbrado é um .docx comum do escritório, com logo e dados no cabeçalho e no rodapé. O corpo dele é apagado; cabeçalho,
rodapé, margens e numeração de página ficam como estão.

Formatação (campos opcionais no topo do perfil; entre parênteses, o padrão):
    fonte (Times New Roman), tamanho (12), tamanho_jurisprudencia (10), entrelinha (1.2), recuo_cm (2.5),
    margens_cm (3 2 2 3: superior direita inferior esquerda, só sem timbrado)

Formato do conteudo.json: references/formato-do-conteudo.md.
Requisito: python-docx (pip install python-docx).
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt
except ImportError:
    sys.exit("Instale o python-docx: pip install python-docx")


# ---------------------------------------------------------------------------
# Perfil do escritório
# ---------------------------------------------------------------------------
def praxis_home():
    return Path(os.environ.get("PRAXIS_HOME") or Path.home() / ".claude" / "praxis")


def ler_perfil(caminho=None):
    """Lê os campos 'chave: valor' do bloco entre '---' no topo do perfil. Sem perfil, devolve {}."""
    caminho = Path(caminho) if caminho else praxis_home() / "perfil.md"
    if not caminho.is_file():
        return {}
    linhas = caminho.read_text(encoding="utf-8").splitlines()
    if not linhas or linhas[0].strip() != "---":
        return {}
    campos = {}
    for linha in linhas[1:]:
        if linha.strip() == "---":
            break
        m = re.match(r"^\s*([A-Za-z_]+)\s*:\s*(.*?)\s*$", linha)
        if m and not linha.lstrip().startswith("#"):
            valor = m.group(2)
            if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in "\"'":
                valor = valor[1:-1]
            campos[m.group(1).lower()] = valor
    return campos


def numero(campos, chave, padrao):
    try:
        return float(str(campos.get(chave, "")).replace(",", "."))
    except ValueError:
        return padrao


class Formato:
    def __init__(self, campos):
        self.fonte = campos.get("fonte") or "Times New Roman"
        self.tamanho = numero(campos, "tamanho", 12)
        self.tamanho_juris = numero(campos, "tamanho_jurisprudencia", 10)
        self.entrelinha = numero(campos, "entrelinha", 1.2)
        self.recuo = Cm(numero(campos, "recuo_cm", 2.5))
        partes = (campos.get("margens_cm") or "3 2 2 3").replace(",", ".").split()
        try:
            self.margens = [float(x) for x in partes] if len(partes) == 4 else [3, 2, 2, 3]
        except ValueError:
            self.margens = [3, 2, 2, 3]


def achar_timbrado(arg, campos):
    if arg:
        return Path(arg)
    if campos.get("timbrado"):
        return Path(os.path.expanduser(campos["timbrado"]))
    padrao = praxis_home() / "timbrado.docx"
    return padrao if padrao.is_file() else None


# ---------------------------------------------------------------------------
# Regras fixas
# ---------------------------------------------------------------------------
PROIBIDOS = ["—"]  # travessão


def conferir_proibidos(blocos):
    problemas = []
    for i, bloco in enumerate(blocos):
        textos = [bloco.get("text", "")] + [r.get("text", "") for r in bloco.get("runs", [])]
        for t in textos:
            for ch in PROIBIDOS:
                if ch in t:
                    problemas.append(f"  - bloco {i}: {t!r}")
    if problemas:
        raise ValueError("Travessão '—' não é permitido. Reescreva com vírgula, ponto, dois-pontos ou parênteses:\n"
                         + "\n".join(problemas))


# ---------------------------------------------------------------------------
# Negrito e itálico automáticos
# ---------------------------------------------------------------------------
MONEY_RE = (r"R\$\s?\d+(?:\.\d{3})*(?:,\d{1,2})?"
            r"(?:\s*\([^()]*(?:reais|real|centavos?)[^()]*\))?")
HOURS_RE = (r"(?<![\w/.,])\d+(?:[.,]\d+)?\s?(?:horas?|minutos?|min)(?!\w)"
            r"|(?<![\w/.,:])\d{1,2}h(?:\d{2})?(?!\w)"
            r"|(?<![\w:])\d{1,2}:\d{2}(?!\w)")
_MESES = "janeiro|fevereiro|mar[çc]o|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro"
DATE_RE = (r"(?<![\w/.])\d{1,2}[/.]\d{1,2}[/.]\d{2,4}(?![\w/])"
           rf"|(?<!\w)\d{{1,2}}[º°]?\s+de\s+(?:{_MESES})(?:\s+de\s+\d{{4}})?(?!\w)"
           rf"|(?<!\w)(?:{_MESES})\s+de\s+\d{{4}}(?!\w)")
_NUM = r"(?:n[ºo°.]{0,2}\s*)?\d"
SUMULA_TRIGGER = (
    rf"S[úu]mulas?\s+(?:Vinculantes?\s+)?{_NUM}"
    rf"|Temas?\s+(?:Repetitivos?\s+|de\s+Repercuss[ãa]o\s+Geral\s+)?{_NUM}"
    rf"|(?:OJs?|Orienta[çc](?:[ãa]o|[õo]es)\s+Jurisprudenci(?:al|ais))"
    rf"(?:\s+(?:da|do)\s+[A-Za-z0-9-]+)?\s+{_NUM}"
)
_ABREV = ["art", "arts", "n", "c", "e", "min", "des", "rel", "inc", "al", "ex", "p", "pp",
          "fls", "fl", "sr", "sra", "dr", "dra", "cf", "v", "obs", "ss", "res", "proc"]
SENTENCE_END = "".join(rf"(?<!\b{a})" for a in _ABREV) + r"\.(?=\s|$)"
SUMULA_RE = rf"(?<!\w)(?:{SUMULA_TRIGGER}).*?(?:{SENTENCE_END}|\Z)"

ESTRANGEIRAS = [
    'a contrario sensu', 'contrario sensu', 'a fortiori', 'a priori', 'a posteriori', 'a quo', 'ad quem', 'ab initio',
    'ad cautelam', 'ad hoc', 'ad judicia et extra', 'ad judicia', 'ad referendum', 'ad valorem', 'affectio societatis',
    'amicus curiae', 'an debeatur', 'animus', 'apud', 'bis in idem', 'non bis in idem', 'caput', 'citra petita',
    'extra petita', 'ultra petita', 'conditio sine qua non', 'sine qua non', 'culpa in eligendo', 'culpa in vigilando',
    'culpa in omittendo', 'custos legis', 'damnum in re ipsa', 'in re ipsa', 'data maxima venia', 'data venia',
    'permissa venia', 'concessa venia', 'de cujus', 'de facto', 'de jure', 'dies a quo', 'dies ad quem',
    'dominus litis', 'erga omnes', 'ex lege', 'ex nunc', 'ex officio', 'ex positis', 'ex tunc', 'ex vi', 'exempli gratia',
    'verbi gratia', 'fumus boni iuris', 'fumus boni juris', 'habeas corpus', 'habeas data', 'ibidem', 'id est',
    'in albis', 'in casu', 'in dubio pro misero', 'in dubio pro operario', 'in dubio pro reo', 'in fine', 'in itinere',
    'in limine litis', 'in limine', 'in natura', 'in totum', 'in verbis', 'inaudita altera parte',
    'inter partes', 'ipsis litteris', 'ipsis verbis', 'jus postulandi', 'jus resistentiae', 'jus variandi',
    'lato sensu', 'latu sensu', 'stricto sensu', 'strictu sensu', 'mens legis', 'modus operandi', 'mutatis mutandis',
    'nemo potest venire contra factum proprium', 'venire contra factum proprium', 'nomen juris', 'nomen iuris',
    'numerus clausus', 'obiter dictum', 'onus probandi', 'pacta sunt servanda', 'pari passu', 'per capita', 'per se',
    'periculum in mora', 'prima facie', 'pro labore', 'pro rata', 'quantum debeatur', 'quorum',
    'ratio decidendi', 'rebus sic stantibus', 'reformatio in pejus', 'reformatio in peius', 'res judicata',
    'res inter alios acta', 'status quo', 'sub judice', 'sui generis', 'vacatio legis', 'mandamus',
    'home office', 'burnout', 'dumping social', 'compliance', 'mobbing', 'bullying', 'stock options',
    'know-how', 'lay-off', 'layoff', 'outsourcing', 'headhunter', 'parquet',
]
ITALICO_RE = re.compile(r"(?<![\w-])(?:" + "|".join(
    re.escape(e).replace(r"\ ", r"\s+") for e in sorted(ESTRANGEIRAS, key=len, reverse=True)) + r")(?![\w-])", re.I)


def compilar(partes):
    nomes = sorted({n.strip() for n in (partes or []) if n and n.strip()}, key=len, reverse=True)
    parte_alt = "(?<!\\w)(?:" + "|".join(re.escape(n) for n in nomes) + ")(?!\\w)" if nomes else None
    so_partes = re.compile(f"(?P<parte>{parte_alt})", re.I) if parte_alt else None
    grupos = [f"(?P<parte>{parte_alt})"] if parte_alt else []
    grupos += [f"(?P<sumula>{SUMULA_RE})", f"(?P<date>{DATE_RE})", f"(?P<money>{MONEY_RE})", f"(?P<hours>{HOURS_RE})"]
    return so_partes, re.compile("|".join(grupos), re.I | re.S)


def _dividir(texto, regex, negrito, interno=None):
    if not texto:
        return []
    if regex is None:
        return [(texto, negrito)]
    out, pos = [], 0
    for m in regex.finditer(texto):
        if m.start() > pos:
            out.append((texto[pos:m.start()], negrito))
        achado, gd = m.group(0), m.groupdict()
        if gd.get("parte"):
            achado = achado.upper()
        if gd.get("sumula") and interno is not None:
            out.extend(_dividir(achado, interno, True))
        else:
            out.append((achado, True))
        pos = m.end()
    if pos < len(texto):
        out.append((texto[pos:], negrito))
    return out


MARCAS = re.compile(r"(\*\*.+?\*\*|\[\[.+?\]\]|(?<!\*)\*[^*\n]+?\*(?!\*))", re.S)


def segmentar(texto, so_partes, completo, auto=True, italico_auto=True):
    """Aplica **negrito**, [[PARTE]], *itálico* e os destaques automáticos. Devolve [(texto, negrito, itálico)]."""
    out = []
    for peca in MARCAS.split(texto):
        if not peca:
            continue
        if len(peca) >= 4 and peca.startswith("**") and peca.endswith("**"):
            out.extend((t, b, False) for t, b in _dividir(peca[2:-2], so_partes, True))
        elif len(peca) >= 4 and peca.startswith("[[") and peca.endswith("]]"):
            out.append((peca[2:-2].upper(), True, False))
        elif len(peca) >= 3 and peca.startswith("*") and peca.endswith("*"):
            out.append((peca[1:-1], False, True))
        else:
            out.extend((t, b, False) for t, b in _dividir(peca, completo if auto else so_partes, False, interno=so_partes))
    for t, _, _ in out:
        if "**" in t or "[[" in t or "]]" in t:
            raise ValueError("Marcador de negrito aberto e não fechado (** ou [[ ]]) em: " + repr(texto))
    if not italico_auto:
        return out
    final = []
    for t, b, i in out:
        if i:
            final.append((t, b, True))
            continue
        pos = 0
        for m in ITALICO_RE.finditer(t):
            if m.start() > pos:
                final.append((t[pos:m.start()], b, False))
            final.append((m.group(0), b, True))
            pos = m.end()
        if pos < len(t):
            final.append((t[pos:], b, False))
    return final


# ---------------------------------------------------------------------------
# Montagem
# ---------------------------------------------------------------------------
class Montador:
    def __init__(self, documento, formato, partes):
        self.doc, self.f = documento, formato
        self.so_partes, self.completo = compilar(partes)

    def fonte(self, run, negrito=False, italico=False, sublinhado=False, tamanho=None):
        run.font.name = self.f.fonte
        run.font.size = Pt(tamanho or self.f.tamanho)
        run.bold, run.italic, run.underline = negrito, italico, sublinhado
        rpr = run._element.get_or_add_rPr()
        rfonts = rpr.find(qn("w:rFonts"))
        if rfonts is None:
            rfonts = rpr.makeelement(qn("w:rFonts"), {})
            rpr.append(rfonts)
        for k in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            rfonts.set(qn(k), self.f.fonte)

    def paragrafo(self, alinhamento, recuo, espaco=False, tamanho=None, recuo_total=False):
        p = self.doc.add_paragraph()
        pf = p.paragraph_format
        tamanho = tamanho or self.f.tamanho
        pf.space_before = Pt(0)
        pf.space_after = Pt(0) if espaco else Pt(round(tamanho * self.f.entrelinha, 1))
        pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
        pf.line_spacing = self.f.entrelinha
        # Só centralizado ou justificado: qualquer outro valor vira justificado.
        pf.alignment = WD_ALIGN_PARAGRAPH.CENTER if alinhamento == "center" else WD_ALIGN_PARAGRAPH.JUSTIFY
        if recuo and recuo_total:
            pf.left_indent, pf.first_line_indent = self.f.recuo, Cm(0)
        elif recuo:
            pf.first_line_indent = self.f.recuo
        else:
            pf.first_line_indent = None
        return p

    def bloco(self, b):
        tipo = b.get("type", "paragraph")
        if tipo == "spacer":
            p = self.paragrafo(b.get("align", "justify"), False, espaco=True)
            self.fonte(p.add_run(""))
            return
        if tipo == "heading":
            p = self.paragrafo(b.get("align", "center"), b.get("indent", False))
            base = b.get("bold", True)
            for t, neg, ita in segmentar(b.get("text", ""), self.so_partes, self.completo, b.get("auto_negrito", True)):
                self.fonte(p.add_run(t.upper() if b.get("upper") else t), negrito=base or neg,
                           italico=b.get("italic", False) or ita, sublinhado=b.get("underline", False))
            return
        juris = tipo in ("jurisprudencia", "jurisprudência")
        tamanho = self.f.tamanho_juris if juris else self.f.tamanho
        p = self.paragrafo(b.get("align", "justify"), b.get("indent", True), tamanho=tamanho, recuo_total=juris)
        runs = b["runs"] if "runs" in b else [{"text": b.get("text", ""), "bold": b.get("bold", False),
                                                 "italic": b.get("italic", False),
                                                 "underline": b.get("underline", False)}]
        auto = b.get("auto_negrito", not juris)
        for r in runs:
            for t, neg, ita in segmentar(r.get("text", ""), None if juris else self.so_partes,
                                         None if juris else self.completo, auto, italico_auto=not juris):
                self.fonte(p.add_run(t), negrito=r.get("bold", False) or neg, italico=r.get("italic", False) or ita,
                           sublinhado=r.get("underline", False), tamanho=tamanho)


def abrir_documento(timbrado, formato):
    if timbrado:
        if not timbrado.is_file():
            raise FileNotFoundError(f"Timbrado não encontrado: {timbrado}")
        doc = Document(str(timbrado))
        corpo = doc.element.body
        for el in list(corpo):
            if el.tag != qn("w:sectPr"):
                corpo.remove(el)
        return doc
    doc = Document()
    for s in doc.sections:
        s.top_margin, s.right_margin, s.bottom_margin, s.left_margin = (Cm(x) for x in formato.margens)
    return doc


def gerar(blocos, saida, timbrado=None, perfil=None):
    campos = ler_perfil(perfil)
    formato = Formato(campos)
    caminho_timbrado = achar_timbrado(timbrado, campos)
    conferir_proibidos(blocos)
    partes, conteudo = [], []
    for b in blocos:
        if b.get("type") == "config":
            partes.extend(b.get("partes", []))
        else:
            conteudo.append(b)
    doc = abrir_documento(caminho_timbrado, formato)
    montador = Montador(doc, formato, partes)
    for b in conteudo:
        montador.bloco(b)
    doc.save(str(saida))
    origem = caminho_timbrado if caminho_timbrado else "sem timbrado (folha em branco)"
    print(f"OK: {saida}  |  timbrado: {origem}")
    return caminho_timbrado


PAGINA_DE_TESTE = [
    {"type": "config", "partes": ["Fulana de Tal", "Empresa Exemplo Ltda"]},
    {"type": "paragraph", "text": "AO JUÍZO DA __ª VARA DO TRABALHO DE [CIDADE] – [UF]", "indent": False},
    {"type": "paragraph", "text": "Fulana de Tal, brasileira, [qualificação], vem, respeitosamente, propor a presente:"},
    {"type": "heading", "text": "RECLAMAÇÃO TRABALHISTA"},
    {"type": "heading", "text": "DAS HORAS EXTRAS E REFLEXOS", "align": "justify"},
    {"type": "paragraph", "text": "A reclamante trabalhava das 8h às 18h, de segunda a sexta-feira, desde 01/03/2024, com "
                                  "salário de R$ 2.000,00 (dois mil reais), apurando-se **(9h x 5 dias) - 44h = 1h semanal**, "
                                  "conforme a Súmula nº 338, III, do TST."},
    {"type": "paragraph", "text": "Este é o entendimento consolidado, in verbis:"},
    {"type": "jurisprudencia", "text": "HORAS EXTRAS. CARTÕES DE PONTO BRITÂNICOS. Texto de exemplo para conferir a fonte "
                                       "menor e o recuo em todas as linhas do bloco de jurisprudência."},
    {"type": "paragraph", "text": "Requer, portanto, a condenação da Empresa Exemplo Ltda ao pagamento de **horas extras** e reflexos."},
    {"type": "spacer"},
    {"type": "paragraph", "text": "Termos em que,", "indent": False},
    {"type": "paragraph", "text": "pede deferimento.", "indent": False},
    {"type": "paragraph", "text": "[ADVOGADO]", "align": "center", "indent": False, "bold": True},
    {"type": "paragraph", "text": "[OAB]", "align": "center", "indent": False, "bold": True},
]


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Gera .docx de peça trabalhista sobre o timbrado do escritório.")
    ap.add_argument("conteudo", nargs="?", help="conteudo.json (omita com --testar)")
    ap.add_argument("saida")
    ap.add_argument("--timbrado")
    ap.add_argument("--perfil")
    ap.add_argument("--testar", action="store_true", help="gera uma página de teste para conferir o timbrado")
    a = ap.parse_args()
    try:
        if a.testar:
            gerar(PAGINA_DE_TESTE, a.saida, a.timbrado, a.perfil)
        else:
            if not a.conteudo:
                ap.error("informe o conteudo.json ou use --testar")
            with open(a.conteudo, encoding="utf-8") as f:
                gerar(json.load(f), a.saida, a.timbrado, a.perfil)
    except (ValueError, FileNotFoundError) as e:
        sys.exit(f"ERRO: {e}")
