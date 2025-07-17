module "storage_account" {
  source = "https://github.com/frontierhq/azurerm-terraform-modules/releases/download/storage-account/2.0.0/module.tar.gz//src"

  environment         = var.environment
  identifier          = local.identifier
  location            = var.location
  resource_group_name = module.resource_group.name
  zone                = var.zone

  log_analytics_workspace_id = data.azurerm_log_analytics_workspace.main.id

  tags = merge(var.tags, local.tags)
}

resource "azurerm_role_assignment" "storage_blob_data_contributor" {
  scope                = module.storage_account.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = module.user_assigned_identity.principal_id
}

resource "azurerm_storage_container" "snapshots" {
  name                  = "snapshots"
  storage_account_id    = module.storage_account.id
  container_access_type = "private"
}
