#!/usr/bin/env bash
set -euxo pipefail

AGENT_VERSION="${1?Missing the APM python agent version}"

sed -ibck "s#elastic-apm==.*#elastic-apm==${AGENT_VERSION}#g" requirements.txt

## Bump agent version in the Dockerfile
sed -ibck "s#\(org.label-schema.version=\)\(.*\)#\1\"${AGENT_VERSION}\"#g" Dockerfile

# Commit changes
git add requirements.txt Dockerfile
git commit -m "Bump version ${AGENT_VERSION}"
