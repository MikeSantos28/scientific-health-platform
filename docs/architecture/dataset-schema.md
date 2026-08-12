# Dataset Schema v0.1

## 1. Objetivo

Este documento formaliza o contrato arquitetural inicial para a entidade **Dataset** da Scientific Health Platform. O contrato descreve a identidade científica lógica de um conjunto de dados, suas representações físicas, metadados, proveniência e ciclo de vida.

Este é um contrato declarativo, não uma implementação do Dataset Registry. Ele não cria banco de dados, API, schema YAML/JSON executável, validador, workflow, executor ou processamento científico. A implementação futura deve preservar a separação entre desenvolvimento leve, orquestração e execução científica.

## 2. Conceito de Dataset

Um Dataset representa uma entidade científica lógica e identificável. Ele pode ser uma coleção de leituras de sequenciamento, uma montagem, um alinhamento, uma chamada de variantes, uma anotação ou outro artefato científico descrito por identidade, tipo, formato e contexto.

O Dataset é a unidade de catálogo, proveniência e reutilização. Um Dataset não é sinônimo de um arquivo físico nem de uma execução. Resultados computacionais futuros deverão ser registrados como novos Datasets, sujeitos à revisão e à validação científica apropriadas; o registro não transforma uma saída em evidência clínica ou conclusão científica.

## 3. Dataset versus Representation

Uma **Representation** é uma manifestação física de um Dataset: por exemplo, um arquivo, um objeto em armazenamento, ou uma cópia equivalente em outra localização. Um Dataset pode ter uma ou mais Representations.

Por exemplo, leituras paired-end de HG002 podem ser um único Dataset lógico, com duas Representations físicas de papéis distintos:

```text
Dataset: HG002 sequencing reads
├── Representation: R1.fastq.gz (role: read_1)
└── Representation: R2.fastq.gz (role: read_2)
```

Portanto, arquivos relacionados não devem ser registrados automaticamente como Datasets independentes. De modo semelhante, uma cópia local e uma cópia em object storage podem representar o mesmo Dataset lógico. O `id` do Dataset é estável; o `id` de uma Representation só precisa ser único dentro daquele Dataset.

## 4. Estrutura do Dataset Schema v0.1

```text
Dataset
├── identity                         required
│   ├── id                           required
│   ├── name                         required
│   └── version                      optional
├── type                             required
├── format                           required
├── metadata                         optional
│   ├── description                  optional
│   ├── organism                     optional
│   │   ├── scientific_name          optional
│   │   └── taxonomy_id              optional
│   ├── sample_id                    optional
│   ├── study_id                     optional
│   └── attributes                   optional, extensible
├── representations                  required collection
│   └── representation
│       ├── id                       required
│       ├── role                     required
│       ├── location                 required
│       │   ├── kind                 required
│       │   └── uri                  required
│       └── integrity                optional
│           ├── algorithm            optional
│           └── checksum             optional
├── provenance                       optional
│   ├── origin                       optional
│   │   ├── type                     required when origin is present
│   │   └── identifier               optional
│   └── parents[]                    optional Dataset IDs
└── lifecycle                        required
    └── status                       required
```

As palavras “required” e “optional” descrevem o contrato v0.1. Esta página não é, por si, um artefato de validação estrutural executável.

## 5. Campos obrigatórios e opcionais

Todo Dataset v0.1 deve possuir `identity.id`, `identity.name`, `type`, `format`, a coleção `representations` e `lifecycle.status`. Cada Representation deve possuir `id`, `role`, `location.kind` e `location.uri`.

`identity.version`, `metadata`, `integrity` e `provenance` são opcionais. Campos internos condicionais são obrigatórios somente quando seu objeto pai estiver presente: por exemplo, `provenance.origin.type` é obrigatório quando `provenance.origin` for declarado.

Uma coleção de `representations` pode estar vazia enquanto o Dataset estiver somente `registered`. A validação semântica futura deverá exigir ao menos uma Representation para um Dataset com status `available`.

## 6. Identity

`identity.id` é o identificador estável do Dataset dentro do Registry. Ele é a referência usada por linhagem, por workflows futuros e por componentes que precisem apontar para a entidade lógica.

`identity.name` é o nome legível por humanos. Ele auxilia navegação e revisão, mas não substitui o identificador estável.

`identity.version` é opcional. Quando existir, descreve uma versão lógica do Dataset e não deve ser confundida com o nome de um arquivo, uma data de cópia ou o estado de uma execução.

## 7. Type

