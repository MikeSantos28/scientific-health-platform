# Agentic Harness

O *Agentic Harness* é a camada de controle que torna a assistência por modelos de linguagem observável e limitada por contratos científicos e operacionais.

| Conceito | Responsabilidade futura |
| --- | --- |
| Agent | Papel especializado que propõe ações dentro de escopo definido. |
| Planner | Converte um objetivo em plano de etapas verificáveis. |
| Tool Selector | Escolhe uma ferramenta registrada e compatível com a etapa. |
| Executor | Solicita a execução à camada apropriada; não interpreta ciência. |
| Validator | Verifica contratos, integridade e critérios definidos. |
| Provenance | Registra entradas, versões, parâmetros, decisões e saídas. |
| Orchestrator | Coordena estado, políticas, aprovações e fluxo entre componentes. |

## Distinções essenciais

- **LLM:** modelo que gera ou transforma linguagem; não é evidência científica e não executa pipelines por si só.
- **Agente:** camada de decisão orientada a objetivo que usa um LLM ou regras, sob políticas e registros.
- **Ferramenta científica:** programa ou método que produz uma saída computacional a partir de entradas e parâmetros definidos.
- **Workflow:** grafo explícito de etapas, dependências, contratos e critérios de conclusão.
- **Executor:** adaptador de infraestrutura que submete, monitora e recupera uma execução, sem definir a metodologia.

Nenhum desses componentes está implementado nesta fase; este documento define somente os limites arquiteturais.
