# Tool Registry

The Tool Registry is a declarative, machine-readable catalog of scientific
software that future platform components may use when planning reproducible
analyses. It records what a tool accepts, what it can produce, important
workflow-level parameters, and the environments with which it is architecturally
compatible.

It exists to keep tool selection explicit and inspectable before the platform
has an execution layer. A registry entry describes a capability; it is not
evidence that a tool is installed, has run, or produced a scientific result.

## Scope

The registry does:

- index the currently registered tools and their definition files;
- describe biological inputs and outputs for future dataset contracts;
- record a small set of workflow-relevant parameters and qualitative resource
  considerations;
- identify intended execution compatibility and its validation status; and
- point to upstream documentation.

It does **not** install or execute tools, download databases, run pipelines,
invoke external APIs, perform scientific interpretation, or make clinical or
diagnostic claims. Those responsibilities belong to future execution, workflow,
and scientific-review components.

## Current registry

| ID | Tool | Category | Primary role |
| --- | --- | --- | --- |
| `fastp` | Fastp | `quality_control` | Sequencing-read preprocessing and QC reporting |
| `megahit` | MEGAHIT | `assembly` | Metagenomic assembly of sequencing reads |
| `diamond` | DIAMOND | `sequence_alignment` | Fast protein and translated sequence database search |

Conceptually, a future workflow may describe this unexecuted sequence:

```text
FASTQ
  ↓
Fastp
  ↓
clean FASTQ
  ↓
MEGAHIT
  ↓
contigs
  ↓
DIAMOND
  ↓
annotation/search results
```

This is a declarative workflow concept only. Phase 1 has not executed Fastp,
MEGAHIT, DIAMOND, or any biological analysis.

## Files and definition structure

`registry.yaml` is the small index of registered tool IDs and their relative
definition paths. Each file in `definitions/` has the fields enforced by
`schemas/tool.schema.yaml`:

- identity and scientific purpose: `id`, `name`, `version`, `description`,
  `domain`, and `category`;
- `inputs` and `outputs`, including format and biological meaning;
- selected `parameters` useful for workflow construction;
- qualitative `resources` requirements;
- `execution` compatibility entries for local, container, Colab, and cloud
  environments, each with an explicit validation `status`;
- `container` availability metadata, without asserting an image exists;
- upstream `documentation`; and
- scientific and operational `limitations`.

The `.yaml` files intentionally use the JSON-compatible subset of YAML. JSON is
valid YAML 1.2, which lets the Phase 1 validator parse them with Python's
standard library rather than add a YAML dependency. Future code may use a YAML
parser if it needs the broader YAML syntax.

## Adding a future tool

1. Add one definition in `definitions/<tool-id>.yaml` following the schema.
2. Add its unique ID and relative path to `registry.yaml`.
3. Keep execution compatibility separate from evidence of execution: mark a
   validation status honestly (`supported`, `planned`, or `unvalidated`).
4. Add focused registry tests if the new contract needs coverage.
5. Run `python tools/validate_registry.py` and `python -m unittest discover -s tests`.

No tool should be represented as installed, executed, or scientifically
validated merely by being registered.

## Validation

`tools/validate_registry.py` is a lightweight standard-library validator. It
checks that the registry exists, contains exactly the Phase 1 tools, has unique
IDs, references existing definitions, and that each definition has the required
structure and metadata. It also validates the same required fields asserted by
the registry tests. It does not execute scientific software.

## Relationships to future components

The future Dataset Registry can use the input/output format and biological
meaning fields to describe compatible datasets and record lineage between them.
The future Workflow Engine can use the parameter contracts and compatibility
metadata to construct explicit, reviewable workflow plans. The future Agentic
Harness may query this structured catalog to suggest tools, but it must not
treat registry metadata as scientific evidence or as authority to replace
scientific validation.
