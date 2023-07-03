#!/usr/bin/env sh

set -e

terraform init
terraform destroy -auto-approve -var-file=environment/local.tf -lock=false