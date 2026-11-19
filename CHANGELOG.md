# Changelog

## 0.4.0 (2026-11-18)

- `minuta:documento` monta o rol de pedidos (bloco `pedido`: letra em negrito, reflexos recuados que recomeçam a cada
  pedido, pontilhado até o valor na margem direita) e o quadro das verbas rescisórias (bloco `tabela`: Arial 11,
  cabeçalho e total em cinza, colunas de 6,8 + 3,4 + 3,4 cm). Antes, os dois tinham de ser ajustados à mão no Word.
- O agente `minuta:redator` usa os blocos novos e, se não puder rodar os scripts, deixa o `conteudo.json` e os comandos
  exatos no relatório, em vez de parar.
- Testado de ponta a ponta num caso fictício: a minuta saiu sem erro na conferência e com as divergências e lacunas do
  caso apontadas no relatório.

## 0.3.0 (2026-11-18)

- Agente `redator`: redige a peça inteira de um caso a partir dos documentos (leitura, mapa, teses da base, redação,
  conferência, Word no timbrado e relatório de pendências na pasta do caso).
- `skills/escrita/scripts/conferir.py`: conferência mecânica do `conteudo.json` antes do Word, com erros (travessão,
  primeira pessoa, negrito aberto, "Súm.", folhas em réplica/CRRO/RO, marcador no RO, inicial sem rol) e avisos
  (pendências, tópico sem pedido em negrito, dados do perfil sem preencher, parágrafo longo, hora "7:30", "(a)").
- O lembrete do hook passa a indicar o agente para a peça inteira.

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
