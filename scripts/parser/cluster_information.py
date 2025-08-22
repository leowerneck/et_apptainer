from default_urls import get_default_url

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
        raise ValueError(f"Ill-formed entry '{cfg}' for package '{pkg}'")

    return pkg, cfg

def normalize_cluster_information(clusters: dict) -> dict:
    """
    This function normalizes different dictionary formats obtained by reading
    the clusters.yml file into the expected format. Specifically, all of the
    formats below:
    v1 = {
        "ClusterName": {
            "mpi": "openmpi-4.1.6",
        },
    }
    v2 = {
        "ClusterName": {
            "mpi": {
                "name": "openmpi-4.1.6",
                "url": <some URL>
            },
        },
    }
    v3 = {
        "ClusterName": {
            "mpi": {
                "flavor": "openmpi",
                "version": "4.1.6"
                "url": <some URL>
            },
        },
    }
    will be converted to the expected format, which is v3.

    While normalizing, we will attempt to use a default URL if none is provided.

    Raises
    ======
      ValueError:
        - input dictionary is not in one of the formats above
        - no URL provided for package flavor/version and no default found
    """
    for cluster, pkgs in clusters.items():
        for pkg, cfg in pkgs.items():
            version = ""
            flavor = ""
            if isinstance(cfg, str):
                # Expected formats include:
                #   - pkg: <flavor>-<version>
                #   - pkg: <version>
                flavor, version = get_flavor_and_version_from_str(pkg, cfg)
            elif isinstance(cfg, dict):
                # Expected formats include:
                #   - cfg = { pkg: { name: <flavor>-<version> } }
                #   - cfg = { pkg: { name: <flavor>-<version>, url: <url> } }
                #   - cfg = { pkg: { flavor: <flavor>, version: <version> } }
                #   - cfg = { pkg: { flavor: <flavor>, version: <version>, url: <url>} }
                if "name" in cfg.keys():
                    flavor, version = get_flavor_and_version_from_str(pkg, cfg["name"])
                elif "version" not in cfg.keys():
                    raise ValueError(f"Invalid configuration for package {pkg}")
                elif "flavor" not in cfg.keys() and pkg in ["fab", "mpi", "blas"]:
                    raise ValueError(f"flavor is mandatory for package '{pkg}'")
                else:
                    flavor = cfg.get("flavor", pkg)
                    version = cfg["version"]
            else:
                raise ValueError(f"Invalid configuration for package {pkg}")

            url = get_default_url(flavor, version)
            clusters[cluster][pkg] = {
                "flavor": flavor,
                "version": version,
                "url": url
            }


    return clusters

if __name__ == "__main__":
    from pprint import pprint
    pprint(normalize_cluster_information({
        "Falcon": {
            "fab": {"name": "ucx-1.15.0"},
            "mpi": {"flavor": "openmpi", "version": "4.1.6"},
            "blas": {"name": "openblas-0.3.30"},
            "hdf5": {"name": "1.14.6"},
            "fftw": {"version": "3.3.10"},
            "gsl": {"flavor": "gsl", "version": "2.8"},
        },
    }), indent=2)
