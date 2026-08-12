# Scientific Health & Bioinformatics Agentic Platform

Plataforma aberta para conceber, executar e auditar workflows científicos em saúde e bioinformática. O projeto reduz a distância entre dados brutos, pipelines reproduzíveis e resultados revisáveis.

## Problema

Análises como controle de qualidade, montagem e anotação dependem de ferramentas heterogêneas, dados volumosos e registros incompletos. A plataforma propõe uma camada comum para organizar datasets, workflows, ferramentas, execução e proveniência.

## Agentic Scientific Workflow Platform

Agentes especializados poderão ajudar a planejar, selecionar ferramentas e validar etapas, sempre dentro de workflows explícitos e auditáveis. Um modelo de linguagem não substitui ferramentas científicas nem produz evidência: apenas poderá ajudar a operar uma arquitetura que registra entradas, versões, parâmetros e saídas.

## Arquitetura e execução

A arquitetura é *cloud-first*: cargas de grande porte poderão seguir para Colab ou nuvem. O desenvolvimento local é leve, voltado a documentação, validações simples e orquestração futura. Uma camada de execução abstrata permitirá migração gradual para máquinas locais mais capazes.

## Princípios

- Reprodutibilidade por versões, parâmetros e ambientes identificáveis.
- Proveniência e rastreabilidade de cada dataset e resultado.
- Separação entre saída computacional e interpretação científica.
- Nenhum resultado científico deve ser inventado ou apresentado sem validação.
- Uso responsável de dados humanos em conformidade com a LGPD.

## Status

**Fase 0 — Architecture — concluída:** fundação documental e estrutural, concluída no commit `37e46e1`.

**Fase 1 — Tool Registry — concluída:** catálogo declarativo de ferramentas científicas, concluído no commit `a4b9990` e publicado na branch `main`. A fase adicionou o índice de ferramentas, schema, definições para Fastp, MEGAHIT e DIAMOND, validação leve e 10 testes. Nenhuma ferramenta científica foi executada, nenhuma dependência científica foi instalada e nenhum processamento científico foi realizado.

**Fase 2 — Dataset Registry — planejada:** próxima etapa para identidade, metadados e linhagem de datasets.

Consulte a [arquitetura do sistema](docs/architecture/system.md), a [metodologia científica](docs/scientific/methodology.md) e o [roadmap](docs/development/roadmap.md).
