# Dataset Registry

The Dataset Registry is a lightweight, file-backed catalog of logical
scientific Datasets. A Dataset may have multiple physical Representations; a
file, path, copy, workflow, execution, or tool is not itself a Dataset.

## Storage

`registry.yaml` is a versionable index of Dataset IDs and definition paths.
Each registered Dataset is stored as one JSON-compatible YAML file in
`definitions/`. This storage contains metadata only: it does not copy, access,
or process biological data. It can be migrated to a future database while
preserving the public Dataset Schema contract.

## Validation

The Registry uses [Dataset Schema v0.1](../schemas/dataset.schema.yaml) as the
source for structural validation. Structural validation checks the declared
JSON Schema shape, required fields, types, allowed lifecycle states, and closed
contract objects.

Semantic validation remains separate. It checks unique Representation IDs
within a Dataset, requires a Representation when lifecycle status is
`available`, and verifies parent Dataset IDs when they are known to the
Registry. Dataset Schema v0.1 does not define a lifecycle transition graph, so
the Registry accepts any schema-permitted lifecycle status after semantic
validation.

## Limitations

v0.1 has no database, API, workflow engine, execution layer, scientific tool
execution, location-access check, checksum computation, or scientific
interpretation. It neither installs nor runs scientific software.
