# Histórico de iterações do prompt v2

Todas as execuções usaram o provider OpenRouter (cliente OpenAI com `OPENAI_BASE_URL`), `LLM_MODEL=google/gemini-3.1-flash-lite` e `EVAL_MODEL=google/gemini-3.8-flash`, contra o dataset `mba-ia-pull-evaluation-prompt-eval` (15 exemplos).

**Dataset público com todos os experimentos:** https://smith.langchain.com/public/cbe668f1-d5ee-4caa-856a-b7c3f178895b/d

## Resumo

| Execução | Data | Helpfulness | Correctness | F1-Score | Clarity | Precision | Média | Menor F1 por exemplo | Experimento |
|---|---|---|---|---|---|---|---|---|---|
| Linha de base: v1 original | 2026-10-11 | 0.99 | 0.92 | 0.86 | 0.99 | 0.98 | 0.9487 | 0.66 | `leonanluppi-bug_to_user_story_v1-52858a2a` |
| Iteração 1 | 2026-10-11 | 0.99 | 0.93 | 0.87 | 0.99 | 0.98 | 0.9533 | 0.79 | `ricardorauber-bug_to_user_story_v2-b05d9ff2` |
| Iteração 2 | 2026-10-11 | 0.99 | 0.93 | 0.88 | 0.99 | 0.98 | 0.9532 | 0.75 | `ricardorauber-bug_to_user_story_v2-e4365069` |
| **Iteração 3 (final)** | 2026-10-11 | **0.99** | **0.95** | **0.90** | **0.99** | **0.99** | **0.9638** | **0.82** | `ricardorauber-bug_to_user_story_v2-a2920cdc` |

A linha de base foi obtida rodando as funções do `src/evaluate.py` (sem alterá-lo) com o prompt `leonanluppi/bug_to_user_story_v1`, para comparar v1 e v2 no mesmo dataset e com os mesmos modelos.

## Linha de base: v1 original

Com os modelos atuais, o v1 já passa no critério de 0.8. Os problemas dele aparecem no formato e na consistência, não na média:

- Abre com frases como "Aqui está a user story estruturada..." e fecha com comentários.
- Usa Markdown carregado (títulos `###`, negrito, checkboxes `[ ]`) em 15 de 15 respostas, em vez do formato de texto do gabarito.
- Escreve "Critérios de Aceite" como lista solta, sem o padrão Dado/Quando/Então.
- Acrescenta "Notas Técnicas" com hipóteses de investigação que não estão no relato.
- Varia muito entre exemplos: o pior F1 foi 0.66, no bug complexo do app offline-first, onde a resposta deixou de fora boa parte dos problemas e números do relato.

## Iteração 1: primeira versão do v2

**Mudança:** criação do v2 com Role Prompting (Product Manager sênior), Chain of Thought interno (analisar persona, comportamento esperado, impacto, detalhes técnicos e complexidade sem escrever o raciocínio), regras explícitas, formato por complexidade (simples, médio, complexo), casos especiais e três exemplos Few-shot originais. O relato foi movido só para o user prompt.

**Resultado:** aprovado (média 0.9533). Clarity e Precision quase perfeitas, mas o F1 (0.87) ficou abaixo do resto. A causa estava no recall.

**Análise (comentários do juiz e traces):** a regra "use apenas fatos presentes no relato" ficou restritiva demais. O modelo omitia o que um PM incluiria naturalmente: confirmação visual, e-mail e log de auditoria em um webhook de pagamento, critérios de prevenção em concorrência de estoque, acessibilidade em modal. Em performance, usou o limite da falha como meta ("menos de 120 segundos", o próprio timeout) em vez de uma meta melhor.

## Iteração 2: liberar complementos esperados

**Mudança:**
- A regra de fatos foi dividida em duas. Uma proíbe inventar fatos sobre o bug (sistemas, endpoints, números, causas). A outra permite e pede os complementos que são consequência direta da correção: feedback ao usuário, log ou auditoria, notificações, consistência e acessibilidade.
- Nova regra de metas de desempenho: nunca usar o limite em que a falha acontece; usar o SLA quando o relato informar.
- Novas seções opcionais para relatos médios: "Critérios de Prevenção:" e "Critérios de Acessibilidade:".
- Pedido de completude nos relatos complexos.

**Resultado:** aprovado (média 0.9532, F1 0.88). Melhoraram bastante o botão de carrinho (de 0.85 para 0.97), o webhook de pagamento (de 0.84 para 0.94) e o relatório lento (de 0.82 para 0.92). Mas o bug simples do dashboard caiu para 0.75 e o modal continuou sem acessibilidade.

**Análise:** no dashboard, o modelo colocou o valor do caso dentro do critério ("deve exibir o valor correto de 42") e acrescentou "Contexto Técnico" a um relato simples. No modal, a seção de acessibilidade era opcional e foi ignorada. Nos relatos complexos, faltaram métricas de antes e depois e tasks organizadas em fases.

## Iteração 3: critérios gerais e seções obrigatórias por tipo

**Mudança:**
- Os critérios descrevem a regra geral, não o valor específico do caso (os valores vão para o contexto).
- Relato SIMPLES nunca ganha seções extras, mesmo citando um número ou navegador.
- "Critérios de Acessibilidade:" passou a ser obrigatória em bugs de componentes de interface.
- Relatos complexos ganham o bloco "Métricas: atual → esperado" e tasks agrupadas em fases quando são muitas.

**Resultado:** aprovado (média 0.9638). Todas as métricas ≥ 0.90 e nenhum exemplo com F1 abaixo de 0.82. O pior caso, o app offline-first, subiu de 0.66 no v1 para 0.82; o modal subiu de 0.79 para 0.91 com a acessibilidade obrigatória.

## F1-Score por bug

| Bug | v1 | It. 1 | It. 2 | It. 3 |
|---|---|---|---|---|
| Botão de adicionar ao carrinho | 0.85 | 0.85 | 0.97 | 0.97 |
| Campo de email aceita texto sem @ | 0.95 | 0.90 | 0.85 | 0.85 |
| Layout do perfil quebrado em landscape (iOS) | 0.94 | 0.91 | 0.95 | 0.95 |
| Dashboard com contagem errada de usuários ativos | 0.92 | 0.92 | 0.75 | 0.90 |
| Imagens não aparecem no Safari | 0.90 | 0.97 | 0.92 | 0.91 |
| Webhook de pagamento não é chamado | 0.90 | 0.84 | 0.94 | 0.93 |
| Relatório de vendas lento | 0.90 | 0.82 | 0.92 | 0.93 |
| Endpoint de usuários sem validar permissões | 0.87 | 0.92 | 0.90 | 0.92 |
| Pipeline calcula total errado com desconto | 0.92 | 0.95 | 0.92 | 0.91 |
| App Android trava na lista de notificações | 0.88 | 0.87 | 0.88 | 0.89 |
| Checkout sem validar estoque | 0.87 | 0.81 | 0.84 | 0.84 |
| Modal atrás do menu lateral | 0.77 | 0.79 | 0.79 | 0.91 |
| Checkout com múltiplas falhas críticas | 0.81 | 0.89 | 0.92 | 0.91 |
| Relatórios gerenciais lentos e inconsistentes | 0.81 | 0.87 | 0.84 | 0.89 |
| App offline-first com falhas de sincronização | 0.66 | 0.79 | 0.79 | 0.82 |

A saída completa da execução aprovada está em [`evaluation-final.txt`](evaluation-final.txt).