`type` representa a categoria científica do Dataset. Vocabulários iniciais úteis incluem `sequencing_reads`, `assembly`, `alignment`, `variants`, `annotation`, `expression`, `epidemiological` e `metadata`.

Esses valores são exemplos iniciais, não uma taxonomia universal rígida. O contrato deve poder evoluir com vocabulários controlados, perfis por domínio ou extensões, sem exigir reconstrução do Dataset Registry.

## 8. Format

`format` representa o formato lógico dos dados. Exemplos incluem `fastq`, `fasta`, `bam`, `cram`, `vcf`, `gff`, `gtf`, `genbank`, `csv`, `tsv` e `json`.

Formato não é compressão. Um Dataset pode declarar `format: fastq` e ter uma Representation física com nome `R1.fastq.gz`. A extensão do arquivo é uma característica da Representation e não substitui a declaração lógica de formato do Dataset.

## 9. Metadata

`metadata` é opcional e extensível. Pode registrar `description`, contexto de organismo em `organism.scientific_name` e `organism.taxonomy_id`, `sample_id`, `study_id` e `attributes` adicionais.

Nem o nome científico nem o identificador taxonômico são obrigatórios para todos os Datasets. `attributes` permite registrar metadados específicos de domínio sem tornar o núcleo do contrato excessivamente rígido. Metadados devem seguir as políticas futuras de qualidade, privacidade, minimização e acesso; credenciais e segredos não pertencem a este contrato.

## 10. Representations

`representations` é uma coleção obrigatória que descreve as manifestações físicas do Dataset. Cada item contém:

- `id`: identificador único dentro do Dataset;
- `role`: papel obrigatório da Representation no conjunto lógico;
- `location`: onde a manifestação pode ser localizada; e
- `integrity`: informação opcional para verificar conteúdo.

Papéis iniciais podem incluir `primary`, `read_1`, `read_2`, `index` e `annotation`. Esta lista poderá evoluir. A unicidade de `representation.id` é local ao Dataset: não há requisito de unicidade global para esses IDs.

Uma entidade pode ter Representations em múltiplas localizações — por exemplo, uma local e outra em object storage — sem deixar de ser um único Dataset.

## 11. Location

Toda Representation possui `location.kind` e `location.uri`.

`kind` identifica a classe de localização física, que poderá ser detalhada futuramente (por exemplo, armazenamento local, object storage ou repositório). `uri` identifica a localização segundo as convenções daquele tipo.

Não armazenar credenciais, tokens, senhas, chaves de API ou outros segredos em `location`, em `metadata` ou em qualquer outro campo do Dataset Schema.

## 12. Integrity

`integrity` é opcional e pode conter `algorithm` e `checksum`. Quando ambos existirem, permitem que uma implementação futura verifique a integridade da Representation física sem confundir essa verificação com validação científica.

SHA-256 é o algoritmo recomendado quando aplicável, mas o v0.1 não limita o contrato exclusivamente a SHA-256. Isso permite compatibilidade com fontes ou repositórios que publiquem outros algoritmos de checksum.

## 13. Provenance

`provenance` registra origem e ancestralidade no nível científico lógico do Dataset. `provenance.origin.type` descreve o tipo de origem; quando presente, seu `identifier` opcional poderá no futuro referenciar accession, URL, identificador de repositório ou outro identificador externo.

`provenance.parents[]` contém IDs de Datasets ancestrais. Pais referenciam Datasets lógicos, nunca arquivos físicos ou URIs de Representations. A resolução dos IDs e a consistência das relações serão responsabilidade de validação semântica futura.

O v0.1 não inclui `provenance.tool` nem qualquer acoplamento direto ao Tool Registry. A relação arquitetural futura permanece:

```text
Dataset → Workflow → Execution → Tool → Dataset
```

## 14. Lifecycle

`lifecycle.status` é obrigatório e descreve o estado de catálogo do Dataset. Os estados iniciais são:

- `registered`: a entidade foi registrada, mas seus dados físicos podem ainda não estar disponíveis;
- `available`: existe uma Representation acessível conforme as políticas do ambiente;
- `archived`: a entidade foi preservada, possivelmente fora do acesso ativo;
- `deprecated`: a entidade permanece rastreável, mas não é recomendada para novo uso.

Estados de execução como `running`, `queued` e `failed` não pertencem ao Dataset Schema. Eles pertencem à futura Execution Layer.

## 15. Structural versus Semantic Validation

O contrato separa dois níveis de validação:

