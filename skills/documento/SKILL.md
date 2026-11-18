---
name: documento
description: "Gera a peça trabalhista em Word (.docx) sobre o timbrado do próprio escritório, com a formatação de peça: fonte, entrelinha, recuos, bloco de jurisprudência em fonte menor e negrito automático de partes, valores, horas, datas, súmulas, OJs e temas. Use sempre que o advogado pedir o Word, o .docx, 'no timbrado', 'pronto para protocolo' ou 'passa a limpo', e ao fim de uma peça redigida com minuta:escrita. Também para configurar ou testar o timbrado do escritório."
---

# Documento no timbrado do escritório

O script `scripts/gerar_docx.py` monta o `.docx` a partir de uma lista de blocos em JSON. Ele usa o timbrado do próprio
escritório: um `.docx` comum, com logo e dados no cabeçalho e no rodapé. O corpo do timbrado é apagado; cabeçalho,
rodapé, margens e numeração ficam como estão.

Requisitos: Python 3.9+ e `python-docx` (`pip install python-docx`). Se faltar, peça licença para instalar.

## Onde está o timbrado

O script procura, nesta ordem:

1. o argumento `--timbrado caminho.docx`;
2. o campo `timbrado:` no topo do perfil (`~/.claude/minuta/perfil.md`);
3. `~/.claude/minuta/timbrado.docx`;
4. nenhum: gera em folha branca, com as margens do perfil, e avisa.

`~/.claude/minuta` pode ser trocada pela variável `MINUTA_HOME`. O timbrado fica fora de qualquer repositório.

## Configurar o timbrado (primeira vez)

1. Peça ao advogado o caminho do `.docx` com o timbrado. Se ele só tiver uma peça antiga no timbrado, sirva-se dela: o
   script apaga o corpo e mantém cabeçalho e rodapé. PDF ou imagem não servem; peça o Word.
2. Copie para `~/.claude/minuta/timbrado.docx` (crie a pasta se faltar). Não mova o original.
3. Gere a página de teste:
   `python "<pasta da skill>/scripts/gerar_docx.py" --testar "<pasta de trabalho>/teste-timbrado.docx"`
4. Se puder, converta em PDF ou imagem e confira cabeçalho, rodapé, margens e o texto justificado. Mostre ao advogado.
5. Se a fonte, o tamanho, a entrelinha ou o recuo do escritório forem outros, grave no topo do perfil (veja
   `/minuta:perfil`): `fonte`, `tamanho`, `tamanho_jurisprudencia`, `entrelinha`, `recuo_cm`, `margens_cm`.

## Gerar a peça

1. Monte o `conteudo.json` conforme `references/formato-do-conteudo.md`, numa pasta temporária, nunca dentro de um
   repositório. Ponha os nomes das partes em `config.partes`.
2. Preencha `[ADVOGADO]`, `[OAB]`, `[CIDADE]` e `[UF]` com o perfil. Sem perfil, deixe os marcadores e avise.
3. Rode:
   `python "<pasta da skill>/scripts/gerar_docx.py" conteudo.json "<pasta do caso>/Peça.docx"`
4. Se o script recusar (travessão, `**` aberto), corrija o texto, não o script.
5. Antes de entregar, converta em PDF ou imagens e confira timbrado, justificação, recuos e quebras de página.
6. Entregue o caminho do `.docx` e apague o `conteudo.json` temporário: ele tem dados do caso.

## Regras fixas

- Só dois alinhamentos: justificado e centralizado.
- Travessão (—) proibido.
- Jurisprudência em bloco próprio, fonte menor, recuo em todas as linhas e sem negrito automático.
- O que o advogado formatou à mão num texto colado fica como ele deixou: passe por `runs`.
