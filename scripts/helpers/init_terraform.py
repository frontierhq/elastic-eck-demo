from python_terraform import IsFlagged, Terraform


def init_terraform(working_dir: str, workspace: str = None):
    terraform = Terraform(working_dir=working_dir)

    print("initialising terraform")
    return_code, _, _ = terraform.init()
    if (return_code != 0):
        exit(return_code)

    if (workspace is not None):
        print(f"selecting workspace {workspace}")
        return_code, x, y = terraform.cmd(
            "workspace select",
            workspace,
            capture_output=False,
            no_color=IsFlagged,
            or_create=IsFlagged,
        )
        if (return_code != 0):
            exit(return_code)

    return terraform


def _test():
    raise NotImplementedError


if __name__ == "__main__":
    _test()
