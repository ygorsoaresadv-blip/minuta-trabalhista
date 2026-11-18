import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { dirname, extname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";

// Barreira contra dado real no repositório público. Só valores fictícios (zerados) passam.
const raiz = join(dirname(fileURLToPath(import.meta.url)), "..");
const IGNORAR = new Set([".git", "node_modules", "__pycache__"]);
const TEXTO = new Set([".md", ".py", ".mjs", ".js", ".json", ".yml", ".yaml", ".txt", ".html", ""]);

function arquivos(pasta = raiz) {
  return readdirSync(pasta).flatMap((nome) => {
    if (IGNORAR.has(nome)) return [];
    const caminho = join(pasta, nome);
    return statSync(caminho).isDirectory() ? arquivos(caminho) : [caminho];
  });
}

const rel = (c) => relative(raiz, c).replaceAll("\\", "/");
const todos = arquivos();
const textos = todos.filter((c) => TEXTO.has(extname(c)) && !rel(c).startsWith("tests/lista-negra"));
const ler = (c) => readFileSync(c, "utf8");

const REGRAS = [
  { nome: "CPF", re: /\b\d{3}\.\d{3}\.\d{3}-\d{2}\b/g, ok: (m) => /^[0.\-]+$/.test(m) },
  { nome: "CNPJ", re: /\b\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}\b/g, ok: (m) => /^00\.000\.000\/000[01]-00$/.test(m) },
  { nome: "processo CNJ", re: /\b\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\b/g, ok: (m) => /^0{7}-00\.(0{4}|20\d\d)\.\d\.\d{2}\.0{4}$/.test(m) },
  { nome: "OAB", re: /OAB\/[A-Z]{2}\s*(?:n[ºo°.]*\s*)?\d{1,3}\.?\d{3}/g, ok: (m) => /0{2,3}\.?0{3}$/.test(m) },
  { nome: "telefone", re: /\(?\b\d{2}\)?\s?9?\d{4}-\d{4}\b/g, ok: (m) => m.includes("90000-") || /^[(0)\s9-]+$/.test(m) },
  {
    nome: "e-mail",
    re: /[\w.+-]+@[\w-]+\.[\w.]+/g,
    ok: (m) => /@(users\.noreply\.github\.com|example\.(com|org)|anthropic\.com)$/.test(m),
  },
];

test("nenhum dado pessoal real em arquivo de texto (só valores zerados ou fictícios)", () => {
  const achados = [];
  for (const c of textos) {
    const conteudo = ler(c);
    for (const { nome, re, ok } of REGRAS) {
      for (const m of conteudo.match(re) ?? []) if (!ok(m)) achados.push(`${rel(c)}: ${nome} ${m}`);
    }
  }
  assert.deepEqual(achados, []);
});

test("nenhum documento, PDF ou base de teses no repositório", () => {
  const proibidos = todos.filter((c) => /\.(docx?|pdf|odt|rtf|zip)$/i.test(c) || /base-teses\.json$/.test(c));
  assert.deepEqual(proibidos.map(rel), []);
});

test("nenhum perfil, gosto ou lista de anonimização fora dos modelos", () => {
  const modelos = new Set(["skills/perfil/templates/perfil.md", "skills/lembrar/templates/gosto.md"]);
  const achados = todos.map(rel).filter((r) => /(^|\/)(perfil|gosto)\.md$|anonimizar-extra\.txt$/.test(r) && !modelos.has(r));
  assert.deepEqual(achados, []);
});

// Lista local, fora do Git: nomes de clientes, do escritório, de empresas. Um termo por linha.
test("nenhum termo da lista negra local (tests/lista-negra.txt)", (t) => {
  const arq = join(raiz, "tests", "lista-negra.txt");
  if (!existsSync(arq)) return t.skip("sem lista negra local");
  const termos = ler(arq).split(/\r?\n/).map((l) => l.trim()).filter((l) => l && !l.startsWith("#"));
  const achados = [];
  for (const c of textos) {
    const conteudo = ler(c).toLowerCase();
    for (const termo of termos) if (conteudo.includes(termo.toLowerCase())) achados.push(`${rel(c)}: "${termo}"`);
  }
  assert.deepEqual(achados, []);
});
