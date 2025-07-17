#! /bin/bash

# n.b. we do not set spec for ppd deployments
# since the {deployname}.yaml should contain the info needed

prefix="ppd-"

if [[ -z "$version" ]]
then
    exit 1
fi

for f in $( find .helm/deployments/ppd -name "*.yaml" )
do
    file=${f%.yaml}
    file=${file#.helm/deployments/ppd/}
    helm status $prefix$file > /dev/null 2>&1
    HELM_STATUS=$?
    
    helm_path=""
    if [[ "$file" == *"server"* ]]
    then
        helm_path=.helm/siibra-api-v4-server/
    fi

    if [[ "$file" == *"worker"* ]]
    then
        helm_path=.helm/siibra-api-v4-worker/
    fi

    if [[ $helm_path == "" ]]
    then
        echo "$file does not match to any, skipping"
        continue
    fi

    if [[ "$HELM_STATUS" == "0" ]]
    then
        echo "upgrading $prefix$file ..."
        helm upgrade -f $f \
            --history-max 3 \
            $prefix$file \
            $helm_path
    else
        echo "[NEW] installing $prefix$file ..."
        helm install -f $f $prefix$file \
            $helm_path
    fi
done
