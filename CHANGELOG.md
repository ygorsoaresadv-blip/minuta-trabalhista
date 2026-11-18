# Changelog

## 0.2.0 (2026-11-18)

- O plugin passa a se chamar `minuta` (antes `praxis`), e o repositório, `minuta-trabalhista`. Os comandos viram
  `/minuta:perfil`, `/minuta:lembrar` etc.
- A pasta pessoal passa a ser `~/.claude/minuta` e as variáveis, `MINUTA_HOME` e `MINUTA_STATE_DIR`. Quem já usava:
  renomeie `~/.claude/praxis` para `~/.claude/minuta`.

## 0.1.0 (2026-11-18)

Primeira versão.

- `minuta:escrita`: regras de escrita, formatação e estrutura de inicial, contestação, réplica, CRRO e RO.
- `minuta:documento`: gera o `.docx` sobre o timbrado do próprio escritório, com negrito e itálico automáticos.
- `minuta:teses`: monta a base de teses a partir das petições do advogado, anonimizada e só no computador dele, com
  relatório do que foi trocado e do que sobrou; busca e mostra a tese literal.
- `minuta:perfil` e `minuta:lembrar`: perfil do escritório e gosto pessoal, em `~/.claude/minuta`.
- Lembrete por hook quando o pedido é uma peça trabalhista.
- Testes de privacidade no CI: CPF, CNPJ, processo, OAB, telefone e e-mail só fictícios; nenhum documento ou base.
