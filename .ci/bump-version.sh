#!/usr/bin/env bash
set -euxo pipefail

AGENT_VERSION="${1?Missing the APM python agent version}"

sed -ibck "s#elastic-apm==.*#elastic-apm==${AGENT_VERSION}#g" requirements.txt

# Commit changes
git add requirements.txt
git commit -m "Bump version ${AGENT_VERSION}"
