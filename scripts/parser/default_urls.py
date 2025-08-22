from typing import Union

base_url = "https://github.com/leowerneck/apptainer_libs/raw/refs/heads/main"
packages = {
    "ucx": ["1.15.0"],
    "openmpi": ["4.1.6"],
    "openblas": ["0.3.30"],
    "hdf5": ["1.14.6"],
    "fftw": ["3.3.10"],
    "gsl": ["2.8"],
}


def get_default_url(package: str, version: Union[str, None] = None) -> str:
    """
    Returns the default URL for a specific package and version

    Raises:
        - ValueError if an invalid package name is provided
        - ValueError if an invalid package version is provided
    """
    if package not in packages.keys():
        raise ValueError(f"Invalid package {package}")

    if version is not None and version not in packages[package]:
        raise ValueError(f"Invalid version {version} for package {package}")

    if version is None:
        version = packages[package][0]

    return base_url + "/" + package + "-" + version + ".tar.gz"


if __name__ == "__main__":
    print(get_default_url("openmpi", "4.1.6"))
    print(get_default_url("openmpi"))
    print(get_default_url("hdf5"))
    print(get_default_url("hdf5", "1.14.6"))
    try:
        print(get_default_url("mympi"))
    except ValueError:
        print("Correctly raised ValueError for invalid package name")
    try:
        print(get_default_url("openmpi", "myversion"))
    except ValueError:
        print("Correctly raised ValueError for invalid package version")
