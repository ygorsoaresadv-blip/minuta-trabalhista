---
name: escrita
description: "Regras de escrita, formatação e estrutura de peças trabalhistas brasileiras: negrito, parênteses, citação de lei, súmula, OJ, tema e jurisprudência, ordem do mérito, parágrafos, marcas de pendência, rol de pedidos e fecho. Use SEMPRE que for redigir, revisar, adaptar, corrigir ou conferir petição inicial, contestação, réplica, contrarrazões (CRRO), recurso ordinário (RO) ou tese trabalhista, mesmo que o pedido não fale em estilo nem formatação ('faz a inicial', 'redige esse tópico', 'escreve a tese de horas extras', 'revisa essa contestação', 'como cito súmula', 'onde vai o negrito'). Para gerar o Word com o timbrado do escritório, combine com minuta:documento; para buscar teses nas petições do próprio escritório, com minuta:teses."
---

# Escrita trabalhista

Regras para escrever, formatar e estruturar peças trabalhistas. O objetivo é que a peça pareça escrita pelo escritório
e conduza o juiz até a conclusão.

## Antes de escrever: as três camadas

1. **Esta base**, igual para todos.
2. **Gosto pessoal** do advogado: `~/.claude/minuta/gosto.md`, se existir.
3. **Perfil do escritório**: `~/.claude/minuta/perfil.md`, se existir. Traz o nome do escritório, o advogado e a OAB, a
   cidade do fecho, a UF do endereçamento, o fecho fixo da inicial, o percentual de honorários e as regras próprias.

Leia o perfil e o gosto antes de redigir. Vale a camada mais específica: o pedido do advogado para a peça, depois o
perfil, depois o gosto pessoal, depois esta base. Onde esta base mostra `[ADVOGADO]`, `[OAB]`, `[CIDADE]`, `[UF]` ou
`[HONORÁRIOS]`, use o valor do perfil; sem perfil, deixe o marcador e avise. A pasta pode ser trocada pela variável de
ambiente `MINUTA_HOME`.

Sem perfil, sugira uma vez `/minuta:perfil`, que leva poucos minutos, e siga com os marcadores.

## Por onde começar

Descubra a peça e o lado, e leia o arquivo correspondente antes de escrever:

| Peça | Lado | Leia |
|---|---|---|
| Petição inicial ou tese de inicial | Reclamante | `references/peca-inicial.md` |
| Contestação ou tese de defesa | Reclamada | `references/peca-contestacao.md` |
| Réplica, contrarrazões ao RO (CRRO) ou recurso ordinário (RO) | Reclamante | `references/peca-replica-crro.md` |

Leia também, sempre que a tarefa tocar nesses assuntos:

- `references/citacoes-e-parenteses.md`: como citar lei, súmula, OJ, tema, julgado e prova, o que pode ir entre
  parênteses, aspas, chamadas de jurisprudência e fontes permitidas em cada peça.
- `references/negrito-e-formatacao.md`: o que sai em negrito (e quem marca), Word, títulos, recuos, bloco de
  jurisprudência, marcas coloridas, rol de pedidos e quadro de verbas.

Para buscar teses já escritas pelo escritório, use `minuta:teses`. Para gerar o `.docx`, use `minuta:documento`, que
abre o timbrado do perfil; não recrie o timbrado.

## Dois modos de trabalho

Descubra em qual você está, porque as regras mudam:

- **Adaptar texto do escritório** (tese da base, modelo, peça anterior): o texto jurídico fica palavra por palavra.
  Troque só os fatos do caso. Isso preserva o que o escritório já testou, e por isso a grafia antiga do texto não é
  padronizada. Retire o que não se aplica e nunca acrescente fundamento. Erro evidente de digitação não se repete, mas
  avise, porque a correção definitiva se faz na petição de origem.
- **Redigir texto novo** (tópico sem modelo, pedido do advogado): siga todos os padrões desta skill e use só fundamento
  verificado.

## Regras que valem em toda peça

**1. Nada inventado.** Fato, data, valor, prova, número de processo, Id, súmula e artigo vêm dos autos, dos documentos
ou de fonte oficial conferida. O que não se sabe vira marcador, para o advogado ver a lacuna em vez de assinar uma
suposição:

| Marcador | Quando |
|---|---|
| `[PENDENTE: o que falta]` | Inicial: dado do caso que falta |
| `[CONFIRMAR COM O CLIENTE: o que falta]` | Contestação: fato ou prova a confirmar com a empresa (repita a dúvida na lista de pendências) |
| `[DATA]` | Contestação: data desconhecida |
| `(INSERIR JURISPRUDÊNCIA AFIRMANDO ...)` | Inicial: parágrafo próprio, em caixa alta, dizendo o que o julgado deve afirmar. No máximo um por tópico, e nunca o julgado em si |
| `(SUGESTÃO DE TESE A REDIGIR: TEMA)` | Inicial: tese que falta na base, só sinalizada |

Em réplica, CRRO e RO, se faltar informação essencial, pare e pergunte em vez de presumir. O RO não sai com marcador:
o que não se confirma fica fora da peça e vai ao relatório final.

**2. Fundamento verificável.** Não cite de memória. Súmula, OJ e Tema só em vigor; artigo só com a lei certa. Sem
doutrina em texto novo. Julgado nunca é escrito de cabeça: ou vem copiado da fonte oficial, ou fica a recomendação
`(INSERIR JURISPRUDÊNCIA ...)`. As fontes aceitas em cada peça estão em `references/citacoes-e-parenteses.md`.

