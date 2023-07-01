terraform {
  required_providers {
    kind = {
      source  = "tehcyx/kind"
      version = "~> 0.0.19"
    }

    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "2.12.1"
    }

    helm = {
      source  = "hashicorp/helm"
      version = "2.6.0"
    }

    null = {
      source  = "hashicorp/null"
      version = "3.1.1"
    }

    okta = {
      source  = "okta/okta"
      version = "~> 3.15"
    }
  }
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


# Setup OKTA groups
resource "okta_group" "k8s_admin" {
  name        = "k8s-admins"
  description = "Users who can access k8s cluster as admins"
}

resource "okta_group" "k8s_restricted_users" {
  name        = "k8s-restricted-users"
  description = "Users who can only view pods and services in default namespace"
}

# Assign users to the groups
data "okta_user" "admin" {
  search {
    name  = "profile.email"
    value = var.okta_admin_user_email
  }
}

resource "okta_group_memberships" "admin_user" {
  group_id = okta_group.k8s_admin.id
  users    = [
    data.okta_user.admin.id
  ]
}

data "okta_user" "restricted_user" {
  search {
    name  = "profile.email"
    value = var.okta_restricted_user_email
  }
}

resource "okta_group_memberships" "restricted_user" {
  group_id = okta_group.k8s_restricted_users.id
  users    = [
    data.okta_user.restricted_user.id
  ]
}


# Create an OIDC application

resource "okta_app_oauth" "k8s_oidc" {
  label                      = "k8s OIDC"
  type                       = "native" # this is important
  token_endpoint_auth_method = "none"   # this sets the client authentication to PKCE
  grant_types                = [
    "authorization_code"
  ]
  response_types = ["code"]
  redirect_uris  = [
    "https://kubernetes-dashboard.k8s.aderevets",
  ]
  post_logout_redirect_uris = [
    "https://kubernetes-dashboard.k8s.aderevets",
  ]
  lifecycle {
    ignore_changes = [groups]
  }
}

output "k8s_oidc_client_id" {
  value = okta_app_oauth.k8s_oidc.client_id
}

# Assign groups to the OIDC application
resource "okta_app_group_assignments" "k8s_oidc_group" {
  app_id = okta_app_oauth.k8s_oidc.id
  group {
    id = okta_group.k8s_admin.id
  }
  group {
    id = okta_group.k8s_restricted_users.id
  }
}

# Create an authorization server

resource "okta_auth_server" "oidc_auth_server" {
  name      = "k8s-auth"
  audiences = ["https://kubernetes-dashboard.k8s.aderevets"]
}

output "k8s_oidc_issuer_url" {
  value = okta_auth_server.oidc_auth_server.issuer
}

# Add claims to the authorization server

resource "okta_auth_server_claim" "auth_claim" {
  name                    = "groups"
  auth_server_id          = okta_auth_server.oidc_auth_server.id
  always_include_in_token = true
  claim_type              = "IDENTITY"
  group_filter_type       = "STARTS_WITH"
  value                   = "k8s-"
  value_type              = "GROUPS"
}

# Add policy and rule to the authorization server

resource "okta_auth_server_policy" "auth_policy" {
  name             = "k8s_policy"
  auth_server_id   = okta_auth_server.oidc_auth_server.id
  description      = "Policy for allowed clients"
  priority         = 1
  client_whitelist = [okta_app_oauth.k8s_oidc.id]
}

resource "okta_auth_server_policy_rule" "auth_policy_rule" {
  name                 = "AuthCode + PKCE"
  auth_server_id       = okta_auth_server.oidc_auth_server.id
  policy_id            = okta_auth_server_policy.auth_policy.id
  priority             = 1
  grant_type_whitelist = [
    "authorization_code"
  ]
  scope_whitelist = ["*"]
  group_whitelist = ["EVERYONE"]
}

resource "kind_cluster" "k8s" {
  name            = var.cluster_name
  kubeconfig_path = pathexpand(var.cluster_config_path)
  wait_for_ready  = true

  depends_on = [okta_app_oauth.k8s_oidc, okta_auth_server.oidc_auth_server]

  kind_config {
    kind        = "Cluster"
    api_version = "kind.x-k8s.io/v1alpha4"

    node {
      role = "control-plane"

      kubeadm_config_patches = [
        "kind: InitConfiguration\nnodeRegistration:\n  kubeletExtraArgs:\n    node-labels: \"ingress-ready=true\"\n",
        "kind: ClusterConfiguration\napiServer:\n  extraArgs:\n    oidc-client-id: \"${okta_app_oauth.k8s_oidc.client_id}\"\n    oidc-issuer-url: \"${okta_auth_server.oidc_auth_server.issuer}\"\n    oidc-username-claim: \"email\"\n"
      ]
      extra_port_mappings {
        container_port = 80
        host_port      = 80
        listen_address = "127.0.0.1"
      }
      extra_port_mappings {
        container_port = 443
        host_port      = 443
        listen_address = "127.0.0.1"
      }
    }

    node {
      role = "worker"
    }
  }
}
