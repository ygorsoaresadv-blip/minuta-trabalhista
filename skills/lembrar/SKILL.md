---
name: lembrar
description: "Guarda uma correção ou preferência do advogado para não ter de repeti-la: no perfil do escritório (~/.claude/minuta/perfil.md) ou no gosto pessoal (~/.claude/minuta/gosto.md). Use quando ele disser 'lembra disso', 'guarda essa regra', 'sempre faça assim', 'nunca mais escreva X', ou corrigir a mesma coisa pela segunda vez numa peça."
argument-hint: "<regra>"
---

# Lembrar

Guarda a regra que o advogado deu, para valer nas próximas peças.

1. Escreva a regra numa frase, no imperativo, sem dado de cliente. Ex.: "Título de tópico sempre justificado." Se a
   correção veio de um caso concreto, generalize: tire nomes, valores e datas do caso.
2. Decida onde ela vai:
   - **Perfil do escritório** (`~/.claude/minuta/perfil.md`, seção "Regras próprias"): vale para as peças deste
     escritório (fecho, assinatura, ordem de tópicos, estilo da casa).
   - **Gosto pessoal** (`~/.claude/minuta/gosto.md`): vale para o advogado em qualquer escritório (jeito de escrever,
     formatação que ele prefere, fluxo de trabalho).
   Na dúvida, pergunte em uma linha.
3. Se o arquivo não existir, crie a partir de `templates/gosto.md` desta skill ou de `minuta:perfil`.
4. Se já houver regra parecida, atualize a antiga em vez de duplicar; se a nova contradiz a antiga, troque e avise.
5. Acrescente a data no fim da linha: "(18/11/2026)".
6. Confirme em uma linha o que foi guardado e onde.

Se a regra contradiz a base do plugin, ela vence para este advogado. Se parecer erro jurídico (citar súmula cancelada,
por exemplo), avise antes de guardar.
