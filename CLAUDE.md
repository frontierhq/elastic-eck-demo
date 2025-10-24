# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Elastic Cloud on Kubernetes (ECK) demo project that provisions Azure infrastructure and deploys Elasticsearch/Kibana stacks using Terraform and Helm. The project uses Python scripts to orchestrate the deployment.

## Development Setup

Dependencies are managed with `uv`. Install and set up the project:

```bash
make install
```

This installs dependencies and sets up pre-commit hooks (except in CI).

## Required Environment Variables

Create a `.env` file with:
- `ARM_SUBSCRIPTION_ID` - Azure subscription ID
- `ENVIRONMENT` - Environment name (e.g., "sbx")
- `REGION` - Azure region (e.g., "uksouth")
- `ZONE` - Zone identifier

## Common Commands

### Deploy Infrastructure and Stacks
```bash
make deploy
```
Runs `scripts/deploy.py` which:
1. Provisions Azure infrastructure via Terraform (AKS cluster, networking, storage, managed identity)
2. Downloads kubeconfig from AKS
3. Deploys Helm charts: ingress-nginx, eck-operator, eck-stack-config, and multiple eck-stack instances
4. Configures dynamic ingress FQDNs using nip.io

### Destroy Infrastructure
```bash
make destroy
```
Runs `scripts/destroy.py` to tear down Terraform resources.

### Testing and Linting
```bash
make test              # Run all tests (lint + scripts)
make test.lint         # Run all linting (Python + YAML)
make test.lint.python  # Run ruff check and format
make test.lint.yaml    # Run yamllint
make test.script       # Run scripts/test.py
```

### Seed Data with esrally
```bash
make seed
```
Seeds Elasticsearch with log data using esrally benchmark tool.

### Clean Up
```bash
make clean
```
Removes all `.terraform` directories.

## Architecture

### Infrastructure Layer (Terraform)
- **Location**: `src/terraform/`
- **Providers**: azurerm, elasticstack
- **Modules**: Uses Frontier HQ's azurerm-terraform-modules for resource groups
- **Components**:
  - AKS cluster (`k8s.tf`)
  - Virtual networking (`virtual_network.tf`)
  - Storage accounts (`storage.tf`)
  - Managed identity with workload identity federation (`identity.tf`)
  - Elasticstack user management via Terraform provider

### Deployment Orchestration (Python)
- **Main script**: `scripts/deploy.py` - async orchestration of Terraform and Helm
- **Helper utilities**: `scripts/helpers/` for kubeconfig download, env value parsing, ingress IP retrieval
- **External dependency**: Uses `py-utils` from `../py-utils` (editable local dependency) for Terraform wrapper functions

### Helm Charts
- **External charts**: ingress-nginx (v4.11.3), eck-operator (v3.1.0), eck-stack (v0.15.0)
- **Custom chart**: `src/helm/eck-stack-config` - configures Azure repository settings, managed identity, licenses, keystores, service accounts, remote certs, and ingest services
- **Stack configurations**: Multiple environment configs in `config/eck-stack/` (monitoring, a, b stacks)

### Deployment Flow
1. Terraform provisions Azure infrastructure
2. Script downloads AKS kubeconfig
3. Deploys ingress-nginx and waits for external IP
4. Deploys eck-operator to elastic-system namespace
5. Generates dynamic ingress FQDN using nip.io
6. Deploys eck-stack-config with Azure/identity settings
7. Deploys multiple eck-stack instances (monitoring, a, b) with stack-specific values and dynamic ingress configuration

## Useful kubectl Commands

Get elastic user password:
```bash
kubectl get secret <cluster>-es-elastic-user -n <namespace> -o=jsonpath='{.data.elastic}' | base64 --decode; echo
```

Get current license stats:
```bash
kubectl -n elastic-system get configmap elastic-licensing -o json | jq .data
```

## Dependencies

- Python 3.11+
- uv (package manager)
- Terraform ~> 1.11
- Azure CLI (for authentication)
- kubectl (for cluster interaction)
