#!/usr/bin/env node
// Lembra o agente de carregar minuta:escrita quando o pedido é uma peça trabalhista,
// uma vez por sessão. Nunca bloqueia nem falha: qualquer problema vira silêncio.

import { existsSync, mkdirSync, readdirSync, readFileSync, realpathSync, statSync, unlinkSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

export const PECA_RE =
  /\b(peti[çc][ãa]o|peti[çc][õo]es|inicial|iniciais|contesta[çc][ãa]o|contesta[çc][õo]es|r[ée]plica|contrarraz[õo]es|crro|recurso ordin[áa]rio|reclama[çc][ãa]o trabalhista|tese|teses|pe[çc]a|pe[çc]as|rol de pedidos|timbrado)\b/i;
export const LEMBRETE =
  "minuta: este pedido envolve peça trabalhista. Antes de redigir ou revisar, carregue a skill minuta:escrita e leia ~/.claude/minuta/perfil.md e ~/.claude/minuta/gosto.md, se existirem. Para teses do escritório use minuta:teses; para o Word no timbrado, minuta:documento.";

const VALIDADE_MS = 7 * 24 * 60 * 60 * 1000;

/** Decisão pura: o que imprimir e o novo estado da sessão. */
export function decidir({ input, estado }) {
  if (typeof input?.prompt !== "string" || !PECA_RE.test(input.prompt) || estado.avisado) return { saida: null, estado };
  return {
    saida: { hookSpecificOutput: { hookEventName: "UserPromptSubmit", additionalContext: LEMBRETE } },
    estado: { ...estado, avisado: true },
  };
}

function pastaEstado(env) {
  if (env.MINUTA_STATE_DIR) return env.MINUTA_STATE_DIR;
  return join(env.CLAUDE_PLUGIN_DATA || join(env.XDG_CACHE_HOME || join(homedir(), ".cache"), "minuta"), "hooks");
}

function limparAntigos(pasta, agora) {
  for (const nome of readdirSync(pasta)) {
    const arq = join(pasta, nome);
    if (nome.endsWith(".json") && agora - statSync(arq).mtimeMs > VALIDADE_MS) unlinkSync(arq);
  }
}

async function lerEntrada() {
  let dados = "";
  for await (const parte of process.stdin) dados += parte;
  return dados;
}

async function cli(env) {
  const input = JSON.parse(await lerEntrada());
  const sessao = String(input?.session_id ?? "").replace(/[^A-Za-z0-9_-]/g, "");
  if (!sessao) return;
  const pasta = pastaEstado(env);
  mkdirSync(pasta, { recursive: true, mode: 0o700 });
  const arq = join(pasta, `${sessao}.json`);
  const estado = existsSync(arq) ? JSON.parse(readFileSync(arq, "utf8")) : {};
  const { saida, estado: novo } = decidir({ input, estado });
  if (!saida) return;
  writeFileSync(arq, JSON.stringify(novo), { mode: 0o600 });
  limparAntigos(pasta, Date.now());
  process.stdout.write(JSON.stringify(saida));
}

function chamadoDireto() {
  try {
    return import.meta.url === pathToFileURL(realpathSync(process.argv[1])).href;
  } catch {
    return false;
  }
}

if (chamadoDireto()) {
  try {
    await cli(process.env);
  } catch {
    // Silêncio é a resposta segura de um hook.
  }
  process.exit(0);
}
