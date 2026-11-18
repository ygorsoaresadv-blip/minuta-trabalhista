"""Testes dos scripts Python, com petições e timbrado fictícios criados na hora."""
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

from docx import Document

RAIZ = Path(__file__).resolve().parent.parent


def carregar(nome, caminho):
    spec = importlib.util.spec_from_file_location(nome, RAIZ / caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gerar_docx = carregar("gerar_docx", "skills/documento/scripts/gerar_docx.py")
montar_base = carregar("montar_base", "skills/teses/scripts/montar_base.py")
buscar_teses = carregar("buscar_teses", "skills/teses/scripts/buscar_teses.py")


def titulo(doc, texto):
    doc.add_paragraph().add_run(texto).bold = True


def peticao_ficticia(caminho, nome="FULANA DE TESTE SOBRENOMEFICTICIO"):
    d = Document()
    d.add_paragraph("AO JUÍZO DA __ª VARA DO TRABALHO DE CIDADE – UF")
    d.add_paragraph(f"{nome}, brasileira, solteira, portadora do RG nº 00.000.000-0, inscrita no CPF sob o nº "
                    "000.000.000-00, residente na Rua das Flores Imaginárias, 123, CEP 01234-567, telefone (11) 90000-0000, "
                    "e-mail fulana@example.com, vem propor a presente:")
    titulo(d, "RECLAMAÇÃO TRABALHISTA")
    d.add_paragraph("em face de EMPRESA FICTÍCIA DE TESTE LTDA, inscrita no CNPJ sob o nº 00.000.000/0001-00, pelas razões:")
    titulo(d, "DAS HORAS EXTRAS E REFLEXOS")
    d.add_paragraph(f"A parte reclamante, {nome.title()}, trabalhava para a EMPRESA FICTÍCIA DE TESTE LTDA das 8h às 18h, "
                    "conforme processo 0000000-00.2024.5.02.0000, sem receber as horas extras devidas, nos termos do "
                    "art. 59 da CLT. A Sobrenomeficticio sempre cumpriu a jornada.")
    d.add_paragraph("Requer, portanto, a condenação da reclamada ao pagamento de horas extras e reflexos.")
    titulo(d, "DOS PEDIDOS")
    d.add_paragraph("Diante do exposto, requer a parte reclamante:")
    d.add_paragraph("a) o pagamento de horas extras excedentes à 8ª diária, com adicional de 50%;")
    d.add_paragraph("Termos em que,")
    d.add_paragraph("pede deferimento.")
    d.add_paragraph("Advogado Fictício")
    d.save(caminho)


class TestMontarBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.pasta = Path(self.tmp.name)
        (self.pasta / "peticoes").mkdir()
        peticao_ficticia(self.pasta / "peticoes" / "2026.01.10 inicial.docx")
        self.home = self.pasta / "home"
        os.environ["PRAXIS_HOME"] = str(self.home)

    def tearDown(self):
        os.environ.pop("PRAXIS_HOME", None)
        self.tmp.cleanup()

    def montar(self):
        montar_base.main([str(self.pasta / "peticoes"), "--tipo", "inicial"])
        base = json.loads((self.home / "teses" / "inicial" / "base-teses.json").read_text(encoding="utf-8"))
        rel = (self.home / "teses" / "inicial" / "relatorio-anonimizacao.md").read_text(encoding="utf-8")
        return base, rel

    def test_anonimiza_dados_pessoais(self):
        base, rel = self.montar()
        bruto = json.dumps(base, ensure_ascii=False)
        for dado in ["FULANA", "Fulana", "Sobrenomeficticio", "000.000.000-00", "00.000.000/0001-00", "Flores",
                     "01234-567", "90000-0000", "fulana@", "0000000-00.2024", "EMPRESA FICTÍCIA"]:
            self.assertNotIn(dado, bruto, dado)
        self.assertIn("[RECLAMANTE]", bruto)
        self.assertIn("[1ª RECLAMADA]", bruto)
        self.assertIn("[PROCESSO]", bruto)
        self.assertIn("Trocados por marcador", rel)

    def test_guarda_a_tese_e_o_pedido(self):
        base, _ = self.montar()
        self.assertEqual([t["h"] for t in base["teses"]], ["DAS HORAS EXTRAS E REFLEXOS"])
        self.assertIn("art. 59 da CLT", base["teses"][0]["vars"][0]["ps"][0]["t"])
        self.assertEqual(base["teses"][0]["vars"][0]["arq"], "Petição de 10/01/2026")
        self.assertTrue(any("horas extras excedentes" in p["t"] for p in base["pedidos"]))
        self.assertFalse(any("Advogado" in p["t"] for p in base["pedidos"]))

    def test_termos_extras(self):
        self.home.mkdir(parents=True)
        (self.home / "anonimizar-extra.txt").write_text("das 8h às 18h\n", encoding="utf-8")
        base, _ = self.montar()
        self.assertIn("[ANONIMIZADO]", json.dumps(base, ensure_ascii=False))

    def test_recusa_gravar_dentro_de_repositorio(self):
        repo = self.pasta / "repo"
        (repo / ".git").mkdir(parents=True)
        with self.assertRaises(SystemExit):
            montar_base.main([str(self.pasta / "peticoes"), "--saida", str(repo / "base")])

    def test_busca(self):
        self.montar()
        self.assertEqual(buscar_teses.pontuar(buscar_teses.carregar("inicial")["teses"][0], ["horas"]) > 0, True)


class TestGerarDocx(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.pasta = Path(self.tmp.name)
        os.environ["PRAXIS_HOME"] = str(self.pasta / "home")

    def tearDown(self):
        os.environ.pop("PRAXIS_HOME", None)
        self.tmp.cleanup()

    def test_usa_o_timbrado_e_apaga_o_corpo(self):
        timbrado = Document()
        timbrado.sections[0].header.paragraphs[0].text = "ESCRITÓRIO FICTÍCIO"
        timbrado.add_paragraph("texto antigo que deve sumir")
        timbrado.save(self.pasta / "timbrado.docx")
        saida = self.pasta / "peca.docx"
        gerar_docx.gerar(gerar_docx.PAGINA_DE_TESTE, saida, timbrado=self.pasta / "timbrado.docx")
        doc = Document(saida)
        self.assertEqual(doc.sections[0].header.paragraphs[0].text, "ESCRITÓRIO FICTÍCIO")
        textos = [p.text for p in doc.paragraphs]
        self.assertNotIn("texto antigo que deve sumir", textos)
        self.assertIn("RECLAMAÇÃO TRABALHISTA", textos)

    def test_sem_timbrado_usa_folha_em_branco(self):
        self.assertIsNone(gerar_docx.gerar(gerar_docx.PAGINA_DE_TESTE, self.pasta / "a.docx"))

    def test_formato_do_perfil(self):
        perfil = self.pasta / "perfil.md"
        perfil.write_text('---\nfonte: "Arial"\ntamanho: "11"\n---\n# Perfil\n', encoding="utf-8")
        saida = self.pasta / "b.docx"
        gerar_docx.gerar([{"type": "paragraph", "text": "Texto."}], saida, perfil=perfil)
        run = Document(saida).paragraphs[0].runs[0]
        self.assertEqual((run.font.name, run.font.size.pt), ("Arial", 11))

    def test_destaques_automaticos(self):
        so_partes, completo = gerar_docx.compilar(["Fulana de Tal"])
        segs = gerar_docx.segmentar("Fulana de Tal recebia R$ 1.000,00, in verbis, conforme a Súmula nº 338 do TST.",
                                    so_partes, completo)
        negritos = [t for t, b, i in segs if b]
        italicos = [t for t, b, i in segs if i]
        self.assertIn("FULANA DE TAL", negritos)
        self.assertIn("R$ 1.000,00", negritos)
        self.assertIn("Súmula nº 338 do TST.", negritos)
        self.assertEqual(italicos, ["in verbis"])

    def test_recusa_travessao_e_negrito_aberto(self):
        with self.assertRaises(ValueError):
            gerar_docx.gerar([{"type": "paragraph", "text": "a — b"}], self.pasta / "c.docx")
        with self.assertRaises(ValueError):
            gerar_docx.gerar([{"type": "paragraph", "text": "**aberto"}], self.pasta / "d.docx")


if __name__ == "__main__":
    unittest.main()
