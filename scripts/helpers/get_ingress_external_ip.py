from py_utils import exec


def get_ingress_external_ip(kubeconfig_file_path: str):
    process = exec(
        "kubectl",
        "get",
        "svc",
        "--namespace",
        "ingress-nginx",
        "--output",
        "jsonpath='{.status.loadBalancer.ingress[0].ip}'",
        "--kubeconfig",
        kubeconfig_file_path,
        "ingress-nginx-controller",
        silent=True,
    )
    return process.stdout.strip("'")


def _test():
    raise NotImplementedError


if __name__ == "__main__":
    _test()
