locals {
  identifier                    = "eckdemo"
  kubernetes_version            = "1.33.2"
  node_max_count                = 6
  node_min_count                = 3
  tags                          = {}
  virtual_network_address_space = "10.1.0.0/24"
  vm_size                       = "Standard_D2s_v3"
}
