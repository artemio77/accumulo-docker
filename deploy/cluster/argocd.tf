resource "helm_release" "argocd" {
  name = "argocd"

  repository       = "https://argoproj.github.io/argo-helm"
  chart            = "argo-cd"
  namespace        = "argocd"
  version          = "5.36.11"
  create_namespace = true
  depends_on       = [kind_cluster.k8s]
  values           = [
    file("argocd/application.yaml")
  ]
}