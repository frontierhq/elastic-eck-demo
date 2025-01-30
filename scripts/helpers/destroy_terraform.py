import os
from python_terraform import IsFlagged, Terraform
from tempfile import TemporaryDirectory


def destroy_terraform(
        terraform: Terraform,
        plan_only: bool = False,
        **kwargs: dict,
) -> dict:
    temp_dir = TemporaryDirectory()
    terraform_plan_file_path = os.path.join(temp_dir.name, "main.tfplan")
    return_code, _, _ = terraform.plan(
        destroy=IsFlagged,
        out=terraform_plan_file_path,
        capture_output=False,
        **kwargs,
    )
    if (return_code != 0 and return_code != 2):
        exit(return_code)

    if not plan_only:
        return_code, _, _ = terraform.apply(
            dir_or_plan=terraform_plan_file_path,
            var=None,
            capture_output=False,
        )
        if (return_code != 0):
            exit(return_code)

    temp_dir.cleanup()


def _test():
    raise NotImplementedError


if __name__ == "__main__":
    _test()
