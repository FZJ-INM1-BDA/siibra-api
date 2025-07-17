#! /bin/bash

# cd .helm/adhoc && \
#     kubectl apply -f configmaps-siibra-api-common.yml,pvc-data-volume.yml,deployment-redis.yaml,pvc-log-volume.yml,service-cache-redis.yml,cronjob-kubectl-top-pod.yaml && \
#     cd ../..

VERSION=$(cat VERSION)

.helm/adhoc
WARM_CACHE_YML=$(SIIBRA_CACHEDIR=/siibra-api-volume/$VERSION/ envsubst < .helm/adhoc/warm-cache.yaml)
echo -e $WARM_CACHE_YML
echo "applying ..."
echo "$WARM_CACHE_YML" | kubectl apply -f -


while true
do
    sleep 10
    POD_PHASE=$(kubectl get pod warmup-pod -o json | jq -r '.status.phase')

    echo Possible phases: Pending, Running, Succeeded, Failed, Unknown
    echo Found phase: $POD_PHASE

    if [[ "$POD_PHASE" == "Failed" ]] || [[ "$POD_PHASE" == "Unknown" ]]
    then
    exit 1
    fi

    if [[ "$POD_PHASE" == "Succeeded" ]]
    then
    exit 0
    fi
done

WARM_CACHE_YML_V4=$(SIIBRA_CACHEDIR=/siibra-api-volume/$VERSION/ envsubst < .helm/adhoc/warm-cache-v4.yaml)
echo -e $WARM_CACHE_YML_V4
echo "applying ..."
echo "$WARM_CACHE_YML_V4" | kubectl apply -f -


while true
do
    sleep 10
    POD_PHASE=$(kubectl get pod warmup-pod-v4 -o json | jq -r '.status.phase')

    echo Possible phases: Pending, Running, Succeeded, Failed, Unknown
    echo Found phase: $POD_PHASE

    if [[ "$POD_PHASE" == "Failed" ]] || [[ "$POD_PHASE" == "Unknown" ]]
    then
    exit 1
    fi

    if [[ "$POD_PHASE" == "Succeeded" ]]
    then
    exit 0
    fi
done
