{{/*
Expand the name of the chart.
*/}}
{{- define "siibra-api-v4-worker.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}


{{/*
Define cache-dir. append -rc if is rc
This is because, on deploy staging it will rm -rf cache-dir.
This should prevent misconfiguration from deleting prod cache
*/}}
{{- define "siibra-api-v4-worker.cache-dir" -}}
{{- if eq .Values.sapi.flavor "rc" -}}
{{/*
N.B. *any* update here *needs* to be reflected in
.github/workflows/docker-img.yml#jobs>warmup-rc-at-helm
*/}}
{{- printf "%s-%s" .Values.sapi.version "rc" }}
{{- else }}
{{- .Values.sapi.version }}
{{- end }}
{{- end }}


{{/*
Define resources.
if high: 300m/1500m, 2Gi/5Gi, no scale
if low (default, also fallback if neither): 100m/500m, 1Gi/2.5Gi, scale
*/}}
{{- define "siibra-api-v4-worker.autoscale" -}}
{{- if eq .Values.sapi.resources.flavor "high" -}}
{{- else -}}
"true"
{{- end }}
{{- end }}

{{- define "siibra-api-v4-worker.resources" -}}
{{- if eq .Values.sapi.resources.flavor "high" -}}
limits:
  cpu: 1500m
  memory: 5Gi
requests:
  cpu: 300m
  memory: 2Gi
{{- else -}}
limits:
  cpu: 500m
  memory: 2.5Gi
requests:
  cpu: 100m
  memory: 1Gi
{{- end }}
{{- end }}


{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "siibra-api-v4-worker.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "siibra-api-v4-worker.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "siibra-api-v4-worker.labels" -}}
app-role: worker
helm.sh/chart: {{ include "siibra-api-v4-worker.chart" . }}
{{ include "siibra-api-v4-worker.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "siibra-api-v4-worker.selectorLabels" -}}
app.kubernetes.io/name: {{ include "siibra-api-v4-worker.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "siibra-api-v4-worker.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "siibra-api-v4-worker.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
