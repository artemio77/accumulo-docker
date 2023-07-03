resource "kubernetes_namespace" "argocd" {
  metadata {
    name = var.kubernetes_argocd_namespace
  }
  depends_on = [kind_cluster.k8s]
}

resource "helm_release" "argocd" {
  depends_on = [kubernetes_namespace.argocd]

  name       = "argocd"
  repository = "https://argoproj.github.io/argo-helm"
  chart      = "argo-cd"
  namespace  = var.kubernetes_argocd_namespace
  version    = var.argocd_helm_chart_version == "" ? null : var.argocd_helm_chart_version
  values     = [
    templatefile(
      "${path.module}/templates/argocd-values.yaml.tpl",
      {
        "argocd_server_host"          = var.argocd_server_host
        "argocd_github_client_id"     = var.argocd_github_client_id
        "argocd_github_client_secret" = var.argocd_github_client_secret
        "argocd_github_org_name"      = var.argocd_github_org_name

        "argocd_ingress_enabled"                 = var.argocd_ingress_enabled
        "argocd_ingress_tls_acme_enabled"        = var.argocd_ingress_tls_acme_enabled
        "argocd_ingress_ssl_passthrough_enabled" = var.argocd_ingress_ssl_passthrough_enabled
        "argocd_ingress_class"                   = var.argocd_ingress_class
        "argocd_ingress_tls_secret_name"         = var.argocd_ingress_tls_secret_name
      }
    )
  ]
}