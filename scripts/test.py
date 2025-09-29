import os
from py_utils import test_terraform


if __name__ == "__main__":
    test_terraform(os.path.join(os.getcwd(), "src", "terraform"))
