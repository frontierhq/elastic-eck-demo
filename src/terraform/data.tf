data "azurerm_log_analytics_workspace" "main" {
  name                = "law-sbx-sbx-uks-main"
  resource_group_name = "rg-sbx-sbx-uks-loganalytics"
}
