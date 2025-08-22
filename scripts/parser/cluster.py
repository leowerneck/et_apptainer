from typing import Union
from default_urls import get_default_url
from normalize_packages_configuration import normalize_packages_configuration

class Cluster:
    """
    A simple class that holds data for the cluster configuration
    """

    def add_default_cfg_entry(self, pkg: str, flavor: str, version: str):
        self.default_cfg[pkg] = {
            "flavor": flavor,
            "version": version,
            "url": get_default_url(flavor, version),
        }
        self.default_cfg[pkg]["filename"] = self.default_cfg[pkg]["url"].split("/")[-1]

    def __init__(self, name: str, user_cfg: dict):
        # Set up the default configuration
        self.default_cfg = {}
        self.add_default_cfg_entry("blas", "openblas", "0.3.30")
        self.add_default_cfg_entry("hdf5", "hdf5", "1.14.6")
        self.add_default_cfg_entry("fftw", "fftw", "3.3.10")
        self.add_default_cfg_entry("gsl", "gsl", "2.8")

        self.name = name
        self.cfg = self.default_cfg | (user_cfg or {})
        self.cfg = normalize_packages_configuration(self.cfg)

        self.fab = self.cfg["fab"]["flavor"] + "-" + self.cfg["fab"]["version"]
        self.mpi = self.cfg["mpi"]["flavor"] + "-" + self.cfg["mpi"]["version"]
        self.help = f"{self.name} stack: {self.fab} + {self.mpi}"

    def get_configuration_environment_variables(self) -> str:
        string = ""
        for pkg in self.cfg:
            pkg_upper = pkg.upper()
            string += f"""
-- Environment variables for package {pkg}
setenv("{pkg_upper}_FLAVOR"  , "{self.cfg[pkg]['flavor']}")
setenv("{pkg_upper}_VERSION" , "{self.cfg[pkg]['version']}")
setenv("{pkg_upper}_URL"     , "{self.cfg[pkg]['url']}")
setenv("{pkg_upper}_FILENAME", "{self.cfg[pkg]['filename']}")
"""
        return string

    def __str__(self):
        return f"""--- {self.name} module configuration)
help("{self.help}")
whatis("{self.help}")

--- Ensures only one cluster stack is active
family("cluster")

-- Root for library installation
local root = pathJoin("/opt", "{self.fab}", "{self.mpi}")

-- Export your original env vars (for scripts that expect them)
setenv("CLUSTER_NAME" , "{self.name}")
{self.get_configuration_environment_variables()}

-- Standardized directories and paths
setenv("LIBS_ROOT"  , root)
setenv("LIBS_INC"   , pathJoin(root, "include"))
setenv("LIBS_LIB"   , pathJoin(root, "lib"))
setenv("LIBS_BIN"   , pathJoin(root, "bin"))
setenv("HOME_LORENE", pathJoin(root, "Lorene"))

-- Paths
prepend_path("PATH",            pathJoin(root, "bin"))
prepend_path("LD_LIBRARY_PATH", pathJoin(root, "lib"))
prepend_path("LIBRARY_PATH",    pathJoin(root, "lib"))
prepend_path("CPATH",           pathJoin(root, "include"))
prepend_path("PKG_CONFIG_PATH", pathJoin(root, "lib/pkgconfig"))
prepend_path("PKG_CONFIG_PATH", pathJoin(root, "share/pkgconfig"))
prepend_path("MANPATH",         pathJoin(root, "share/man"))
"""

if __name__ == '__main__':
    falcon = Cluster("Falcon", {
        "fab": "ucx-1.15.0",
        "mpi": "openmpi-4.1.6",
        "blas": "openblas-0.3.30",
        "hdf5": "1.14.6",
        "fftw": "3.3.10",
        "gsl": "2.8",
    })
    print(falcon)
