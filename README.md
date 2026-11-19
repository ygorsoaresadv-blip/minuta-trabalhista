# minuta-trabalhista

Base de redação de peças trabalhistas para o Claude Code.

O Claude escreve petição que funciona, mas a primeira versão raramente parece do escritório: súmula citada de memória,
pedido sem destaque, tópico que termina sem pedir, travessão, fundamento inventado. O `minuta` dá ao Claude as regras
de escrita de peças trabalhistas, gera o Word no **seu** timbrado e consulta a **sua** base de teses, montada a partir
das suas próprias petições e anonimizada no seu computador.

Nada do seu escritório sai do seu computador: perfil, timbrado e teses ficam em `~/.claude/minuta`, fora de qualquer
repositório.

## Instalar

No Claude Code:

```
/plugin marketplace add ygorsoaresadv-blip/minuta-trabalhista
/plugin install minuta@minuta-trabalhista
```

Ou pela linha de comando:

```
claude plugin marketplace add ygorsoaresadv-blip/minuta-trabalhista
claude plugin install minuta@minuta-trabalhista
```

Requisitos: Python 3.9 ou mais novo e `pip install python-docx`. Para petições antigas em `.doc`, LibreOffice.

## Primeiros passos

1. `/minuta:perfil`: cadastra o escritório (advogado, OAB, cidade, honorários, fecho da inicial) e o timbrado.
2. Peça ao Claude: "monta minha base de teses com as iniciais da pasta X". Leia o relatório de anonimização.
3. Peça a peça: "faz a inicial deste caso com os documentos da pasta Y". O agente redator lê os documentos, redige,
   confere e entrega o Word e um relatório de pendências.

## O que tem

| Skill | O que faz |
|---|---|
| `minuta:escrita` | Regras de escrita, formatação e estrutura de inicial, contestação, réplica, contrarrazões (CRRO) e recurso ordinário: ordem do mérito, citação de lei, súmula, OJ, tema e julgado, negrito, parágrafos, marcas de pendência, rol de pedidos, quadro de verbas rescisórias. Carrega sozinha quando o pedido é uma peça. |
| `minuta:documento` | Gera o `.docx` sobre o timbrado do escritório. Negrito automático de partes, valores, horas, datas, súmulas, OJs e temas; itálico automático de expressões latinas e estrangeiras; bloco de jurisprudência em fonte menor; recusa travessão. Fonte, tamanho, entrelinha e recuo vêm do perfil. |
| `minuta:teses` | Monta a base de teses a partir das suas petições `.docx`, troca dados pessoais por marcadores e entrega um relatório do que trocou e do que parece ter sobrado. Busca e mostra a tese literal para adaptar. |
| `minuta:perfil` | Cria o perfil do escritório em `~/.claude/minuta/perfil.md`. |
| `minuta:lembrar` | Guarda uma correção sua no perfil do escritório ou no seu gosto pessoal, para não repetir. |

## Agente redator

Para a peça inteira de um caso, o Claude delega ao agente `minuta:redator`. Ele trabalha sozinho, do começo ao fim:

1. lê os documentos do caso (relato, CTPS, holerites, cartões de ponto, TRCT, inicial, contestação, sentença);
2. monta o mapa da peça: pedidos na ordem do mérito, prova de cada um, divergências entre documentos;
3. busca na sua base as teses de cada tópico e adapta em modo literal; o que não está na base vira texto novo enxuto;
4. redige pelas regras de `minuta:escrita` e com os dados do seu perfil;
5. confere com `conferir.py` (travessão, primeira pessoa, "Súm.", folhas onde se cita Id, tópico sem pedido em negrito,
   pendências) e com a lista de conferência;
6. gera na pasta do caso `Minuta - <Peça> - <data>.docx` e o relatório com as pendências, sem sobrescrever nada.

O agente roda os scripts em Python: na primeira vez, o Claude Code pede licença para executar `python`. Sem essa
licença, ele entrega a minuta em `conteudo.json` com os dois comandos para conferir e gerar o Word.

O que falta nos documentos vira marcador na peça e item no relatório: o agente não inventa nem pergunta no meio do
caminho. Ele não protocola, não envia nada a ninguém e não leva dado do caso para a base de teses ou para a internet.
Inicial, contestação, réplica, contrarrazões e recurso ordinário.

A conferência também roda sozinha, sobre qualquer minuta:

```
python skills/escrita/scripts/conferir.py conteudo.json --peca inicial
```

## Três camadas

1. **Base**: este plugin, igual para todos.
2. **Gosto pessoal**: `~/.claude/minuta/gosto.md`, suas regras em qualquer escritório.
3. **Perfil do escritório**: `~/.claude/minuta/perfil.md`, com o timbrado em `~/.claude/minuta/timbrado.docx`.

Vale a camada mais específica: o seu pedido para a peça, depois o perfil, depois o gosto, depois a base. A pasta pode
ser trocada pela variável de ambiente `MINUTA_HOME`.

## Timbrado próprio

Qualquer `.docx` do escritório com logo e dados no cabeçalho e no rodapé serve, inclusive uma peça antiga: o corpo é
apagado e cabeçalho, rodapé, margens e numeração ficam. Sem timbrado, a peça sai em folha branca.

```
python skills/documento/scripts/gerar_docx.py --testar teste.docx --timbrado "C:\caminho\timbrado.docx"
```

## Base de teses própria

```
python skills/teses/scripts/montar_base.py "C:\pasta\das\iniciais" --tipo inicial
python skills/teses/scripts/buscar_teses.py "intervalo intrajornada"
python skills/teses/scripts/buscar_teses.py --mostrar t012
```

A anonimização troca nome do cliente e das empresas da qualificação, CPF, CNPJ, RG, PIS, CTPS, e-mail, telefone, CEP,
endereço, número de processo e OAB. Tópicos de fatos do caso ficam fora por padrão. Ela é automática e **pode falhar**:
leia sempre o `relatorio-anonimizacao.md` e acrescente o que sobrar em `~/.claude/minuta/anonimizar-extra.txt`, um
termo por linha. O script recusa gravar a base dentro de um repositório Git.

## Privacidade

- O plugin não envia nada a lugar nenhum. O que o Claude lê numa conversa segue as regras da sua conta do Claude.
- Perfil, gosto, timbrado e base ficam em `~/.claude/minuta`.
- Este repositório tem testes que barram CPF, CNPJ, número de processo, OAB, telefone e e-mail que não sejam fictícios,
  e qualquer `.docx`, `.pdf` ou base de teses.

## Aviso

O `minuta` ajuda a redigir; quem assina é o advogado. Confira fatos, fundamentos, prazos e a vigência de cada súmula,
OJ e tema antes de protocolar. Não é aconselhamento jurídico.

## Desenvolvimento

```
pip install python-docx
npm test
claude plugin validate . --strict
```

Para testar uma cópia local numa sessão: `claude --plugin-dir caminho/para/minuta-trabalhista`.

Para checar termos que nunca podem ir ao repositório (nomes de clientes, do escritório), crie `tests/lista-negra.txt`,
um termo por linha. O arquivo fica fora do Git e o teste de privacidade passa a usá-lo.

## Licença

MIT
