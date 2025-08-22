import asyncio
import os
import yaml
from dotenv import load_dotenv
from helpers.apply_terraform import apply_terraform
from helpers.download_kubeconfig import download_kubeconfig
from helpers.get_env_value import get_env_value
from helpers.get_ingress_external_ip import get_ingress_external_ip
from helpers.init_terraform import init_terraform
from pathlib import Path
from pyhelm3 import Client as HelmClient


async def deploy():
    load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))

    environment = get_env_value("ENVIRONMENT")
    region = get_env_value("REGION")
    zone = get_env_value("ZONE")

    terraform = init_terraform(
        working_dir=os.path.join(os.getcwd(), "src/terraform"),
    )

    output = apply_terraform(
        terraform=terraform,
        var={
            "environment": environment,
            "location": region,
            "zone": zone,
        },
    )

    kubeconfig_file_path, kubeconfig_file_cleanup = download_kubeconfig(
        aks_cluster_id=output["aks_cluster_id"]["value"],
    )

    helm_client = HelmClient(kubeconfig=kubeconfig_file_path)

    print("deploying ingress-nginx")
    nginx_chart = await helm_client.get_chart(
        "ingress-nginx",
        repo="https://kubernetes.github.io/ingress-nginx",
        version="4.11.3",
    )
    nginx_values_file_path = os.path.join(
        os.getcwd(), "config", "ingress-nginx", "values.yml"
    )
    nginx_values = yaml.safe_load(Path(nginx_values_file_path).read_text())
    nginx_revision = await helm_client.install_or_upgrade_release(
        "ingress-nginx",
        nginx_chart,
        nginx_values,
        namespace="ingress-nginx",
        create_namespace=True,
        wait=True,
    )
    print(
        f"release {nginx_revision.release.name} with revision {nginx_revision.revision} has status {nginx_revision.status}"
    )

    print("deploying eck-operator")
    eck_operator_chart = await helm_client.get_chart(
        "eck-operator", repo="https://helm.elastic.co", version="3.1.0"
    )
    eck_operator_values_file_path = os.path.join(
        os.getcwd(), "config", "eck-operator", "values.yml"
    )
    eck_operator_values = yaml.safe_load(
        Path(eck_operator_values_file_path).read_text()
    )
    eck_operator_revision = await helm_client.install_or_upgrade_release(
        "eck-operator",
        eck_operator_chart,
        eck_operator_values,
        namespace="elastic-system",
        create_namespace=True,
        wait=True,
    )
    print(
        f"release {eck_operator_revision.release.name} with revision {eck_operator_revision.revision} has status {eck_operator_revision.status}"
    )

    ingress_external_ip = get_ingress_external_ip(kubeconfig_file_path)
    ingress_fqdn = f"{ingress_external_ip.replace('.', '-')}.nip.io"

    print("deploying eck-stack-config")
    eck_stack_config_chart = await helm_client.get_chart(
        chart_ref=os.path.join(os.getcwd(), "src", "helm"),
    )
    eck_stack_config_values = {
        "azure_repository": {
            "account": output["storage_account_name"]["value"],
        },
        "managed_identity": {
            "client_id": output["managed_identity_client_id"]["value"],
        },
    }
    eck_stack_config_revision = await helm_client.install_or_upgrade_release(
        "eck-stack-config",
        eck_stack_config_chart,
        eck_stack_config_values,
        namespace="elastic",
        create_namespace=True,
        wait=True,
    )
    print(
        f"release {eck_stack_config_revision.release.name} with revision {eck_stack_config_revision.revision} has status {eck_stack_config_revision.status}"
    )

    eck_stack_names = ["monitoring", "a", "b"]
    for eck_stack_name in eck_stack_names:
        print(f"deploying eck-stack {eck_stack_name}")
        eck_stack_chart = await helm_client.get_chart(
            "eck-stack", repo="https://helm.elastic.co", version="0.15.0"
        )
        eck_stack_values_file_path = os.path.join(
            os.getcwd(), "config", "eck-stack", f"values.{eck_stack_name}.yml"
        )
        eck_stack_values = yaml.safe_load(Path(eck_stack_values_file_path).read_text())
        eck_stack_values["eck-kibana"]["config"]["server.publicBaseUrl"] = (
            f"https://{eck_stack_name}.{ingress_fqdn}"
        )
        eck_stack_values["eck-kibana"]["ingress"]["hosts"][0]["host"] = (
            f"{eck_stack_name}.{ingress_fqdn}"
        )
        eck_stack_revision = await helm_client.install_or_upgrade_release(
            f"eck-stack-{eck_stack_name}",
            eck_stack_chart,
            eck_stack_values,
            namespace="elastic",
            create_namespace=True,
            wait=True,
        )
        print(
            f"release {eck_stack_revision.release.name} with revision {eck_stack_revision.revision} has status {eck_stack_revision.status}"
        )

        print(f"Kibana available at: https://{eck_stack_name}.{ingress_fqdn}")

    kubeconfig_file_cleanup()


if __name__ == "__main__":
    asyncio.run(deploy())
