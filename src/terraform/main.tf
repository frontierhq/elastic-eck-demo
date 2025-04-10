provider "azurerm" {
  features {}
}

module "resource_group" {
  source = "https://github.com/frontierhq/azurerm-terraform-modules/releases/download/resource-group/2.0.0/module.tar.gz//src"

  environment = var.environment
  identifier  = local.identifier
  location    = var.location
  zone        = var.zone

  tags = merge(var.tags, local.tags)
}
