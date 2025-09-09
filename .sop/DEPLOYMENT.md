# Deployment

This document outline the standard operating procedure of how to rollout a new release on ebrains infrastructure.

## Requirements

- bash
- jq
- yq

Go to https://docker-registry.ebrains.eu/harbor/projects/28/summary , and ensure sufficient disk space (> 6GB). If insufficient:

- `siibra/siibra-explorer` namespace: `2.*.*` that is not the latest can be deleted
- `siibra/siibra-api` namespace: `0.3.*[-worker|-worker-v4|server]` that is not the latest can be deleted
- above, any untagged image can be deleted
- if unsure, ask Xiao 

## Steps

1. Increment `VERSION`. Run `./prepare_release.sh lint` and ensure passes (`./prepare_release.sh fix`, if necessary). Commit, and push to remote `master`. Ensure test passes.

**n.b. VERSION must be incremented. siibra-api uses VERSION as key for cache invalidation**

1. Make prerelease with the name `$VERSION-rc` e.g. `0.3.19-rc`, then `0.3.19-rc2` ... etc. 

**Ensure prerelease flag is checked**

**Ensure rc is in the tag**

2. Wait until action completes. Once it does, check https://siibra-api-rc.apps.ebrains.eu/ , and ensure:

    - the hash matches with the git hash of the prerelease.
    - the version matches with the value of the file `VERSION`

3. Ensure siibra-explorer release checklist is complete.

4. Make release with the name `$VERSION` e.g. `0.3.19`. 
