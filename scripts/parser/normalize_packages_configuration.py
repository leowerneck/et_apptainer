from default_urls import get_default_url
from parser_exceptions import *


def get_flavor_and_version_from_str(pkg: str, cfg: str) -> tuple[str, str]:
    """
    Returns a package's flavor and version from the configuration string.
    Expected formats are:
      - cfg = <flavor>-<version> (pkg ignored)
      - cfg = <version> and pkg = <flavor>
    If pkg in ["mpi", "fab", "blas"], the first format is enforced.
    """
    if "-" in cfg:
        flavor, version = cfg.strip().split("-", maxsplit=1)
        return flavor, version

    if pkg in ["mpi", "fab", "blas"]:
        raise ValueError

    return pkg, cfg


def normalize_packages_configuration(cluster: dict) -> dict:
    """
    This function normalizes different dictionary formats obtained by reading
    the clusters.yml file into the expected format. Specifically, all of the
    formats below:
    v1 = {
        "mpi": "openmpi-4.1.6",
    }
    v2 = {
        "mpi": {
            "name": "openmpi-4.1.6",
            "url": <some URL>
        },
    }
    v3 = {
        "mpi": {
            "flavor": "openmpi",
            "version": "4.1.6"
            "url": <some URL>
        },
    }
    will be converted to the expected format, which is v3 + a "filename" key.

    While normalizing, we will attempt to use a default URL if none is provided.

    Raises
    ======
      MissingFlavorError: package flavor is missing
      MissingVersionError: package version is missing
      InvalidYAMLFormatError: ill-formed package configuration
    """
    for pkg, cfg in cluster.items():
        version = ""
        flavor = ""
        if isinstance(cfg, str):
            # Expected formats include:
            #   - cfg = <flavor>-<version>
            #   - cfg = <version>
            flavor, version = get_flavor_and_version_from_str(pkg, cfg)
            url = get_default_url(flavor, version)
        elif isinstance(cfg, dict):
            # Expected formats include:
            #   - cfg = { name: <flavor>-<version> }
            #   - cfg = { name: <flavor>-<version>, url: <url> }
            #   - cfg = { version: <version> }
            #   - cfg = { version: <version>, url: <url> }
            #   - cfg = { flavor: <flavor>, version: <version> }
            #   - cfg = { flavor: <flavor>, version: <version>, url: <url>}
            if "name" in cfg.keys():
                flavor, version = get_flavor_and_version_from_str(pkg, cfg["name"])
                url = cfg.get("url", get_default_url(flavor, version))
            elif "version" not in cfg.keys():
                raise MissingVersionError(f"Package '{pkg}' version is missing")
            elif "flavor" not in cfg.keys() and pkg in ["fab", "mpi", "blas"]:
                raise MissingFlavorError(f"Package '{pkg}' flavor is missing")
            else:
                flavor = cfg.get("flavor", pkg)
                version = cfg["version"]
                url = cfg.get("url", get_default_url(flavor, version))
        else:
            raise InvalidYAMLFormatError(f"Ill-formed YAML for package '{pkg}'")

        cluster[pkg] = {
            "flavor": flavor,
            "version": version,
            "url": url,
            "filename": url.split("/")[-1],
        }

    return cluster


if __name__ == "__main__":
    from pprint import pprint

    pprint(
        normalize_packages_configuration(
            {
               "fab": {"name": "ucx-1.15.0"},
               "mpi": {"flavor": "openmpi", "version": "4.1.6"},
               "blas": {"name": "openblas-0.3.30"},
               "hdf5": {"name": "1.14.6"},
               "fftw": {"version": "3.3.10"},
               "gsl": {"flavor": "gsl", "version": "2.8"},
            }
        ),
        indent=2,
    )
