---
name: teses
description: "Monta, confere e consulta a base de teses do próprio escritório, tirada das petições do advogado e anonimizada no computador dele. Use quando o advogado quiser 'montar minha base de teses', 'importar minhas petições', 'anonimizar minhas iniciais', e sempre que for redigir inicial ou contestação com praxis:escrita e precisar da tese que o escritório já usa ('tem tese de intervalo?', 'usa a nossa tese de horas extras', 'qual o pedido padrão de insalubridade')."
---

# Base de teses do escritório

A base é feita das petições do próprio advogado, anonimizada e guardada só no computador dele, em
`~/.claude/praxis/teses/<tipo>/base-teses.json` (ou `PRAXIS_HOME`). Ela nunca vai para repositório, para o perfil nem
para a internet. Este plugin não traz teses prontas.

Requisitos: Python 3.9+ e `python-docx`. Para `.doc` antigo, LibreOffice.

## Montar a base

1. Pergunte a pasta com as petições `.docx` e se são iniciais ou contestações. Quanto mais petições, melhor; uma
   tese aparece em várias e o script fica com as duas versões mais recentes. O nome do arquivo pode começar pela data
   (`2026.03.15 ...`); sem isso, vale a data de modificação.
2. Rode:
   `python "<pasta da skill>/scripts/montar_base.py" "<pasta das petições>" --tipo inicial`
   Subpasta que não deve entrar: `--ignorar "TRECHO DO NOME"`. O script recusa gravar dentro de um repositório Git.
3. **Leia o relatório** `relatorio-anonimizacao.md` com o advogado. Ele mostra o que foi trocado por marcador e o
   que parece nome de pessoa ou empresa e ficou. Para cada dado pessoal que sobrou, acrescente o termo, um por linha, em
   `~/.claude/praxis/anonimizar-extra.txt` e rode de novo. Repita até o relatório ficar limpo.
4. Diga quantas teses e linhas de pedido a base tem e onde está.

O que o script anonimiza: nome do cliente e das empresas da qualificação (e partes soltas do nome do cliente), CPF,
CNPJ, RG, PIS, CTPS, e-mail, telefone, CEP, endereço, número de processo e OAB. Tópicos de fatos do caso (DOS FATOS,
DO CONTRATO, competência territorial) ficam fora por padrão, porque são quase só dados do cliente; `--incluir-fatos`
os traz, com mais risco. Valores, datas e funções ficam, porque fazem parte do texto da tese; o advogado decide se
algum deles identifica o caso.

## Usar a base ao redigir

1. Busque:
   `python "<pasta da skill>/scripts/buscar_teses.py" "intervalo intrajornada" --tipo inicial`
   Lista de títulos: `--listar`. Linhas de pedido do rol: `--pedidos "horas extras"`.
2. Abra a tese escolhida: `--mostrar t012`. Vêm a versão mais recente e a anterior, com o texto literal; recuo indica
   bloco de jurisprudência.
3. Adapte pelas regras de `praxis:escrita` (modo "adaptar texto do escritório"): texto jurídico palavra por palavra,
   troca só dos fatos, marcadores como `[RECLAMANTE]` e `[1ª RECLAMADA]` viram os dados do caso, fato que falta vira
   `[PENDENTE: ...]`.
4. Tese que não está na base: siga `praxis:escrita` (tese nova enxuta) ou sinalize `(SUGESTÃO DE TESE A REDIGIR: ...)`.

## Nunca

- Copiar a base, ou trecho dela com dado de cliente, para repositório, issue, e-mail ou site.
- Usar nome de cliente como termo de busca de jurisprudência.
- Acrescentar à base texto com fato de cliente sem anonimizar.
