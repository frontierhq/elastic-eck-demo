import os
from helpers.destroy_terraform import destroy_terraform
from helpers.get_env_value import get_env_value
from helpers.init_terraform import init_terraform


def deploy():
    environment = get_env_value("ENVIRONMENT")
    region = get_env_value("REGION")
    zone = get_env_value("ZONE")

    terraform = init_terraform(
        working_dir=os.path.join(os.getcwd(), "src/terraform"),
    )

    destroy_terraform(
        terraform=terraform,
        var={
            "environment": environment,
            "location": region,
            "zone": zone,
        },
    )


if __name__ == "__main__":
    deploy()
