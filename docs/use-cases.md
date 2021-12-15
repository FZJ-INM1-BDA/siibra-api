# Examples

## 01_atlases_and_parcellations
### 000_accessing_atlases

_It is possible to get all known atlases. 
The response data contains links to get further information for each atlas._

**Swagger**
```
https://siibra-api-stable.apps.hbp.eu/v1_0/docs#/atlases/get_all_atlases_atlases_get
```

**Rest Call**
```
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases
```

**Curl**
```
curl -X 'GET' 'https://siibra-api-stable.apps.hbp.eu/v1_0/atlases' -H 'accept: application/json'
```

_It is also possible to get one single atlas by providing an atlas ID. For example the **Multilevel Human Atlas**._

**Swagger**
```
https://siibra-api-stable.apps.hbp.eu/v1_0/docs#/atlases/get_atlas_by_id_atlases__atlas_id__get
```

**Rest Call**
```
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1
```

**Curl**
```
curl -X 'GET' 'https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1' -H 'accept: application/json'
```

### 001_accessing_parcellations

_All parcellations for **Multilevel Human Atlas**._
```
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/parcellations
```

_**Julich-Brain Cytoarchitectonic Maps 2.9**_
```
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/parcellations/minds%2Fcore%2Fparcellationatlas%2Fv1.0.0%2F94c1125b-b87e-45e4-901c-00daee7f2579-290
```

### 002_explore_region_hierarchy

```
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/parcellations/minds%2Fcore%2Fparcellationatlas%2Fv1.0.0%2F94c1125b-b87e-45e4-901c-00daee7f2579-290
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/parcellations/minds%2Fcore%2Fparcellationatlas%2Fv1.0.0%2F94c1125b-b87e-45e4-901c-00daee7f2579-290/regions

```

### 003_find_regions

```
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/parcellations/minds%2Fcore%2Fparcellationatlas%2Fv1.0.0%2F94c1125b-b87e-45e4-901c-00daee7f2579-290
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/parcellations/minds%2Fcore%2Fparcellationatlas%2Fv1.0.0%2F94c1125b-b87e-45e4-901c-00daee7f2579-290/regions

```

### 004_brain_region_metadata

```
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/parcellations/minds%2Fcore%2Fparcellationatlas%2Fv1.0.0%2F94c1125b-b87e-45e4-901c-00daee7f2579-290
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/parcellations/minds%2Fcore%2Fparcellationatlas%2Fv1.0.0%2F94c1125b-b87e-45e4-901c-00daee7f2579-290/regions/v1%20left
```

### 005_brain_region_spatialprops

```
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/spaces/minds%2Fcore%2Freferencespace%2Fv1.0.0%2Fdafcffc5-4826-4bf1-8ff6-46b8a31ff8e2
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/parcellations/minds%2Fcore%2Fparcellationatlas%2Fv1.0.0%2F94c1125b-b87e-45e4-901c-00daee7f2579-290
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/parcellations/minds%2Fcore%2Fparcellationatlas%2Fv1.0.0%2F94c1125b-b87e-45e4-901c-00daee7f2579-290/regions/v1%20left
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/parcellations/minds%2Fcore%2Fparcellationatlas%2Fv1.0.0%2F94c1125b-b87e-45e4-901c-00daee7f2579-290/regions/v1%20left?space_id=minds%2Fcore%2Freferencespace%2Fv1.0.0%2Fdafcffc5-4826-4bf1-8ff6-46b8a31ff8e2
```

## 02
### 001

```
MNI152 2009c nonl asym

https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/spaces/minds%2Fcore%2Freferencespace%2Fv1.0.0%2Fdafcffc5-4826-4bf1-8ff6-46b8a31ff8e2 


MNI Colin 27

https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/spaces/minds%2Fcore%2Freferencespace%2Fv1.0.0%2F7f39f7be-445b-47c0-9791-e971c0b6d992


Big Brain

https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/spaces/minds%2Fcore%2Freferencespace%2Fv1.0.0%2Fa1655b99-82f1-420f-a3c2-fe80fd4c8588
```




### 002

```
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/spaces/minds%2Fcore%2Freferencespace%2Fv1.0.0%2Fdafcffc5-4826-4bf1-8ff6-46b8a31ff8e2/templates
```

### 003

```
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/spaces/minds%2Fcore%2Freferencespace%2Fv1.0.0%2F7f39f7be-445b-47c0-9791-e971c0b6d992/parcellation_maps
```

### 004

```
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/spaces/minds%2Fcore%2Freferencespace%2Fv1.0.0%2Fa1655b99-82f1-420f-a3c2-fe80fd4c8588/parcellation_maps
```



## 03
### 001

```
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1

https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/parcellations/minds%2Fcore%2Fparcellationatlas%2Fv1.0.0%2F94c1125b-b87e-45e4-901c-00daee7f2579-290/regions/v1/features/ReceptorDistribution
```


### 002

```
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1

https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/parcellations/minds%2Fcore%2Fparcellationatlas%2Fv1.0.0%2F94c1125b-b87e-45e4-901c-00daee7f2579-290/regions/v1/features/CorticalCellDistribution
```

### 003

```
https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1

https://siibra-api-stable.apps.hbp.eu/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/parcellations/minds%2Fcore%2Fparcellationatlas%2Fv1.0.0%2F94c1125b-b87e-45e4-901c-00daee7f2579-290/regions/v1/features/GeneExpression
```

### 004

## 04
...

## 05
### 001
### 002