- **Structural validation** verifica presença de campos, tipos, estrutura, valores permitidos e unicidade quando aplicável.
- **Semantic validation** verifica significado e relações: por exemplo, que um Dataset `available` possui Representation, que IDs de Representation são únicos, que `parents[]` aponta para Dataset IDs válidos e que lifecycle e relações são consistentes.

O v0.1 documenta essa divisão, mas não implementa validador estrutural ou semântico. A decisão sobre quando e onde executar validações pertence a fases posteriores do Dataset Registry e da Execution Layer.

## 16. Exemplos conceituais

Os exemplos abaixo descrevem agrupamentos lógicos; não são registros reais, não incluem locais reais e não representam dados executados ou validados.

### Paired-end FASTQ

```text
Dataset (type: sequencing_reads, format: fastq)
├── Representation (role: read_1): R1.fastq.gz
└── Representation (role: read_2): R2.fastq.gz
```

### BAM e índice BAI

```text
Dataset (type: alignment, format: bam)
├── Representation (role: primary): sample.bam
└── Representation (role: index): sample.bam.bai
```

### VCF comprimido e índice TBI

```text
Dataset (type: variants, format: vcf)
├── Representation (role: primary): variants.vcf.gz
└── Representation (role: index): variants.vcf.gz.tbi
```

### Assembly

```text
Dataset (type: assembly, format: fasta)
└── Representation (role: primary): contigs.fasta.gz
```

### Registro sem arquivo disponível

```text
Dataset (lifecycle.status: registered)
└── representations: coleção ainda sem manifestação disponível
```

### Múltiplas localizações

```text
Dataset (uma entidade lógica)
├── Representation (role: primary, location.kind: local)
└── Representation (role: primary, location.kind: object_storage)
```

## 17. Relação com o Tool Registry

O [Tool Registry](../../tools/README.md) descreve capacidades, contratos de entrada/saída e parâmetros de ferramentas. O Dataset Schema descreve entidades científicas lógicas e suas manifestações físicas. Os dois registries não são acoplados diretamente no v0.1.

No futuro, um Workflow poderá selecionar uma definição de ferramenta e ligar as exigências de entrada/saída a Datasets registrados. O Tool Registry não executa ferramentas, e a simples compatibilidade de formatos não prova correção científica ou execução bem-sucedida.

## 18. Relação futura com o Workflow Engine

O futuro Workflow Engine poderá consultar o Dataset Registry para encontrar Datasets compatíveis, registrar as dependências lógicas de um plano e declarar quais novos Datasets uma etapa espera produzir. Ele deverá preservar IDs, versões, parâmetros e relações de proveniência, sem confundir planejamento com execução.

Fluxo conceitual futuro:

```text
User
  ↓
Agent / Workflow Engine
  ↓
Dataset Registry
  ↓
Tool Registry
  ↓
Workflow
  ↓
Execution Layer
  ↓
Executor
  ↓
New Dataset
  ↓
Dataset Registry
```

Esse fluxo não é implementado por este documento.

## 19. Relação futura com a Execution Layer

A futura [Execution Layer](execution-layer.md) poderá resolver Representations autorizadas, submeter trabalho a executores e registrar resultados como novos Datasets. Estados operacionais, logs, falhas, filas, ambientes e credenciais devem permanecer fora do Dataset Schema.

O Dataset Schema também não afirma que uma localização é acessível, que um checksum foi verificado ou que dados foram processados. Essas são verificações operacionais e semânticas futuras.

## 20. Limitações do v0.1

- Não define um schema YAML, JSON Schema, API, banco de dados ou implementação de Registry.
- Não define validação estrutural ou semântica executável.
- Não fixa taxonomias universais para `type`, `role`, `location.kind` ou atributos extensíveis.
- Não resolve referências de pais, acesso a locais, checksums, permissões ou políticas de dados humanos.
- Não modela Workflows, Executions, Tools, resultados científicos ou interpretação clínica.

## 21. Princípios de evolução futura

A evolução do contrato deve preservar:

- Dataset como entidade científica lógica, distinta de seus arquivos e cópias;
- extensibilidade sem perder campos nucleares estáveis;
- proveniência por Dataset IDs, não por caminhos físicos transitórios;
- separação entre validação estrutural, validação semântica e execução;
- ausência de segredos no metadado do Dataset;
- compatibilidade com desenvolvimento local leve e execução futura em Colab, nuvem ou hardware local apropriado; e
- distinção entre metadado computacional e conclusão científica, clínica ou diagnóstica.

Qualquer schema executável, validador, Dataset Registry funcional ou integração com workflow e execução requer uma fase posterior explicitamente autorizada.
