variable "cluster_name" {
  type        = string
  description = "The name of the cluster."
}

variable "cluster_config_path" {
  type        = string
  description = "Cluster's kubeconfig location"
  default     = "~/.kube/config"
}

variable "cluster_domain" {
  type        = string
  description = "Cluster's domain"
}

variable "okta_base_url" {
  description = "The Okta base URL. Example: okta.com, oktapreview.com, etc. This is the domain part of your Okta org URL"
}
variable "okta_org_name" {
  description = "The Okta org name. This is the part before the domain in your Okta org URL"
}
variable "okta_api_token" {
  type        = string
  description = "The Okta API token, this will be read from environment variable (TF_VAR_api_token) for security"
}

variable "okta_admin_user_email" {
  type        = string
  description = "The Okta admin user email"
}

variable "okta_restricted_user_email" {
  type        = string
  description = "The Okta restricted user email"
}

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