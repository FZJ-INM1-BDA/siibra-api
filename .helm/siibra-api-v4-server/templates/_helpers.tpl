{{/*
Expand the name of the chart.
*/}}
{{- define "siibra-api-v4-server.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}


{{/*
Define cache-dir. append -rc if is rc
This is because, on deploy staging it will rm -rf cache-dir.
This should prevent misconfiguration from deleting prod cache
*/}}
{{- define "siibra-api-v4-server.cache-dir" -}}
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
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "siibra-api-v4-server.fullname" -}}
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
{{- define "siibra-api-v4-server.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "siibra-api-v4-server.labels" -}}
app-role: server
helm.sh/chart: {{ include "siibra-api-v4-server.chart" . }}
{{ include "siibra-api-v4-server.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "siibra-api-v4-server.selectorLabels" -}}
app.kubernetes.io/name: {{ include "siibra-api-v4-server.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "siibra-api-v4-server.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "siibra-api-v4-server.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
