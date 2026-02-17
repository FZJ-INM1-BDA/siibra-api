#! /bin/bash

fix_key="fix"

if [[ "$1" = "help" || "$1" = "--help" || "$1" = "-h"  ]]
then
    echo "'$0 $fix_key' to fix (in place replace). Otherwise lint (return non-zero if fails)."
    exit 0
fi

if [[ "$1" = "$fix_key" ]]
then
    fix_flag="1"
fi

version=$(cat VERSION)
# latest_tag=$(curl 'https://api.github.com/repos/FZJ-INM1-BDA/siibra-api/releases' | jq -r '[.[] | select(.prerelease==false) | .tag_name][0]')
latest_release_tag=$(curl 'https://api.github.com/repos/FZJ-INM1-BDA/siibra-api/releases/latest' | jq -r '.tag_name')

if [[ ! "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]
then
    echo "cat VERSION: '"$version"' does not fit ^[0-9]+\.[0-9]+\.[0-9]+$"
    exit 1
fi

if [[ ! "$latest_release_tag" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]
then
    echo "Warning: latest_release_tag: '"$latest_release_tag"' does not fit ^v[0-9]+\.[0-9]+\.[0-9]+$"
    echo "I hope you know what you are doing ..."
fi


if [[ "v$version" = "$latest_release_tag" ]]
then
    echo "Version did not seem to be incremented."
    echo "I hope you know what you are doing ..."
fi

error=""

# check image.spec is correct
check_spec() {
    filepath=$1
    filename=$2

    if [[ "$filepath" = *"/prod/"* ]]
    then
        deploy_target="prod"
    fi
    
    if [[ "$filepath" = *"/ppd/"* ]]
    then
        deploy_target="prod"
    fi
    
    if [[ "$filepath" = *"/rc/"* ]]
    then
        deploy_target="rc"
    fi

    if [[ "$deploy_target" != "prod" ]]
    then
        # do not check spec other than in prod setting
        return 0
    fi

    if [[ "$filename" = "worker-"* ]]
    then
        expected_spec=$version-worker
    fi
    if [[ "$filename" = "server" ]]
    then
        expected_spec=$version-server
    fi
    if [[ "$filename" = "worker-v4" ]]
    then
        expected_spec=$version-worker-v4
    fi
    
    if [[ -z "$expected_spec" ]]
    then
        echo expected spec cannot be found: $filepath $filename
        exit 1
    fi

    if [[ "$fix_flag" = "1" ]]
    then
        expected_spec=$expected_spec yq -i '.image.spec=strenv(expected_spec)' $filepath
        return 0
    fi
    curr_spec=$(yq '.image.spec' $filepath)
    
    if [[ "$expected_spec" != "$curr_spec" ]]
    then
        error="$f : .image.spec : $curr_spec\n$error"
    fi
    return 0
}

# check sapi.queue is correct
check_queue() {
    
    filepath=$1
    filename=$2

    if [[ "$filename" != "worker-"* ]]
    then
        # not worker, do not fix
        return 0
    fi
    if [[ "$filename" = *"v4" ]]
    then
        # _is_ worker-v4, do not fix
        return 0
    fi
    queue=${filename#worker-}
    expected_q=$version.$dir.$queue
    if [[ "$fix_flag" = "1" ]]
    then
        expected_q=$expected_q yq -i '.sapi.queue=strenv(expected_q)' $filepath
        return 0
    fi
    curr_q=$(yq '.sapi.queue' $filepath)
    if [[ "$expected_q" != "$curr_q" ]]
    then
        error="$f : .sapi.queue : $curr_q\n$error"
    fi
    return 0
}

# iterate and check
for dir in rc prod ppd
do
    for f in $( find .helm/deployments/$dir -name "*.yaml" )
    do
        filename=$f
        filename=${filename%.yaml}
        filename=${filename#.helm/deployments/$dir/}
        
        check_queue $f $filename
        check_spec $f $filename

        if [[ "$fix_flag" = "1" ]]
        then
            version=$version yq -i '.sapi.version=strenv(version)' $f
            continue
        fi

        curr_version=$(yq '.sapi.version' $f)
        if [[ "$curr_version" != "$version" ]]
        then
            error="$f sapi.veresion $curr_version\n$error"
            continue
        fi
    done
done

if [[ "$fix_flag" = "1" ]]
then
    echo "fixed all if needed"
    exit 0
fi

if [[ -z "$error" ]]
then
    echo "validation success!"
    exit 0
fi

echo "validation failed!"
echo "expected version: $version"
echo -e "$error"

exit 1
