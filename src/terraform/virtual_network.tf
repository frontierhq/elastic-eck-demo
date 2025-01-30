module "virtual_network" {
  source = "https://github.com/frontierhq/azurerm-terraform-modules/releases/download/virtual-network/2.0.2/module.tar.gz//src"

  environment         = var.environment
  identifier          = local.identifier
  location            = var.location
  resource_group_name = module.resource_group.name
  zone                = var.zone

  address_space              = local.virtual_network_address_space
  log_analytics_workspace_id = data.azurerm_log_analytics_workspace.main.id

  tags = merge(var.tags, local.tags)
}

resource "azurerm_subnet" "main" {
  name                 = "${local.identifier}-k8s"
  virtual_network_name = module.virtual_network.name
  resource_group_name  = module.resource_group.name

  address_prefixes = [cidrsubnet(local.virtual_network_address_space, 3, 0)]
}
