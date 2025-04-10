module "user_assigned_identity" {
  source = "https://github.com/frontierhq/azurerm-terraform-modules/releases/download/user-assigned-identity/2.0.0/module.tar.gz//src"

  environment         = var.environment
  identifier          = local.identifier
  location            = var.location
  resource_group_name = module.resource_group.name
  zone                = var.zone

  tags = merge(var.tags, local.tags)
}

resource "azurerm_federated_identity_credential" "main" {
  name                = "elasticsearch"
  resource_group_name = module.resource_group.name
  audience            = ["api://AzureADTokenExchange"]
  issuer              = module.kubernetes_cluster.oidc_issuer_url
  parent_id           = module.user_assigned_identity.id
  subject             = "system:serviceaccount:elastic:workload-identity"
}
