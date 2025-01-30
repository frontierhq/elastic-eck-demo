module "kubernetes_cluster" {
  source = "https://github.com/frontierhq/azurerm-terraform-modules/releases/download/kubernetes-cluster/3.0.2/module.tar.gz//src"

  environment         = var.environment
  identifier          = local.identifier
  location            = var.location
  resource_group_name = module.resource_group.name
  zone                = var.zone

  kubernetes_version         = local.kubernetes_version
  log_analytics_workspace_id = data.azurerm_log_analytics_workspace.main.id
  node_max_count             = local.node_max_count
  node_min_count             = local.node_min_count
  subnet_id                  = azurerm_subnet.main.id
  vm_size                    = local.vm_size

  tags = merge(var.tags, local.tags)
}
