import os


def get_env_value(name: str, allow_empty: bool = False) -> str:
    value = os.getenv(name)
    if not allow_empty and value is None:
        raise ValueError(f"Environment variable \"{name}\" is not set")

    return value


def _test():
    raise NotImplementedError


if __name__ == "__main__":
    _test()
