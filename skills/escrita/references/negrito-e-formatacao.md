# Negrito e formatação

Os padrões visuais das peças do escritório. O Word é gerado pela skill `minuta:documento`, sobre o timbrado do perfil; aqui está o
que escrever e como marcar para ele sair certo.

## Sumário

1. Negrito: quem marca o quê
2. Como escolher o que vai em negrito
3. Armadilhas do negrito automático
4. Caixa alta, sublinhado e marca-texto
5. Formatação do Word
6. Títulos
7. Bloco de jurisprudência
8. Marcas que ficam na minuta
9. Rol de pedidos
10. Quadro das verbas rescisórias
11. Imagens de prova

## 1. Negrito: quem marca o quê

| O que | Como fica | Quem faz |
|---|---|---|
| Nome de parte, em qualquer menção | **NEGRITO + CAIXA ALTA** | Automático, pela lista `partes` do bloco `config`. Fora da lista: `[[Nome]]` |
| Núcleo do pedido principal de cada tópico | Negrito | Você, com `**...**` |
| Objeto principal de cada item do rol | Negrito | Você, com `**...**` |
| Cálculo de horas completo: `**(9h x 5 dias) - 44h = 1h semanal**` | Negrito na expressão inteira | Você, com `**...**` |
| Valores: `R$ 1.500,00`, com o extenso entre parênteses, se houver | Negrito | Automático |
| Horas e minutos: `8 horas`, `44h`, `2h30`, `15 minutos`, `08:00` | Negrito | Automático |
| Datas: `01/03/2020`, `15.05.2022`, `13 de outubro de 2026`, `1º de março de 2020`, `março de 2020` | Negrito | Automático |
| Súmula, OJ e Tema, do número até o ponto final da frase | Negrito em todo o trecho | Automático |

Designações como "reclamante", "reclamada", "autor" e "réu" não são nomes de parte: ficam em texto normal.

Não use `**` em mais nada. O que é automático não deve ser marcado à mão, e texto transcrito de jurisprudência não
recebe negrito automático.

## 2. Como escolher o que vai em negrito

O objetivo é o olho do juiz bater no que se pede. Um núcleo por pedido, nunca a frase inteira.

- Tópico da inicial: "Requer, portanto, seja deferido o pagamento de **horas extras** e reflexos."
- Tópico da contestação: "Requer-se a **improcedência do pedido de adicional de insalubridade** e reflexos."
- Item do rol: "o pagamento de **horas extras** excedentes à 8ª diária, com adicional de 50%;"
- Reflexos e pedidos gerais ficam sem negrito, salvo quando são o objeto do item: "a condenação em **honorários
  advocatícios**;"
- Se o tópico começa pelo pedido, o destaque vem no começo.

No julgado trazido por pesquisa, cita-se a ementa inteira e só o trecho que decide a questão vai em negrito (uma ou duas
frases). Julgado que já está na tese da base fica sem marcação nova.

## 3. Armadilhas do negrito automático

Conferidas no código da `minuta:documento`:

- **Súmula no meio da frase:** o negrito vai do número até o ponto final e pega tudo. "conforme a Súmula nº 338, III, do
  TST, o pedido procede." sai inteiro em negrito. Ponha a citação no fim ou divida a frase.
- **"Súm." não é reconhecida.** "Súm. 457 do C. TST" sai sem negrito. Escreva "Súmula".
- **Precisa de número:** "a súmula do TST" e "o tema da ação" não são destacados.
- **Pontos que não encerram a frase:** abreviações ("art.", "n.", "c.", "p.", "fls.") e milhar ("1.046").
- **Percentual e artigo não têm negrito automático:** "50%" e "art. 71, § 4º, da CLT" ficam normais.
- **Extenso de valor** entra no negrito se contiver "reais", "real" ou "centavos". O extenso do percentual, não.
- **`**` ou `[[` aberto** faz o Word não ser gerado.

## 4. Caixa alta, sublinhado e marca-texto

- **Caixa alta:** títulos, nomes das partes, marcas de pendência entre parênteses e o início da ementa. Nas teses
  antigas, a caixa alta também destaca o objeto do pedido ("A CONCESSÃO DOS BENEFÍCIOS DA JUSTIÇA GRATUITA"): mantenha
  em adaptação, não reproduza em texto novo.
