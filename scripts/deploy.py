import os
import yaml
from helpers.apply_terraform import apply_terraform
from helpers.download_kubeconfig import download_kubeconfig
from helpers.exec import exec
from helpers.get_env_value import get_env_value
from helpers.get_ingress_external_ip import get_ingress_external_ip
from helpers.init_terraform import init_terraform
from tempfile import TemporaryDirectory


def deploy():
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

    exec("helm", "repo", "add", "ingress-nginx",
         "https://kubernetes.github.io/ingress-nginx")
    exec("helm", "repo", "add", "elastic",
         "https://helm.elastic.co")
    exec("helm", "repo", "update")

    kubeconfig_file_path, kubeconfig_file_cleanup = download_kubeconfig(
        aks_cluster_id=output['aks_cluster_id']['value'],
    )

    exec(
        "helm", "upgrade", "ingress-nginx", "ingress-nginx/ingress-nginx",
        "--version", "4.11.3",
        "--namespace", "ingress-nginx",
        "--create-namespace",
        "--install",
        "--wait",
        "--kubeconfig", kubeconfig_file_path,
        "--values", os.path.join(
            os.getcwd(), "config", "ingress-nginx", "values.yml"),
    )

    eck_values_file_path = os.path.join(
        os.getcwd(), "config", "eck-operator", "values.yml")

    # eck_values = None
    # with open(eck_values_file_path, "r") as file:
    #     eck_values = yaml.safe_load(file)

    # temp_dir = TemporaryDirectory()

    # for n in eck_values["managedNamespaces"]:
    #     manifest_file_path = os.path.join(temp_dir.name, f"{n}.yaml")
    #     create_ns_cmd = exec(
    #         "kubectl", "create", "namespace",
    #         n,
    #         "--dry-run=client",
    #         "--output", "yaml",
    #     )
    #     with open(manifest_file_path, "w") as manifest_file:
    #         manifest_file.write(create_ns_cmd.stdout)
    #         manifest_file.close()
    #     exec(
    #         "kubectl", "apply",
    #         "-f",
    #         manifest_file_path,
    #         "--wait",
    #         "--kubeconfig", kubeconfig_file_path,
    #     )

    # temp_dir.cleanup()

    exec(
        "helm", "upgrade", "eck-operator", "elastic/eck-operator",
        "--version", "2.16.1",
        # "--namespace", "tenant-external-search",
        # "--create-namespace",
        "--install",
        "--wait",
        "--kubeconfig", kubeconfig_file_path,
        "--values", eck_values_file_path,
    )

    ingress_external_ip = get_ingress_external_ip(kubeconfig_file_path)
    ingress_fqdn = f"{ingress_external_ip.replace('.', '-')}.nip.io"

    values = {
        "external_hostname_suffix": ingress_fqdn,
    }

    temp_dir = TemporaryDirectory()

    values_file_path = os.path.join(temp_dir.name, "values.yml")

    with open(values_file_path, "w") as values_file:
        yaml.dump(values, values_file)
        values_file.close()

    exec(
        "helm", "upgrade", "eck-demo", os.path.join(
            os.getcwd(), "src", "helm"),
        "--namespace", "elastic",
        "--create-namespace",
        "--install",
        "--wait",
        "--values", values_file_path,
        "--kubeconfig", kubeconfig_file_path,
    )

    temp_dir.cleanup()

    kubeconfig_file_cleanup()

    print(f"Monitoring available at: https://monitoring.{ingress_fqdn}")


if __name__ == "__main__":
    deploy()
