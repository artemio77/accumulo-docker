terraform {
  required_providers {
    kind = {
      source  = "tehcyx/kind"
      version = "~> 0.2.0"
    }

    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "2.21.1"
    }

    helm = {
      source  = "hashicorp/helm"
      version = "2.10.1"
    }

    null = {
      source  = "hashicorp/null"
      version = "3.2.1"
    }

    okta = {
      source  = "okta/okta"
      version = "4.0.2"
    }

    template = {
      source  = "hashicorp/template"
      version = "2.2.0"
    }
  }
  required_version = ">= 1.0.0"
}

provider "kind" {
}

provider "kubernetes" {
  config_path = pathexpand(var.cluster_config_path)
}

provider "helm" {
  kubernetes {
    config_path = pathexpand(var.cluster_config_path)
  }
}

provider "okta" {
  org_name  = var.org_name
  base_url  = var.base_url
  api_token = var.api_token
}