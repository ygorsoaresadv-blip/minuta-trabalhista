#!/usr/bin/env python3
"""
Monta a base de teses do escritório a partir das PRÓPRIAS petições (.docx), com anonimização.

Uso:
    python montar_base.py "<pasta com as petições>" [--tipo inicial|contestacao] [--saida <pasta>]
        [--ignorar "TRECHO DE SUBPASTA"] [--incluir-fatos] [--permitir-repositorio]

Gera, por padrão em ~/.claude/minuta/teses/<tipo>/ (ou MINUTA_HOME/teses/<tipo>/):
    base-teses.json              teses (texto literal anonimizado) e linhas de pedido
    relatorio-anonimizacao.md    o que foi trocado por marcador e o que PARECE dado pessoal e sobrou

Como funciona:
    - Cada petição é dividida em tópicos pelos títulos (parágrafos em negrito e caixa alta).
    - Tópicos com o mesmo título viram uma tese; ficam as 2 versões mais recentes.
    - Qualificação, endereçamento, assinatura e tópicos de fatos do caso (DO CONTRATO, DOS FATOS...) ficam fora.
    - Nome do cliente e das empresas da qualificação, CPF, CNPJ, RG, PIS, CTPS, e-mail, telefone, CEP, endereço,
      número de processo e OAB viram marcadores. Termos extras: um por linha em ~/.claude/minuta/anonimizar-extra.txt.
    - A base nunca é gravada dentro de um repositório Git (salvo --permitir-repositorio).

A anonimização é automática e falha: SEMPRE leia o relatório antes de usar a base.
Requisitos: python-docx. Para .doc antigos, LibreOffice (soffice) no PATH.
"""
import argparse
import collections
import datetime
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path


def minuta_home():
    return Path(os.environ.get("MINUTA_HOME") or Path.home() / ".claude" / "minuta")


# ---------------------------------------------------------------------------
# Leitura e segmentação
# ---------------------------------------------------------------------------
def eh_titulo(p):
    t = p.text.strip()
    if not t or len(t) > 220:
        return False
    runs = [r for r in p.runs if r.text.strip()]
    estilo_negrito = bool(p.style is not None and p.style.font is not None and p.style.font.bold)
    if not runs or not all(r.bold or (r.bold is None and estilo_negrito) for r in runs):
        return False
    letras = [c for c in t if c.isalpha()]
    return len(letras) >= 4 and sum(c.isupper() for c in letras) / len(letras) > 0.85


def citacao(p):
    """Bloco de jurisprudência: fonte pequena ou recuo grande."""
    runs = [r for r in p.runs if r.text.strip()]
    tamanhos = [r.font.size.pt for r in runs if r.font.size]
    recuo = p.paragraph_format.left_indent
    return bool((tamanhos and max(tamanhos) <= 10.5) or (recuo is not None and recuo.cm > 3))


def itens(doc):
    from docx.table import Table
    from docx.text.paragraph import Paragraph
    for el in doc.element.body.iterchildren():
        tag = el.tag.split("}")[-1]
        if tag == "p":
            yield Paragraph(el, doc)
        elif tag == "tbl":
            for row in Table(el, doc).rows:
                celulas = []
                for c in row.cells:
                    ct = c.text.strip()
                    if ct and (not celulas or celulas[-1] != ct):
                        celulas.append(ct)
                if celulas:
                    yield {"t": " | ".join(celulas), "q": False}


def ler_peticao(caminho, data):
    from docx import Document
    doc = Document(caminho)
    secoes, atual, antes = [], None, []
    for p in itens(doc):
        if isinstance(p, dict):
            (atual["ps"] if atual else antes).append(p)
            continue
        if not p.text.strip():
            continue
        if eh_titulo(p):
            atual = {"h": p.text.strip(), "ps": []}
            secoes.append(atual)
        else:
            (atual["ps"] if atual else antes).append({"t": p.text.strip(), "q": citacao(p)})
    return {"data": data, "antes": antes, "secs": secoes}


