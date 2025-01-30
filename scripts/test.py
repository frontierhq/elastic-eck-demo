import os
from helpers.test_terraform import test_terraform


if __name__ == "__main__":
    test_terraform(os.path.join(os.getcwd(), "src", "terraform"))
