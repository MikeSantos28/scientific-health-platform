# Camada de execução

A camada de execução isola o workflow da infraestrutura. Um workflow descreve **o que** deve ocorrer; um executor futuro define **onde** e **como** a tarefa é submetida, observada e registrada.

```text
Executor
├── MockExecutor
├── ColabExecutor
├── CloudExecutor
├── LocalExecutor
├── DockerExecutor
└── ApptainerExecutor
```

- **MockExecutor:** usado para testes estruturais, sem rodar ciência.
- **ColabExecutor:** destinado a workloads interativos que caibam em notebooks Colab.
- **CloudExecutor:** alvo para jobs escaláveis e gerenciados.
- **LocalExecutor:** futuro uso em máquinas locais com capacidade suficiente.
- **DockerExecutor:** futura execução em contêineres Docker.
- **ApptainerExecutor:** futura alternativa para ambientes científicos e HPC.

Todos deverão expor um contrato comum de submissão, estado, logs, cancelamento e metadados de proveniência. Nenhum executor é implementado na Fase 0, e esta fase não instala imagens, contêineres ou ferramentas.
