# Use Cases for the brainscapes api and client

This use cases should show what can be done with the HTTP Api and how the same result can be achieved using the python client.

A more detailed documentation of the python client can be found her [braincapes documentation](https://jugit.fz-juelich.de/v.marcenko/brainscapes).

## Base URL for all requests

- URL: https://brainscapes.apps-dev.hbp.eu/api

## Parcellations

Return a list of all known parcellations in the brainscapes client.


- URL: [/parcellations](https://brainscapes.apps-dev.hbp.eu/api/parcellations)
- Response schema:

```
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "id": { "type": "string" },
      "name": { "type": "string" }
    },
    "required": ["id", "name"]
  }
}
```

- Response Example:

```javascript
[
  {
    "id": "minds/core/parcellationatlas/v1.0.0/94c1125b-b87e-45e4-901c-00daee7f2579",
    "name": "Julich-Brain Probabilistic Cytoarchitectonic Atlas"
  },
  {
    "id": "juelich/iav/atlas/v1.0.0/5",
    "name": "Probabilistic Long White Matter Bundle Atlas"
  },
]

```
- Python:

```python
atlas = REGISTRY.MULTILEVEL_HUMAN_ATLAS
parcellations = atlas.parcellations
```

## Spaces

## Regions

## Maps

## Templates

## Spatial props

## Receptor Data

### fingerprint

### profiles

### autoradiographs