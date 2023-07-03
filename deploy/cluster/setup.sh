#!/usr/bin/env sh

set -e

brew install kreuzwerker/taps/m1-terraform-provider-helper
m1-terraform-provider-helper activate
m1-terraform-provider-helper install hashicorp/template -v v2.2.0

terraform init
terraform apply -auto-approve -var-file=environment/local.tf