import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const raiz = join(dirname(fileURLToPath(import.meta.url)), "..");
const json = (c) => JSON.parse(readFileSync(join(raiz, c), "utf8"));

test("plugin.json declara praxis sob MIT, com versão igual ao package.json", () => {
  const plugin = json(".claude-plugin/plugin.json");
  assert.equal(plugin.name, "praxis");
  assert.equal(plugin.license, "MIT");
  assert.equal(plugin.version, json("package.json").version);
  assert.equal(plugin.repository, "https://github.com/ygorsoaresadv-blip/praxis-trabalhista");
  assert.match(plugin.description, /^[\x20-\x7E]{20,}$/);
});

test("marketplace.json lista só o plugin da raiz", () => {
  const market = json(".claude-plugin/marketplace.json");
  assert.equal(market.name, "praxis-trabalhista");
  assert.equal(market.plugins.length, 1);
  assert.equal(market.plugins[0].name, "praxis");
  assert.equal(market.plugins[0].source, "./");
});

test("hooks.json chama o lembrete pelo CLAUDE_PLUGIN_ROOT", () => {
  const hooks = json("hooks/hooks.json");
  const cmd = hooks.hooks.UserPromptSubmit[0].hooks[0].command;
  assert.match(cmd, /\$\{CLAUDE_PLUGIN_ROOT\}\/hooks\/lembrete\.mjs/);
});

test(".gitignore mantém documentos e dados do escritório fora do Git", () => {
  const linhas = readFileSync(join(raiz, ".gitignore"), "utf8").split(/\r?\n/);
  for (const l of ["*.docx", "*.pdf", "base-teses.json", "perfil.md", "gosto.md", "anonimizar-extra.txt", "tests/lista-negra.txt"]) {
    assert.ok(linhas.includes(l), `falta ${l}`);
  }
});
