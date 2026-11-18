---
name: perfil
description: "Cria ou atualiza o perfil do escritório em ~/.claude/praxis/perfil.md: nome, advogado e OAB, cidade e UF, honorários, fecho da inicial, timbrado, fonte e recuos, regras próprias. Use quando o advogado pedir para configurar o praxis, 'cadastrar meu escritório', 'configurar meu timbrado', 'mudar a fonte das peças', ou quando praxis:escrita ou praxis:documento acharem o perfil faltando."
---

# Perfil do escritório

O perfil é a camada do escritório: vale por cima da base do plugin e do gosto pessoal. Fica em
`~/.claude/praxis/perfil.md` (ou `PRAXIS_HOME/perfil.md`), fora de qualquer repositório.

## Criar

1. Se o perfil já existe, leia e só atualize o que o advogado pedir. Não sobrescreva.
2. Copie `templates/perfil.md` para `~/.claude/praxis/perfil.md`, criando a pasta se faltar.
3. Pergunte de uma vez, numa mensagem só, o que não der para descobrir sozinho:
   - nome do escritório, advogado que assina e OAB (ex.: `OAB/SP nº 000.000`);
   - cidade do fecho e UF do endereçamento;
   - percentual de honorários de sucumbência que costuma pedir;
   - onde está o timbrado (`.docx`) e, se quiser, uma peça antiga para tirar o fecho da inicial e a formatação.
   Se ele mandar uma peça antiga, tire dela o fecho, a fonte, o tamanho, a entrelinha e o recuo, em vez de perguntar.
4. Preencha os campos do topo (entre `---`). Valores sempre entre aspas. Apague a linha do que não se aplica.
5. Timbrado: copie o arquivo para `~/.claude/praxis/timbrado.docx` e siga "Configurar o timbrado" em
   `praxis:documento`, gerando a página de teste.
6. Mostre o perfil pronto e diga onde ficou.

## Atualizar

Regras novas vão em "Regras próprias", uma por linha, com a data. Para guardar correções no meio do trabalho, use
`praxis:lembrar`.

## Nunca

- Dado de cliente no perfil.
- Gravar o perfil dentro de um repositório.
