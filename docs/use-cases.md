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
### 003_find_regions
### 004_brain_region_metadata
### 005_brain_region_spatialprops

## 02
### 001
### 002
### 003
### 004

## 03
### 001
### 002
### 003
### 004

## 04
...

## 05
### 001
### 002
