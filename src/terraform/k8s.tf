module "kubernetes_cluster" {
  source = "https://github.com/frontierhq/azurerm-terraform-modules/releases/download/kubernetes-cluster/4.0.0/module.tar.gz//src"

  environment         = var.environment
  identifier          = local.identifier
  location            = var.location
  resource_group_name = module.resource_group.name
  zone                = var.zone

  kubernetes_version         = local.kubernetes_version
  log_analytics_workspace_id = data.azurerm_log_analytics_workspace.main.id
  network_plugin_mode        = null
  node_max_count             = local.node_max_count
  node_min_count             = local.node_min_count
  pod_subnet_id              = azurerm_subnet.pod.id
  vm_size                    = local.vm_size
  vnet_subnet_id             = azurerm_subnet.node.id

  tags = merge(var.tags, local.tags)
}