**3. Terceira pessoa, sempre.** Nada de "nós", "entendemos", "requeremos". O escritório fala pela parte: "a parte
reclamante requer", "a reclamada impugna", "Requer-se".

**4. Travessão proibido.** O "—" nunca aparece: use vírgula, ponto, dois-pontos, ponto e vírgula ou parênteses. A
`minuta:documento` recusa gerar o Word com ele. A meia-risca "–" só tem usos fixos: endereçamento ("– [UF]"),
complemento de título ("DAS HORAS EXTRAS – ESCALA 6X1") e "– sem destaque no original".

**5. Conduza o juiz.** Quem lê forma a impressão cedo e tende a confirmá-la. Por isso a premissa vem antes da
conclusão, a causa antes da consequência e o mais bem provado primeiro; cada parágrafo prepara o seguinte, para o pedido
chegar como consequência lógica do que veio antes. Isso vale para a estrutura da peça, para a ordem dos tópicos e para
dentro de cada tópico. A ordem do mérito, em degraus, está nos arquivos de cada peça.

**6. Parágrafos médios.** Em texto novo, de 4 a 10 linhas (cerca de 60 a 150 palavras), uma ideia em cada; maior só se a
ideia não couber. Parágrafo longo demais cansa o juiz. Na réplica e no RO vale o oposto: frases e parágrafos curtos.

**7. Conclusão separada.** O parágrafo do pedido é sempre o último do tópico e fica sozinho, com o pedido em negrito,
para o juiz achá-lo de relance ("Requer-se, portanto, ..."). O "por eventualidade" vai junto dele. Vale até para tópico
curto: argumento num parágrafo, pedido no outro.

**8. Um tópico por matéria, texto corrido.** Sem bullets, subtópicos, enumerações internas, rodapés nem links. Lista de
verbas vai na mesma frase, separada por vírgula, ou no quadro das verbas rescisórias. Sem floreio, repetição ou
introdução genérica: convença pelo argumento, não pelo volume.

**9. Negrito, em resumo.** Um único núcleo do pedido principal de cada tópico, nunca a frase inteira, e o cálculo de
horas completo. O resto (partes, valores, horas, datas, súmulas, temas, OJs) a `minuta:documento` destaca sozinha.
Detalhes e armadilhas em `references/negrito-e-formatacao.md`.

**10. Citação, em resumo.** Forma padrão: `art. 71, § 4º, da CLT`, `Súmula nº 338, III, do TST`. Súmula, OJ e Tema no
fim da frase, porque o negrito automático vai do número até o ponto final.

**11. Números.** Datas `02/08/2024`, valores `R$ 17.172,00`, horas `7h30` (nunca `7:30`), percentuais `50%`.

**12. Gênero e número.** Flexione "o reclamante / a reclamante" e as reclamadas conforme o caso. A forma "(a)" só existe
em referência de julgado ("Relator(a)"); na peça, resolva o gênero.

**13. Sigilo.** Dado de cliente (nome, CPF, endereço, fatos do caso) fica no caso. Nunca vai para a base de teses, para
o perfil, para o gosto pessoal nem para a busca de jurisprudência.

## Quando as fontes divergem

Vale esta ordem: o pedido do advogado para a peça; depois o perfil do escritório; depois o gosto pessoal; depois esta
base; por último, o costume dos textos antigos. Consequências práticas:

- **Negrito:** teses antigas costumam vir sem negrito. A regra atual manda usar negrito no pedido; a caixa alta do
  objeto do pedido é costume antigo, mantido só no texto literal adaptado.
- **Parágrafos:** teses antigas costumam ter de 1 a 3 parágrafos de períodos longos. Em texto novo vale a regra dos
  parágrafos médios com conclusão separada. Tese da inicial adaptada da base continua literal, sem redividir.
- **Doutrina:** algumas teses antigas citam autor. Em adaptação, fica como está; em texto novo, não entra.
- **Títulos:** sem numeração, salvo no RO, com tópicos em algarismos romanos.

## Conferência antes de entregar

- [ ] Nenhum "—" no texto.
- [ ] Nenhum fato, data, Doc., Id ou valor sem origem nos autos.
- [ ] Cada lacuna virou marcador, e nenhum marcador ficou esquecido na lista de pendências.
- [ ] Cada artigo, súmula, OJ e tema foi conferido; os que não foram estão avisados.
- [ ] Ordem dos tópicos conforme a peça, causa antes da consequência.
- [ ] Cada tópico termina no parágrafo do pedido, separado, com um só núcleo em negrito.
- [ ] Cada pedido do corpo está no rol, e cada item do rol tem fundamento no corpo (inicial).
- [ ] Cada pedido da inicial tem tópico próprio na defesa (contestação).
- [ ] Súmula, OJ e Tema no fim da frase, escritos por extenso ("Súmula", não "Súm.").
- [ ] Jurisprudência em bloco próprio, com a referência oficial; nada de TRT ou 1º grau onde a peça proíbe.
- [ ] Marcadores do perfil (`[ADVOGADO]`, `[OAB]`, `[CIDADE]`, `[UF]`, `[HONORÁRIOS]`) preenchidos ou avisados.
- [ ] Nada de dado de cliente em material que vá para a base de teses.
