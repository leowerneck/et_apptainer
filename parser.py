"""YAML parser for Einstein Toolkit Apptainer image"""

import os
import re
import shutil
import sys
import yaml
from typing import Union


class Cluster:
    """
    A simple class that holds data for the cluster configuration
    """

    def __init__(self, name: str, user_cfg: dict):
        self.default_cfg = {
            "blas": "openblas-0.3.30",
            "hdf5": "1.14.6",
            "fftw": "3.3.10",
            "gsl": "2.8",
        }
        cfg = self.default_cfg | (user_cfg or {})
        self.name = name
        self.fab_flavor, self.fab_version = self._get_flavor_and_version(cfg["fab"])
        self.mpi_flavor, self.mpi_version = self._get_flavor_and_version(cfg["mpi"])
        self.blas_flavor, self.blas_version = self._get_flavor_and_version(cfg["blas"])
        self.hdf5_version = self._get_version(cfg["hdf5"])
        self.fftw_version = self._get_version(cfg["fftw"])
        self.gsl_version = self._get_version(cfg["gsl"])
        self.help = f"{name} stack: {cfg['fab']} + {cfg['mpi']}"

    @staticmethod
    def _get_flavor_and_version(value: str) -> tuple[str, str]:
        s = value.strip()
        m = re.match(r"^([A-Za-z0-9_.]+)-(\d+(?:\.\d+){0,2}(?:-[A-Za-z0-9]+)?)$", s)
        if not m:
            raise RuntimeError(f"YAML value '{value}' is ill-formed")

        return m.group(1).lower(), m.group(2)

    @staticmethod
    def _get_version(value: Union[str, int, float]) -> str:
        s = str(value).strip()
        m = re.search(r'(?<!\d)(\d+(?:\.\d+){0,2}(?:-[0-9A-Za-z][0-9A-Za-z.-]*)?)$', s)
        return m.group(1) if m else s

    def __str__(self):
        return f"""--- {self.name} module configuration)
help("{self.help}")
whatis("{self.help}")

--- Ensures only one cluster stack is active
family("cluster")

-- Root for library installation
local root = pathJoin("/opt", "{self.fab_flavor}-{self.fab_version}", "{self.mpi_flavor}-{self.mpi_version}")

-- Export your original env vars (for scripts that expect them)
setenv("CLUSTER_NAME", "{self.name}")
setenv("MPI_FLAVOR"  , "{self.mpi_flavor}")
setenv("MPI_VERSION" , "{self.mpi_version}")
setenv("FAB_FLAVOR"  , "{self.fab_flavor}")
setenv("FAB_VERSION" , "{self.fab_version}")
setenv("BLAS_FLAVOR" , "{self.blas_flavor}")
setenv("BLAS_VERSION", "{self.blas_version}")
setenv("HDF5_VERSION", "{self.hdf5_version}")
setenv("FFTW_VERSION", "{self.fftw_version}")
setenv("GSL_VERSION" , "{self.gsl_version}")
setenv("LIBS_ROOT"   , root)
setenv("LIBS_INC"    , pathJoin(root, "include"))
setenv("LIBS_LIB"    , pathJoin(root, "lib"))
setenv("LIBS_BIN"    , pathJoin(root, "bin"))
setenv("HOME_LORENE" , pathJoin(root, "Lorene"))

-- Paths
prepend_path("PATH",            pathJoin(root, "bin"))
prepend_path("LD_LIBRARY_PATH", pathJoin(root, "lib"))
prepend_path("LIBRARY_PATH",    pathJoin(root, "lib"))
prepend_path("CPATH",           pathJoin(root, "include"))
prepend_path("PKG_CONFIG_PATH", pathJoin(root, "lib/pkgconfig"))
prepend_path("PKG_CONFIG_PATH", pathJoin(root, "share/pkgconfig"))
prepend_path("MANPATH",         pathJoin(root, "share/man"))
"""


class Parser:
    """
    A simple class to parse the cluster configuration YAML file.
    """

    def __init__(self, filename: str, outdir: str) -> None:
        self.infile = filename
        self.outdir = outdir

    def parse(self) -> None:
        clusters = yaml.safe_load(open(self.infile))

        for name, user_cfg in clusters.items():
            outfile = os.path.join(self.outdir, name.lower() + ".lua")
            with open(outfile, "w") as f:
                f.write(f"{Cluster(name, user_cfg)}")

            print(f"Successfully wrote configuration '{outfile}'")


if __name__ == "__main__":
    outdir = os.path.join(sys.argv[2], "cluster")
    shutil.rmtree(outdir, ignore_errors=True)
    os.mkdir(outdir)

    print(f"Outputting cluster configurations to {outdir}/")
    parser = Parser(sys.argv[1], outdir)
    parser.parse()
