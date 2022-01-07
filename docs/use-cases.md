# Examples

## 01_atlases_and_parcellations
### 000_accessing_atlases

_It is possible to get all known atlases. 
The response data contains links to get further information for each atlas._

**Get all atlases**
```
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases
```

**Get a single atlas by ID. For example the _Multilevel Human Atlas_**
```
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1
```

**Get all spaces for an atlas.**
```
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/spaces
```

### 001_accessing_parcellations

**Get all parcellations for _Multilevel Human Atlas_.**
```
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/parcellations
```

**Get the _Julich-Brain Cytoarchitectonic Maps 2.9_ parcellation.**
```
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/parcellations/minds%2Fcore%2Fparcellationatlas%2Fv1.0.0%2F94c1125b-b87e-45e4-901c-00daee7f2579-290
```

### 002_explore_region_hierarchy

**Get the _Julich-Brain Cytoarchitectonic Maps 2.9_ parcellation.**
```
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/parcellations/minds%2Fcore%2Fparcellationatlas%2Fv1.0.0%2F94c1125b-b87e-45e4-901c-00daee7f2579-290
```

**Get all regions for a single parcellation.**
```
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/parcellations/minds%2Fcore%2Fparcellationatlas%2Fv1.0.0%2F94c1125b-b87e-45e4-901c-00daee7f2579-290/regions
```

### 003_find_regions & 004_brain_region_metadata

**Get a single region by name.**
```
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/parcellations/minds%2Fcore%2Fparcellationatlas%2Fv1.0.0%2F94c1125b-b87e-45e4-901c-00daee7f2579-290/regions/v1%20left
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/parcellations/minds%2Fcore%2Fparcellationatlas%2Fv1.0.0%2F94c1125b-b87e-45e4-901c-00daee7f2579-290/regions/hOc2
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/parcellations/minds%2Fcore%2Fparcellationatlas%2Fv1.0.0%2F94c1125b-b87e-45e4-901c-00daee7f2579-290/regions/amygdala
```

### 005_brain_region_spatialprops

**Get the _MNI152 2009c nonl asym_ space**
```
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/spaces/minds%2Fcore%2Freferencespace%2Fv1.0.0%2Fdafcffc5-4826-4bf1-8ff6-46b8a31ff8e2
```

**Get spatial properties for the _Area hOc1 (V1, 17, CalcS) left_**
```
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/parcellations/minds%2Fcore%2Fparcellationatlas%2Fv1.0.0%2F94c1125b-b87e-45e4-901c-00daee7f2579-290/regions/v1%20left?space_id=minds%2Fcore%2Freferencespace%2Fv1.0.0%2Fdafcffc5-4826-4bf1-8ff6-46b8a31ff8e2
```

## 02_maps_and_templates
### 001_selecting_reference_spaces

**Get Space: _MNI152 2009c nonl asym_**

```
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/spaces/minds%2Fcore%2Freferencespace%2Fv1.0.0%2Fdafcffc5-4826-4bf1-8ff6-46b8a31ff8e2 
```

**Get Space: _MNI Colin 27_**
```
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/spaces/minds%2Fcore%2Freferencespace%2Fv1.0.0%2F7f39f7be-445b-47c0-9791-e971c0b6d992
```

**Get Space: _BigBrain_**
```
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/spaces/minds%2Fcore%2Freferencespace%2Fv1.0.0%2Fa1655b99-82f1-420f-a3c2-fe80fd4c8588
```

### 002_accessing_templates

**Get the reference template for _MNI152 2009c nonl asym_**
```
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/spaces/minds%2Fcore%2Freferencespace%2Fv1.0.0%2Fdafcffc5-4826-4bf1-8ff6-46b8a31ff8e2/templates
```

### 003_accessing_maps

**Get the parcellation maps for _MNI152 2009c nonl asym_**
```
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/spaces/minds%2Fcore%2Freferencespace%2Fv1.0.0%2F7f39f7be-445b-47c0-9791-e971c0b6d992/parcellation_maps
```

### 004_access_bigbrain

**Get the reference template for _BigBrain_**
```
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/spaces/minds%2Fcore%2Freferencespace%2Fv1.0.0%2Fa1655b99-82f1-420f-a3c2-fe80fd4c8588/templates
```

## 03_data_features
### 001_receptor_densities & 002_colorize_map

**Get receptor density features for the _Area hOc1 (V1, 17, CalcS) left_**
```
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/parcellations/minds%2Fcore%2Fparcellationatlas%2Fv1.0.0%2F94c1125b-b87e-45e4-901c-00daee7f2579-290/regions/v1/features/ReceptorDistribution
```

### 003_cell_distributions

**Get cortical cell body distributions for the _Area hOc1 (V1, 17, CalcS) left_**
```
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/parcellations/minds%2Fcore%2Fparcellationatlas%2Fv1.0.0%2F94c1125b-b87e-45e4-901c-00daee7f2579-290/regions/v1/features/CorticalCellDistribution
```

### 004_gene_expressions

**Get gene expressions for the _Area hOc1 (V1, 17, CalcS) left_**
```
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/parcellations/minds%2Fcore%2Fparcellationatlas%2Fv1.0.0%2F94c1125b-b87e-45e4-901c-00daee7f2579-290/regions/v1/features/GeneExpression
```


## 04_locations
...

## 05_anatomical_assignment
### 001_coordinates
### 002_activation_maps
