import asyncio
import os
import yaml
from helpers.apply_terraform import apply_terraform
from helpers.download_kubeconfig import download_kubeconfig
from helpers.get_env_value import get_env_value
from helpers.get_ingress_external_ip import get_ingress_external_ip
from helpers.init_terraform import init_terraform
from pathlib import Path
from pyhelm3 import Client as HelmClient


async def deploy():
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
        aks_cluster_id=output['aks_cluster_id']['value'],
    )

    helm_client = HelmClient(kubeconfig=kubeconfig_file_path)

    print("deploying ingress-nginx")
    nginx_chart = await helm_client.get_chart(
        "ingress-nginx",
        repo="https://kubernetes.github.io/ingress-nginx",
        version="4.11.3"
    )
    nginx_values_file_path = os.path.join(
        os.getcwd(), "config", "ingress-nginx", "values.yml")
    nginx_values = yaml.safe_load(Path(nginx_values_file_path).read_text())
    nginx_revision = await helm_client.install_or_upgrade_release(
        "ingress-nginx",
        nginx_chart,
        nginx_values,
        namespace="ingress-nginx",
        create_namespace=True,
        wait=True,
    )
    print(f"release {nginx_revision.release.name} with revision {nginx_revision.revision} has status {nginx_revision.status}")

    print("deploying eck-operator")
    eck_operator_chart = await helm_client.get_chart(
        "eck-operator",
        repo="https://helm.elastic.co",
        version="2.16.1"
    )
    eck_operator_values_file_path = os.path.join(
        os.getcwd(), "config", "eck-operator", "values.yml")
    eck_operator_values = yaml.safe_load(
        Path(eck_operator_values_file_path).read_text())
    eck_operator_revision = await helm_client.install_or_upgrade_release(
        "eck-operator",
        eck_operator_chart,
        eck_operator_values,
        namespace="elastic-system",
        create_namespace=True,
        wait=True,
    )
    print(f"release {eck_operator_revision.release.name} with revision {eck_operator_revision.revision} has status {eck_operator_revision.status}")

    ingress_external_ip = get_ingress_external_ip(kubeconfig_file_path)
    ingress_fqdn = f"{ingress_external_ip.replace('.', '-')}.nip.io"

    print("deploying eck-demo")
    eck_demo_chart = await helm_client.get_chart(
        chart_ref=os.path.join(os.getcwd(), "src", "helm"),
    )
    eck_demo_values = {
        "external_hostname_suffix": ingress_fqdn,
    }
    eck_demo_revision = await helm_client.install_or_upgrade_release(
        "eck-demo",
        eck_demo_chart,
        eck_demo_values,
        namespace="elastic",
        create_namespace=True,
        wait=True,
    )
    print(f"release {eck_demo_revision.release.name} with revision {eck_demo_revision.revision} has status {eck_demo_revision.status}")

    kubeconfig_file_cleanup()

    print(f"Monitoring available at: https://monitoring.{ingress_fqdn}")


if __name__ == "__main__":
    asyncio.run(deploy())