- **Réplica** aceita mais destaque, com parcimônia, de 4 a 6 vezes na peça: marca-texto amarelo + negrito no nome de cada
  documento impugnado e na frase-chave da contradição da defesa; sublinhado + negrito na expressão decisiva de um
  parágrafo; título `DA CONCLUSÃO` sublinhado.
- **RO:** marca-texto amarelo + negrito só na frase-chave que resume a contradição da sentença, no máximo 4 a 6 vezes na
  peça.
- **Nunca:** "!!!", mesmo que apareça em texto antigo.

## 5. Formatação do Word

| Item | Padrão |
|---|---|
| Fonte | Times New Roman 12 |
| Fonte da jurisprudência | Times New Roman 10 |
| Entrelinha | 1,2 |
| Espaço entre parágrafos | Uma linha, embutida no parágrafo; não insira linhas vazias |
| Alinhamento | Só justificado ou centralizado, nada à esquerda ou à direita |
| Recuo de primeira linha | 2,5 cm no corpo do texto |
| Sem recuo | Títulos, endereçamento, "Processo nº", "Termos em que,", "pede deferimento.", data, assinatura |
| Centralizado | Nome e OAB do advogado, nome da ação, títulos de seção indicados em cada peça |
| Timbrado | O timbrado do perfil (`minuta:documento`), nunca recriado |

Exceção: o que o advogado formatar à mão (fonte, tamanho, alinhamento, lista, grifo) fica como ele deixou.

Cada parágrafo é um bloco; não use quebra de linha dentro do texto. Antes de entregar o `.docx`, converta em PDF ou
imagens e confira timbrado, justificação, recuos e quebras de página.

## 6. Títulos

Caixa alta, em negrito, sem numeração romana, em geral iniciados por DO, DA, DOS ou DAS: "DA MULTA NORMATIVA", "DO
INTERVALO INTRAJORNADA E REFLEXOS". Acrescente "E REFLEXOS" quando houver verbas acessórias. Complemento depois de
meia-risca: "DAS HORAS EXTRAS – NULIDADE DO REGIME 12X36", "DA JUSTIÇA GRATUITA – TEMA 21 DO C. TST". O RO é a exceção:
seus tópicos levam algarismos romanos.

**Todo título de tópico é justificado, sempre**, sem recuo, em qualquer peça: inclusive
PRELIMINARMENTE, DA IMPUGNAÇÃO AOS PEDIDOS, NO MÉRITO, DOS REQUERIMENTOS, DAS PRELIMINARES e DA CONCLUSÃO.
Centralizados só o endereçamento e o nome da peça (RECLAMAÇÃO TRABALHISTA, CONTESTAÇÃO), que não são tópicos.

## 7. Bloco de jurisprudência

Ementa, acórdão, súmula ou tese transcrita vai em bloco próprio (`jurisprudencia` na `minuta:documento`): fonte 10, recuo de
2,5 cm em **todas** as linhas, sem negrito automático. Se o trecho estiver dentro de um parágrafo maior, separe: texto
do advogado em parágrafo comum, transcrição em bloco. Como chamar e como fechar o bloco está em
`references/citacoes-e-parenteses.md`.

## 8. Marcas que ficam na minuta

| Marca | Na minuta |
|---|---|
| `[PENDENTE: ...]`, `[CONFIRMAR ...]` | Amarelo |
| `(INSERIR JURISPRUDÊNCIA ...)`, `(SUGESTÃO DE TESE A REDIGIR: ...)` | Vermelho e negrito |
| Citação que não estava no modelo adaptado | Vermelho |
| Menção a TRT ou 1º grau na contestação | Rosa |
| Jurisprudência de pesquisa nova | Grifo verde |

Essas marcas são para o advogado resolver antes do protocolo; a peça não sai com elas.

## 9. Rol de pedidos

Só a inicial tem rol. Padrão do escritório:

- Abre com o título DOS PEDIDOS e "Diante do exposto, requer a parte reclamante:".
- Pedido principal: alínea `a)`, `b)`... em negrito, gerada pela `minuta:documento` (bloco `pedido`).
- Reflexos: recuados, com `a.`, `b.` em negrito, recomeçando em cada pedido.
- Texto justificado, terminado em ponto e vírgula, sem a letra escrita no texto.
- Pontos pontilhados até o valor, em negrito, alinhado à margem direita.

