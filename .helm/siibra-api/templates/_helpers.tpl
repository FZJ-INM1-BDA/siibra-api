{{/*
Expand the name of the chart.
*/}}
{{- define "siibra-api.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Define root image
*/}}
{{- define "siibra-api.root-img" -}}
{{- if eq .Values.sapiFlavor "rc" }}
{{- "rc" }}
{{- else }}
{{- .Values.sapiVersion }}
{{- end }}
{{- end }}


{{/*
Define cache-dir. append -rc if is rc
This is because, on deploy staging it will rm -rf cache-dir.
This should prevent misconfiguration from deleting prod cache
*/}}
{{- define "siibra-api.cache-dir" -}}
{{- if eq .Values.sapiFlavor "rc" -}}
{{/*
N.B. *any* update here *needs* to be reflected in
.github/workflows/docker-img.yml#jobs>warmup-rc-at-helm
*/}}
{{- printf "%s-%s" .Values.sapiVersion "rc" }}
{{- else }}
{{- .Values.sapiVersion }}
{{- end }}
{{- end }}


{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "siibra-api.fullname" -}}
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
{{- define "siibra-api.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "siibra-api.labels" -}}
helm.sh/chart: {{ include "siibra-api.chart" . }}
{{ include "siibra-api.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app: siibra-api
app-flavor: {{ .Values.sapiFlavor }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "siibra-api.selectorLabels" -}}
app.kubernetes.io/name: {{ include "siibra-api.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "siibra-api.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "siibra-api.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
