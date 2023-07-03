variable "kubernetes_argocd_namespace" {
  description = "Namespace to release argocd into"
  type        = string
  default     = "argocd"
}

variable "argocd_helm_chart_version" {
  description = "argocd helm chart version to use"
  type        = string
  default     = "5.36.13"
}

variable "argocd_server_host" {
  description = "Hostname for argocd (will be utilised in ingress if enabled)"
  type        = string
}

variable "argocd_ingress_class" {
  description = "Ingress class to use for argocd"
  type        = string
  default     = "nginx"
}

variable "argocd_ingress_enabled" {
  description = "Enable/disable argocd ingress"
  type        = bool
  default     = true
}

variable "argocd_ingress_tls_acme_enabled" {
  description = "Enable/disable acme TLS for ingress"
  type        = string
  default     = "true"
}

variable "argocd_ingress_ssl_passthrough_enabled" {
  description = "Enable/disable SSL passthrough for ingresss"
  type        = string
  default     = "true"
}

variable "argocd_ingress_tls_secret_name" {
  description = "Secret name for argocd TLS cert"
  type        = string
  default     = "argocd-cert"
}

variable "argocd_github_client_id" {
  description = "GitHub OAuth application client id (see Argo CD user management guide)"
  type        = string
}

variable "argocd_github_client_secret" {
  description = "GitHub OAuth application client secret (see Argo CD user management guide)"
  type        = string
}

variable "argocd_github_org_name" {
  description = "Organisation to restrict Argo CD to"
  type        = string
}

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