output "aks_cluster_id" {
  value = module.kubernetes_cluster.id
}

output "storage_account_name" {
  value = module.storage_account.name
}

output "managed_identity_client_id" {
  value = module.user_assigned_identity.client_id
}
