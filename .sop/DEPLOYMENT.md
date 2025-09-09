# Deployment

This document outline the standard operating procedure of how to rollout a new release on ebrains infrastructure.

## Requirements

bash

Go to https://docker-registry.ebrains.eu/harbor/projects/28/summary , and ensure sufficient disk space (> 6GB). If insufficient:

- `siibra/siibra-explorer` namespace: `2.*.*` that is not the latest can be deleted
- `siibra/siibra-api` namespace: `3.*.*[-worker|-worker-v4|server]` that is not the latest can be deleted
- above, any untagged image can be deleted
- if unsure, ask Xiao 

## Steps

0. Increment `VERSION`. Run `prepare_release.sh lint` and ensure passes (`prepare_release.sh fix`, if necessary). Commit, and push to remote main. Ensure test passes.

1. Make prerelease with the name `$VERSION-rc` e.g. `0.3.19-rc`, then `0.3.19-rc2` ... etc. 

**Ensure prerelease flag is checked**

**Ensure rc is in the tag**

2. Wait until action completes

3. Ensure siibra-explorer release checklist is complete.

4. Make release with the name `$VERSION` e.g. `0.3.19`. 
