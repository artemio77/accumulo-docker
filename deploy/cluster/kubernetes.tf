

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
      }
      extra_port_mappings {
        container_port = 443
        host_port      = 443
      }
    }

    node {
      role = "worker"
    }
  }
}
