import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.containerservice import ContainerServiceClient
from tempfile import TemporaryDirectory


def download_kubeconfig(aks_cluster_id: str):
    temp_dir = TemporaryDirectory()

    kubeconfig_file_path = os.path.join(temp_dir.name, "kube.config")

    aks_cluster_id_parts = aks_cluster_id.split("/")
    aks_cluster_subscription_id = aks_cluster_id_parts[2]
    aks_cluster_resource_group_name = aks_cluster_id_parts[4]
    aks_cluster_name = aks_cluster_id_parts[8]

    client = ContainerServiceClient(credential=DefaultAzureCredential(
    ), subscription_id=aks_cluster_subscription_id)
    cluster_admin_credentials = client.managed_clusters.list_cluster_admin_credentials(
        resource_group_name=aks_cluster_resource_group_name,
        resource_name=aks_cluster_name,
    )
    with open(kubeconfig_file_path, "wb") as kubeconfig_file:
        kubeconfig_file.write(cluster_admin_credentials.kubeconfigs[0].value)
        kubeconfig_file.close()

    os.chmod(kubeconfig_file_path, 0o600)

    return kubeconfig_file_path, temp_dir.cleanup