| Tipo de pedido | Valor |
|---|---|
| Com expressão econômica | `R$ 0,00`; sem cálculo ainda, `R$ [PENDENTE]` |
| Sem valor (perícia, aplicação de CCT, retificação, ofícios, entrega de guias) | `A deferir` |
| Gerais (justiça gratuita, estimativa, inversão do ônus, dedução, recolhimentos) | Vazio |

O rol segue a ordem dos tópicos, cada pedido seguido dos reflexos discriminados, um por item. Não crie pedido que não
esteja fundamentado no corpo. O rol termina no último pedido; o que vem depois é o fecho (`references/peca-inicial.md`).

## 10. Quadro das verbas rescisórias

Sempre que a inicial pede verbas rescisórias, elas não saem como pedidos soltos, qualquer que seja o motivo do fim do
contrato. Primeiro o item-cabeça, terminado em dois-pontos. Na rescisão indireta:

> Requer o reconhecimento da rescisão indireta do contrato de trabalho, nos termos do art. 483, [alíneas invocadas], da
> CLT, e a condenação da parte reclamada ao pagamento das verbas rescisórias conforme discriminado a seguir:

Na justa causa:

> Requer a declaração de nulidade da justa causa aplicada, com sua reversão em dispensa sem justa causa, e a condenação
> da parte reclamada ao pagamento das verbas rescisórias conforme discriminado a seguir:

No pedido de demissão, "Requer a conversão do pedido de demissão em rescisão indireta do contrato de trabalho, nos
termos do art. 483, [alíneas invocadas], da CLT, e a condenação..."; nas diferenças, "...ao pagamento das diferenças de
verbas rescisórias conforme discriminado a seguir:"; nos demais casos, "Requer a condenação da parte reclamada ao
pagamento das verbas rescisórias conforme discriminado a seguir:".

Depois, o quadro, que sai no rol e no fim do tópico "Das verbas rescisórias" (sem esse tópico, no fim do tópico que
discute o fim do contrato e pede as verbas):

| Verbas Rescisórias | Proporção | Valores |
|---|---|---|
| Saldo de Salário | 29 dias | R$ |
| Aviso prévio indenizado | 36 dias | R$ |
| Férias vencidas + 1/3 | 2 Períodos | R$ |
| Férias Proporcionais + 1/3 - 2026/27 | 5/12 Avos | R$ |
| 13º Sal. Proporcional - 2026 | 11/12 Avos | R$ |
| Multa de 40% do FGTS | 40% | R$ |
| **Total a ser pago** | | **R$** |

No Word, sai do bloco `tabela` da `minuta:documento`. Formato: Arial 11 centralizado, cabeçalho e total em cinza (BFBFBF), colunas de 6,8 + 3,4 + 3,4 cm, recuo de 1,25 cm no
rol. Ficam fora do quadro, como pedidos próprios depois dele: multas dos arts. 467 e 477, depósitos do FGTS, liberação
das guias e seguro-desemprego.

## 11. Imagens de prova

**Contestação:** o parágrafo que apresenta a prova termina em dois-pontos e a imagem entra logo depois, centralizada.
No máximo 6 recortes na peça, com 14 cm de largura.

**Réplica:** no máximo 1 a 2 recortes por tópico, só os que decidem o ponto. Imagem a 300 dpi, só o trecho relevante,
sem alterar o conteúdo, girada quando preciso. Quadro vermelho (RGB 220,0,0, linha de 6 a 7 px em 2000 px de largura) em
volta do trecho decisivo, sem tapar texto; nunca outra cor. Sem legenda: o parágrafo já diz o que a imagem prova, com o
nome do documento e o Id. Largura: espelhos de ponto e tabelas largas com cerca de 17 cm; documentos em retrato, avisos
e recibos, de 14 a 14,5 cm; faixas de uma linha, 15 cm. Se ficar ilegível, não insira e avise.

**RO:** a mesma técnica, com 1 a 3 recortes por tópico, logo depois do parágrafo que os explica: sentença que contradiz a
si mesma, linha da ata ou do depoimento, quadro do laudo, página do ponto, post. Trechos de sentença ou laudo com cerca de
14 cm; ponto e tabelas largas com cerca de 17 cm; sempre centralizados. Confira se não há imagem vazia ou quebrada no Word.
