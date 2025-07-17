module "kubernetes_cluster" {
  source = "https://github.com/frontierhq/azurerm-terraform-modules/releases/download/kubernetes-cluster/4.1.0/module.tar.gz//src"

  environment         = var.environment
  identifier          = local.identifier
  location            = var.location
  resource_group_name = module.resource_group.name
  zone                = var.zone

  kubernetes_version         = local.kubernetes_version
  log_analytics_workspace_id = data.azurerm_log_analytics_workspace.main.id
  node_max_count             = local.node_max_count
  node_min_count             = local.node_min_count
  oidc_issuer_enabled        = true
  vm_size                    = local.vm_size
  vnet_subnet_id             = azurerm_subnet.node.id
  workload_identity_enabled  = true

  # network_plugin_mode        = null # Uncomment to use flat network mode, rather than overlay
  # pod_subnet_id              = azurerm_subnet.pod.id # Uncomment to use flat network mode, rather than overlay

  tags = merge(var.tags, local.tags)
}
