# Formato do conteudo.json

Lista JSON de blocos, na ordem do documento. Cada bloco vira um parágrafo do Word.

## Tipos de bloco

| `type` | Para quê | Padrões |
|---|---|---|
| `paragraph` | Texto comum | justificado, recuo de primeira linha |
| `heading` | Título | centralizado, negrito, sem recuo |
| `jurisprudencia` | Ementa, súmula ou tese transcrita | fonte menor, recuo em todas as linhas, sem destaque automático |
| `spacer` | Respiro extra (antes da assinatura, por exemplo) | linha vazia |
| `config` | Não vira texto: `{"type": "config", "partes": ["Nome", "Empresa Ltda"]}` | |

Todo `paragraph` e `heading` já sai com uma linha de espaço depois. Não use `spacer` entre blocos comuns.

## Campos

| Campo | Tipos | Padrão | Descrição |
|---|---|---|---|
| `text` | paragraph, heading, jurisprudencia | | Texto do bloco |
| `runs` | paragraph, jurisprudencia | | `[{"text": "...", "bold": true, "italic": false, "underline": false}]`, para misturar formatação |
| `align` | todos | ver acima | `justify` ou `center`. Qualquer outro valor vira justificado |
| `indent` | todos | ver acima | Recuo de primeira linha (em `jurisprudencia`, recuo de todas as linhas) |
| `bold`, `italic`, `underline` | paragraph, heading | | Aplica ao bloco inteiro |
| `upper` | heading | `false` | Caixa alta |
| `auto_negrito` | paragraph, heading, jurisprudencia | `true` (`false` em jurisprudencia) | Liga ou desliga os destaques automáticos no bloco |

## Marcações dentro do texto

| Marcação | Resultado |
|---|---|
| `**trecho**` | Negrito: núcleo do pedido, cálculo de horas completo |
| `[[Nome da Parte]]` | NEGRITO + CAIXA ALTA, para parte que não está em `config.partes` |
| `*expressão*` | Itálico, para expressão estrangeira que o script não reconhece |
| Automático: nomes de `config.partes` | NEGRITO + CAIXA ALTA |
| Automático: `R$ 1.500,00` e o extenso entre parênteses | Negrito |
| Automático: `8 horas`, `44h`, `2h30`, `15 minutos`, `08:00` | Negrito |
| Automático: `01/03/2020`, `13 de outubro de 2026`, `março de 2020` | Negrito |
| Automático: `Súmula nº 338...`, `Tema 1.046...`, `OJ 394 da SDI-1...` | Negrito do número até o ponto final da frase |
| Automático: `in verbis`, `data venia`, `home office`, `burnout` e outras | Itálico |

O script recusa gerar o Word se houver travessão (—) ou `**` / `[[` sem fechar.

## Exemplo

```json
[
  {"type": "config", "partes": ["Fulana de Tal", "Empresa Exemplo Ltda"]},
  {"type": "paragraph", "text": "AO JUÍZO DA __ª VARA DO TRABALHO DE [CIDADE] – [UF]", "indent": false},
  {"type": "paragraph", "text": "Fulana de Tal, brasileira, [qualificação], por seu advogado que esta subscreve, vem, respeitosamente, propor a presente:", "indent": false},
  {"type": "heading", "text": "RECLAMAÇÃO TRABALHISTA"},
  {"type": "paragraph", "text": "em face de Empresa Exemplo Ltda, inscrita no CNPJ sob o nº [CNPJ], pelas razões de fato e de direito adiante expostas e articuladas:", "indent": false},
  {"type": "heading", "text": "DAS HORAS EXTRAS E REFLEXOS", "align": "justify"},
  {"type": "paragraph", "text": "A reclamante trabalhava das 8h às 18h, apurando-se **(9h x 5 dias) - 44h = 1h semanal**."},
  {"type": "paragraph", "text": "Este é o entendimento consolidado, in verbis:"},
  {"type": "jurisprudencia", "text": "[Ementa copiada da fonte oficial.] (TST, ...) – sem destaque no original"},
  {"type": "paragraph", "text": "Requer, portanto, a condenação da reclamada ao pagamento de **horas extras** e reflexos."},
  {"type": "heading", "text": "DOS PEDIDOS", "align": "justify"},
  {"type": "paragraph", "text": "Diante do exposto, requer a parte reclamante:"},
  {"type": "paragraph", "indent": false, "text": "a) o pagamento de **horas extras** excedentes à 8ª diária, com adicional de 50%;"},
  {"type": "spacer"},
  {"type": "paragraph", "text": "Termos em que,", "indent": false},
  {"type": "paragraph", "text": "pede deferimento.", "indent": false},
  {"type": "paragraph", "text": "[CIDADE], [data por extenso].", "indent": false},
  {"type": "spacer"},
  {"type": "paragraph", "text": "[ADVOGADO]", "align": "center", "indent": false, "bold": true},
  {"type": "paragraph", "text": "[OAB]", "align": "center", "indent": false, "bold": true}
]
```

Nome e OAB em dois blocos: o script não trata `\n` como quebra de linha. Títulos de tópico ficam justificados
(`"align": "justify"`); centralizados, só o nome da peça e a assinatura.
