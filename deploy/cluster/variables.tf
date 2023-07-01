variable "cluster_name" {
  type        = string
  description = "The name of the cluster."
  default     = "local-devtron"
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

variable "base_url" {
  description = "The Okta base URL. Example: okta.com, oktapreview.com, etc. This is the domain part of your Okta org URL"
}
variable "org_name" {
  description = "The Okta org name. This is the part before the domain in your Okta org URL"
}
variable "api_token" {
  type        = string
  description = "The Okta API token, this will be read from environment variable (TF_VAR_api_token) for security"
  sensitive   = true
}

variable "okta_admin_user_email" {
  type        = string
  description = "The Okta admin user email"
}

variable "okta_restricted_user_email" {
  type        = string
  description = "The Okta restricted user email"
}