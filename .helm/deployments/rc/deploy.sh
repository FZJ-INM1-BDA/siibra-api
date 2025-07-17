#! /bin/bash

# n.b. we *need* to set the spec in the form of sha256:<sha_hash>
# this will force redeploy of pods, and be specific about which image to use

prefix="rc-"

for f in $( find .helm/deployments/rc -name "*.yaml" )
do
    echo "processing $f ..."
    file=${f%.yaml}
    file=${file#.helm/deployments/rc/}
    helm status $prefix$file > /dev/null 2>&1
    HELM_STATUS=$?
    
    helm_path=""
    spec=""
    if [[ "$file" == *"server"* ]]
    then
        helm_path=.helm/siibra-api-v4-server/
        spec=$DOCKER_IMGSHA_SERVER
    fi

    if [[ "$file" == *"worker"* ]]
    then
        helm_path=.helm/siibra-api-v4-worker/
        spec="$DOCKER_IMGSHA_WORKER"

        # the cursed duo spy dependency
        # hopefully, spy v2 would fix this issue
        # and will not need to have two separate worker images
        if [[ "$file" == *"worker-v4"* ]]
        then
            spec="$DOCKER_IMGSHA_WORKER_V4"
        fi
    fi

    if [[ "$helm_path" == "" ]]
    then
        echo "$file does not match to any, skipping"
        continue
    fi
    
    if [[ "$spec" == "" ]]
    then
        echo "spec not set. Something went wrong."
        exit 1
    fi

    if [[ "$HELM_STATUS" == "0" ]]
    then
        echo "upgrading $prefix$file ..."
        helm upgrade -f $f \
            --set image.spec=$spec \
            --set image.repository=ghcr.io/fzj-inm1-bda/siibra-api \
            --history-max 3 \
            $prefix$file \
            $helm_path
    else
        echo "[NEW] installing $prefix$file ..."
        helm install -f $f \
            --set image.spec=$spec \
            --set image.repository=ghcr.io/fzj-inm1-bda/siibra-api \
            $prefix$file $helm_path
    fi
done
