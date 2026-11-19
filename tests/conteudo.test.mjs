import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { decidir, LEMBRETE, PECA_RE } from "../hooks/lembrete.mjs";

const raiz = join(dirname(fileURLToPath(import.meta.url)), "..");
const skills = readdirSync(join(raiz, "skills"));

function frontmatter(texto) {
  const m = texto.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  return m ? m[1] : "";
}

test("as cinco skills existem", () => {
  assert.deepEqual([...skills].sort(), ["documento", "escrita", "lembrar", "perfil", "teses"]);
});

test("agente redator: frontmatter, skills citadas existem e nenhuma ação externa permitida", () => {
  const texto = readFileSync(join(raiz, "agents", "redator.md"), "utf8");
  const fm = frontmatter(texto);
  assert.match(fm, /^name: redator$/m);
  assert.match(fm, /^description: .{200,}$/m);
  for (const [, nome] of texto.matchAll(/minuta:(\w+)/g)) assert.ok(skills.includes(nome), `skill minuta:${nome} não existe`);
  for (const script of ["buscar_teses.py", "conferir.py", "gerar_docx.py"]) assert.ok(texto.includes(script), script);
  assert.match(texto, /## Nunca[\s\S]*Protocolar/);
});

for (const skill of skills) {
  const pasta = join(raiz, "skills", skill);
  const texto = readFileSync(join(pasta, "SKILL.md"), "utf8");

  test(`${skill}: frontmatter com name igual à pasta e description`, () => {
    const fm = frontmatter(texto);
    assert.match(fm, new RegExp(`^name: ${skill}$`, "m"));
    assert.match(fm, /^description: .{80,}$/m);
  });

  test(`${skill}: todo arquivo citado em references/, scripts/ ou templates/ existe`, () => {
    const citados = texto.match(/(?:references|scripts|templates)\/[\w.-]+\.\w+/g) ?? [];
    for (const c of citados) assert.ok(existsSync(join(pasta, c)), `${skill} cita ${c}, que não existe`);
  });
}

test("as regras de escrita não usam travessão, que elas mesmas proíbem", () => {
  const pasta = join(raiz, "skills", "escrita");
  const arquivos = ["SKILL.md", ...readdirSync(join(pasta, "references")).map((f) => `references/${f}`)];
  for (const f of arquivos) {
    const linhas = readFileSync(join(pasta, f), "utf8").split("\n");
    const com = linhas.filter((l) => l.includes("—") && !/travess[ãa]o|"—"|\(—\)/i.test(l));
    assert.deepEqual(com, [], f);
  }
});

test("lembrete: avisa uma vez por sessão em pedido de peça", () => {
  const primeiro = decidir({ input: { prompt: "faz a contestação de horas extras" }, estado: {} });
  assert.equal(primeiro.saida.hookSpecificOutput.additionalContext, LEMBRETE);
  const segundo = decidir({ input: { prompt: "agora a réplica" }, estado: primeiro.estado });
  assert.equal(segundo.saida, null);
});

test("lembrete: fica quieto fora de peça trabalhista", () => {
  assert.equal(PECA_RE.test("arruma o CSS do site"), false);
  assert.equal(decidir({ input: { prompt: "qual a previsão do tempo" }, estado: {} }).saida, null);
});