# ---------------------------------------------------------------------------
# Anonimização
# ---------------------------------------------------------------------------
QUALIF = re.compile(r"portador.{0,40}RG|inscrit.{0,30}CPF|CTPS|residente e domiciliad", re.I)
PADROES = [
    (re.compile(r"\b\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\b"), "[PROCESSO]"),
    (re.compile(r"\b\d{20}\b"), "[PROCESSO]"),
    (re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-\d{2}\b"), "[CPF]"),
    (re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/\d{4}-\d{2}\b"), "[CNPJ]"),
    (re.compile(r"\b\d{3}\.\d{5}\.\d{2}-\d\b"), "[PIS]"),
    (re.compile(r"\b\d{1,2}\.\d{3}\.\d{3}-[\dXx]\b"), "[RG]"),
    (re.compile(r"\bCTPS\s+(?:n[ºo°.]*\s*)?[\d./-]+(?:\s*,?\s*s[ée]rie\s+[\d./-]+)?", re.I), "CTPS [CTPS]"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "[E-MAIL]"),
    (re.compile(r"\(?\b\d{2}\)?\s?9?\d{4}-?\d{4}\b"), "[TELEFONE]"),
    (re.compile(r"\bCEP:?\s*\d{5}-?\d{3}\b|\b\d{5}-\d{3}\b", re.I), "[CEP]"),
    (re.compile(r"\bOAB\s*/?\s*[A-Z]{2}\s*(?:n[ºo°.]*\s*)?[\d.]+", re.I), "[OAB]"),
    (re.compile(r"\b(?:Rua|R\.|Avenida|Av\.|Alameda|Al\.|Travessa|Estrada|Rodovia|Praça|Largo|Viela)\s+"
                r"[^,;\n]{2,80}?(?:,\s*(?:n[ºo°.]*\s*)?\d+[A-Za-z]?)?(?=[,;.\n]|\s-\s|$)"), "[ENDEREÇO]"),
]
PROPOSTA = re.compile(r"(?:proposta|ajuizada|movida) por ([^,]{5,90}),\s*j[áa] qualificad", re.I)
SOCIO = re.compile(r"^([A-ZÀ-Ý][A-ZÀ-Ý \.]{5,}),\s*(?=s[oó]ci|administrador)")


def termos_do_caso(peticao):
    """Nome do cliente (qualificação) e empresas (com CNPJ) do começo da petição."""
    cliente, empresas = [], []
    blocos = list(peticao["antes"])
    for s in peticao["secs"][:6]:
        blocos += [{"t": s["h"]}] + s["ps"]
    for p in blocos[:40]:
        t = p["t"]
        primeiro = re.sub(r"^(em face de|e)\s+", "", t.split(",")[0].strip(), flags=re.I).strip(" :")
        if QUALIF.search(t) and 5 < len(primeiro) < 90 and primeiro not in cliente:
            cliente.append(primeiro)
        elif "CNPJ" in t.upper() and 4 < len(primeiro) < 160 and primeiro not in empresas:
            empresas.append(primeiro)
        m = PROPOSTA.search(t)
        if m and m.group(1).strip() not in cliente:
            cliente.append(m.group(1).strip())
    termos = [(n, "[RECLAMANTE]") for n in cliente]
    termos += [(n, f"[{i}ª RECLAMADA]") for i, n in enumerate(empresas, 1)]
    return termos


# Sobrenomes tão comuns que aparecem em nome de relator, de lei ou de doutrina: só saem no nome completo.
SOBRENOMES_COMUNS = {"silva", "santos", "souza", "sousa", "oliveira", "pereira", "lima", "costa", "ferreira",
                     "rodrigues", "almeida", "nascimento", "carvalho", "araujo", "araújo", "ribeiro", "martins"}


def ler_extras():
    caminho = minuta_home() / "anonimizar-extra.txt"
    if not caminho.is_file():
        return []
    linhas = caminho.read_text(encoding="utf-8").splitlines()
    return [(l.strip(), "[ANONIMIZADO]") for l in linhas if l.strip() and not l.strip().startswith("#")]


def anonimizar(texto, termos, registro=None):
    """Troca dados pessoais por marcadores. 'registro' (Counter) conta o que foi trocado."""
    # 1º os nomes completos (o mais longo primeiro), para um não comer pedaço do outro
    for nome, marcador in sorted(termos, key=lambda x: len(x[0]), reverse=True):
        padrao = re.compile(r"(?<!\w)" + re.escape(nome) + r"(?!\w)", re.I)
        if registro is not None:
            for m in padrao.finditer(texto):
                registro[(m.group(0), marcador)] += 1
        texto = padrao.sub(marcador, texto)
    # 2º primeiro nome e sobrenomes soltos do cliente, só escritos como nome próprio (Maria, MARIA),
    # para não apagar palavra comum ("campos", "rocha") do texto jurídico
    for nome, marcador in termos:
        if marcador != "[RECLAMANTE]":
            continue
        for parte in [w for w in nome.split() if len(w) > 3 and w.lower() not in SOBRENOMES_COMUNS]:
            formas = {parte.upper(), parte[:1].upper() + parte[1:].lower()}
            p2 = re.compile(r"(?<!\w)(?:" + "|".join(re.escape(f) for f in formas) + r")(?!\w)")
            if registro is not None:
                for m in p2.finditer(texto):
                    registro[(m.group(0), marcador)] += 1
            texto = p2.sub(marcador, texto)
    texto = SOCIO.sub("[SÓCIO(A)], ", texto)
    for padrao, marcador in PADROES:
        if registro is not None:
            for m in padrao.finditer(texto):
                registro[(m.group(0), marcador)] += 1
        texto = padrao.sub(marcador, texto)
    return texto


# Palavras que tornam uma sequência de nomes próprios "jurídica", não pessoal.
COMUNS = set("""tribunal superior trabalho lei leis código codigo processo civil constituição constituicao federal justiça
justica vara excelência excelencia vossa súmula sumula regional região regiao consolidação consolidacao ministério
ministerio público publico reclamante reclamada reclamadas turma supremo seção secao orientação orientacao
jurisprudencial norma regulamentadora convenção convencao coletiva acordo previdência previdencia social fundo garantia
tempo serviço servico instituto nacional seguro brasil república republica estado municipal secretaria economia
emprego portaria resolução resolucao instrução instrucao normativa tema repercussão repercussao geral recursos
repetitivos incidente sdi tst stf trt clt cpc cf ccr cct act fgts inss pje ltda eireli epp mei rescisão rescisao
indireta horas extras adicional insalubridade periculosidade aviso prévio previo férias ferias décimo decimo terceiro
salário salario dano moral multa pedidos fatos mérito merito preliminarmente direito contrato juízo juizo
""".split())
# Nome de gente não tem estas palavras; ementa e título em caixa alta têm.
FUNCIONAIS = set("""não nao para pela pelo pelas pelos com sem caso inserir confirmar pendente sugestão sugestao
título titulo cláusula clausula verbas imposto renda perfil intervalo refeição refeicao jornada indenização
indenizacao ocorrência ocorrencia possibilidade inversão inversao ônus onus prova exibição exibicao documentos
controle ponto horários horarios extraordinária extraordinaria paga devida supressão supressao fruição fruicao
determinação determinacao empregadora valores proporção proporcao sindicato trabalhadores empresas serviços
servicos limpeza urbana conservação conservacao asseio prestação prestacao""".split())
NOME_TITULO = re.compile(r"\b[A-ZÀ-Ý][a-zà-ÿ]+(?:\s+(?:d[aeo]s?\s+|e\s+)?[A-ZÀ-Ý][a-zà-ÿ]+){1,5}")
NOME_CAIXA = re.compile(r"\b[A-ZÀ-Ý]{3,}(?:\s+(?:D[AEO]S?\s+|E\s+|&\s+)?[A-ZÀ-Ý]{3,}){1,6}\b")


def suspeitos(texto):
    """Sequências que parecem nome de pessoa ou empresa e não viraram marcador."""
    achados = []
    for regex in (NOME_TITULO, NOME_CAIXA):
        for m in regex.finditer(texto):
            palavras = [w.lower() for w in re.findall(r"[A-Za-zÀ-ÿ]+", m.group(0)) if len(w) > 2]
            if not palavras or any(w in COMUNS or w in FUNCIONAIS for w in palavras):
                continue
            if regex is NOME_TITULO and m.start() > 0 and texto[max(0, m.start() - 2):m.start()].strip() in ("", ".", ":"):
                # começo de frase: só conta com 3 palavras ou mais
                if len(palavras) < 3:
                    continue
            ini = max(0, m.start() - 40)
            achados.append((m.group(0), texto[ini:m.end() + 40].replace("\n", " ")))
    return achados


# ---------------------------------------------------------------------------
# Agrupamento
# ---------------------------------------------------------------------------
def normalizar(h):
    h = unicodedata.normalize("NFKD", h).encode("ascii", "ignore").decode().upper()
    return re.sub(r"\s+", " ", re.sub(r"[^A-Z0-9 ]", " ", h)).strip()


FECHO = re.compile(r"^(Os pedidos devem|Protesta|D[áa]-se|Diante do exposto|Ante o exposto)", re.I)
ESTRUTURA = re.compile(r"^(OAB|RECLAMACAO TRABALHISTA|CONTESTACAO|REPLICA|AO JUIZO|EXCELENTISSIMO|PRELIMINARMENTE|"
                       r"NO MERITO|DO MERITO|DOS PEDIDOS|DO PEDIDO|DOS REQUERIMENTOS|CONCLUSAO|DA CONCLUSAO|TERMOS EM QUE|"
                       r"SINOPSE|PROCESSO)")
FATOS = re.compile(r"^(DOS FATOS|DO CONTRATO|CONTRATO|DO CONTRATO DE TRABALHO|JORNADA DE TRABALHO|"
                   r"ADMISSAO FUNCAO SALARIO.*|DA COMPETENCIA TERRITORIAL|SINOPSE DA INICIAL|BREVE SINTESE.*|DOS FATOS E.*)$")


def montar(peticoes, incluir_fatos=False, extras=()):
    grupos = collections.OrderedDict()
    pedidos = collections.Counter()
    registro = collections.Counter()
    for pet in peticoes:
        termos = termos_do_caso(pet) + list(extras)
        dt = pet["data"]
        rotulo = f"Petição de {dt[8:10]}/{dt[5:7]}/{dt[:4]}"
        em_pedidos = merito = False
        total = len(pet["secs"])
        for i, s in enumerate(pet["secs"]):
            k = normalizar(s["h"])
            if re.match(r"^(NO MERITO|DO MERITO)", k):
                merito = True
            if k.startswith(("DOS PEDIDOS", "DO PEDIDO")):
                em_pedidos = True
            if em_pedidos:
                for p in s["ps"]:
                    if p["t"].lower().startswith(("termos em que", "pede deferimento", "nestes termos")):
                        em_pedidos = "fim"
                    if em_pedidos == "fim" or FECHO.match(p["t"]):
                        continue
                    t = anonimizar(p["t"], termos, registro)
                    t = re.sub(r"\s*[\.…]{4,}.*$", "", t).strip()
                    t = re.sub(r"\s*R\$\s*[\d\.,]+;?\s*$", "", t).strip()
                    t = re.sub(r"^[a-zA-Z]{1,2}[\).]\s*", "", t).strip()
                    if len(t) < 15 or t.lower().startswith(("termos em que", "pede deferimento", "diante do exposto")):
                        continue
                    if re.match(r"^[A-ZÀ-Ý][^,]{3,40}, \d{1,2} de ", t):
                        continue
                    pedidos[t] += 1
                continue
            if ESTRUTURA.match(k) or "CNPJ" in k or "LTDA" in k or not s["ps"] or re.match(r"^[A-Z]$", k):
                continue
            if FATOS.match(k) and not incluir_fatos:
                continue
            if QUALIF.search(s["ps"][0]["t"]):
                continue
            ps = [{"t": anonimizar(p["t"], termos, registro), "q": p["q"]} for p in s["ps"]]
            txt = "\n".join(p["t"] for p in ps)
            if len(txt) < 60:
                continue
            h = hashlib.sha1(re.sub(r"\s+", " ", txt).encode()).hexdigest()[:12]
            g = grupos.setdefault(k, {"n": set(), "vars": {}, "pos": [], "pre": []})
            g["n"].add(id(pet))
            g["pos"].append(i / max(total, 1))
            g["pre"].append(not merito)
            v = g["vars"].get(h)
            if not v or v["data"] < dt:
                g["vars"][h] = {"data": dt, "arq": rotulo, "h": anonimizar(s["h"], termos, registro), "ps": ps}
    teses = []
    for i, (k, g) in enumerate(grupos.items()):
        vs = sorted(g["vars"].values(), key=lambda v: v["data"], reverse=True)[:2]
        teses.append({"id": "t%03d" % i, "h": vs[0]["h"], "n": len(g["n"]), "fatos": bool(FATOS.match(k)),
                      "pos": round(sum(g["pos"]) / len(g["pos"]), 3), "pre": sum(g["pre"]) > len(g["pre"]) / 2,
                      "vars": [{"data": v["data"], "arq": v["arq"], "ps": v["ps"]} for v in vs]})
    teses.sort(key=lambda x: -x["n"])
    base = {"gerado": datetime.date.today().isoformat(), "ndocs": len(peticoes), "teses": teses,
            "pedidos": [{"t": t, "n": n} for t, n in pedidos.most_common()
                        if n >= (2 if len(peticoes) >= 5 else 1) and len(t) < 400]}
    return base, registro


def relatorio(base, registro, ilegiveis):
    linhas = [f"# Relatório de anonimização ({base['gerado']})", "",
              f"{base['ndocs']} petição(ões), {len(base['teses'])} teses, {len(base['pedidos'])} linhas de pedido.", "",
              "Leia tudo antes de usar a base. A anonimização é automática e pode falhar. O que sobrou de dado pessoal",
              "vai para `anonimizar-extra.txt` (um termo por linha) e a base é montada de novo.", "",
              "**Este relatório contém os dados pessoais originais (coluna \"Texto original\").** Não o compartilhe nem o",
              "envie a ninguém; apague-o depois de conferir. A base (`base-teses.json`) é que fica.", ""]
    linhas += ["## Trocados por marcador", "", "| Texto original | Marcador | Vezes |", "|---|---|---|"]
    for (orig, marc), n in sorted(registro.items(), key=lambda x: -x[1])[:400]:
        linhas.append(f"| {orig.replace('|', '/')} | {marc} | {n} |")
    vistos, sus = set(), []
    for t in base["teses"]:
        for v in t["vars"]:
            for p in v["ps"]:
                if p.get("q"):
                    continue  # transcrição de julgado: nomes de relator são públicos
                for nome, ctx in suspeitos(p["t"]):
                    if nome not in vistos:
                        vistos.add(nome)
                        sus.append((t["id"], nome, ctx))
    for ped in base["pedidos"]:
        for nome, ctx in suspeitos(ped["t"]):
            if nome not in vistos:
                vistos.add(nome)
                sus.append(("pedido", nome, ctx))
    linhas += ["", f"## Parecem nome de pessoa ou empresa e ficaram ({len(sus)})", "",
               "Muitos são falsos alarmes (nomes de lei, de tribunal, de doutrina). Confira um a um.", "",
               "| Tese | Trecho | Contexto |", "|---|---|---|"]
    for tid, nome, ctx in sus[:500]:
        linhas.append(f"| {tid} | {nome.replace('|', '/')} | …{ctx.replace('|', '/')}… |")
    if ilegiveis:
        linhas += ["", "## Arquivos que não consegui ler", ""] + [f"- {x}" for x in ilegiveis]
    return "\n".join(linhas) + "\n"


# ---------------------------------------------------------------------------
# Execução
# ---------------------------------------------------------------------------
def dentro_de_repositorio(pasta):
    p = Path(pasta).resolve()
    for d in [p, *p.parents]:
        if (d / ".git").exists():
            return d
    return None


def arquivos(pasta, ignorar):
    achados = []
    for f in glob.glob(os.path.join(pasta, "**", "*"), recursive=True):
        rel = os.path.relpath(f, pasta)
        if any(x.upper() in rel.upper() for x in ignorar) or os.path.basename(f).startswith("~$"):
            continue
        if f.lower().endswith((".docx", ".doc")):
            achados.append(f)
    return sorted(achados)


def converter_doc(antigos):
    if not antigos:
        return {}
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        print(f"Aviso: {len(antigos)} arquivo(s) .doc ignorado(s): LibreOffice não encontrado. Salve-os como .docx.")
        return {}
    tmp = tempfile.mkdtemp()
    subprocess.run([soffice, "--headless", "--convert-to", "docx", "--outdir", tmp, *antigos],
                   capture_output=True, timeout=600)
    conv = {}
    for f in antigos:
        c = os.path.join(tmp, os.path.splitext(os.path.basename(f))[0] + ".docx")
        if os.path.exists(c):
            conv[f] = c
    return conv


def data_do_arquivo(f):
    m = re.match(r"(\d{4})[.\-_](\d{2})[.\-_](\d{2})", os.path.basename(f))
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return datetime.datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Monta a base de teses anonimizada a partir das suas petições.")
    ap.add_argument("pasta")
    ap.add_argument("--tipo", choices=["inicial", "contestacao"], default="inicial")
    ap.add_argument("--saida")
    ap.add_argument("--ignorar", action="append", default=[])
    ap.add_argument("--incluir-fatos", action="store_true", help="inclui tópicos de fatos do caso (mais risco)")
    ap.add_argument("--permitir-repositorio", action="store_true")
    a = ap.parse_args(argv)
    try:
        import docx  # noqa: F401
    except ImportError:
        sys.exit("Instale o python-docx: pip install python-docx")
    if not os.path.isdir(a.pasta):
        sys.exit(f"Pasta não encontrada: {a.pasta}")
    saida = Path(a.saida) if a.saida else minuta_home() / "teses" / a.tipo
    repo = dentro_de_repositorio(saida.parent if not saida.exists() else saida)
    if repo and not a.permitir_repositorio:
        sys.exit(f"Recusado: {saida} fica dentro do repositório Git {repo}. A base não deve ir para o Git.")
    lista = arquivos(a.pasta, a.ignorar)
    conv = converter_doc([f for f in lista if f.lower().endswith(".doc")])
    peticoes, ilegiveis = [], []
    for f in lista:
        real = conv.get(f, f)
        if real.lower().endswith(".doc"):
            ilegiveis.append(os.path.basename(f))
            continue
        try:
            peticoes.append(ler_peticao(real, data_do_arquivo(f)))
        except Exception as e:  # arquivo corrompido, protegido etc.
            ilegiveis.append(f"{os.path.basename(f)} ({type(e).__name__})")
    if not peticoes:
        sys.exit("Nenhuma petição .docx legível encontrada.")
    base, registro = montar(peticoes, a.incluir_fatos, ler_extras())
    saida.mkdir(parents=True, exist_ok=True)
    (saida / "base-teses.json").write_text(json.dumps(base, ensure_ascii=False, indent=1), encoding="utf-8")
    (saida / "relatorio-anonimizacao.md").write_text(relatorio(base, registro, ilegiveis), encoding="utf-8")
    print(f"{len(peticoes)} petição(ões), {len(base['teses'])} teses, {len(base['pedidos'])} linhas de pedido")
    print(f"Base: {saida / 'base-teses.json'}")
    print(f"Relatório (leia antes de usar): {saida / 'relatorio-anonimizacao.md'}")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
