# Einstein Toolkit Apptainer Image Generator

This repository contains [Apptainer](https://apptainer.org/)/[Singularity](https://docs.sylabs.io/guides/3.5/user-guide/introduction.html) recipes for creating a [layered container image](https://dl.acm.org/doi/pdf/10.1145/3569951.3593596) with all of the necessary tools and libraries needed to perform simulations with the [Einstein Toolkit](https://einsteintoolkit.org/).

## Building the Toolkit

For users interested in running the Einstein Toolkit in one of the [supported clusters](#supported-clusters), it is highly recommended to download one of the [releases](https://github.com/leowerneck/et_apptainer/releases) available in this repository. The example below shows how to download release v0.1.0 and build the Einstein Toolkit:
```shell
curl -LO https://github.com/leowerneck/et_apptainer/releases/download/v0.1.0/et_apptainer-v0.1.0.tar.gz
tar xzvf et_apptainer-v0.1.0.tar.gz
cd et_apptainer-v0.1.0.tar.gz
make
./et_bns.sif -v
```
The output from last command should look something like this:
```shell
Einstein Toolkit container ready. Running the Einstein Toolkit.
/et_exe: Version 4.16.0.  Compiled on Aug 21 2025 at 19:50:43
```

## Supported Clusters

As of release v0.2.0, the following clusters are supported:

| **Cluster** | **Fabric** |    **MPI**    |
|:-----------:|:----------:|:-------------:|
|   Falcon    | ucx-1.15.1 | openmpi-4.1.6 |

## Adding Support for Other Clusters :construction:

New clusters can be added by extending the `clusters.yml` file. Each entry should have the following format:
```yml
Name:
  fab: <flavor>-<version>
    url: [url]
    configure: [flags]
  mpi: <flavor>-<version>
    url: [url]
    configure: [flags]
  blas: [flavor-][version] # default openblas-0.3.30
    url: [url]
    configure: [flags]
    make: [flags]
  hdf5: [hdf5-][version]   # default 1.14.6
    url: [url]
    configure: [flags]
  fftw: [fftw-][version]   # default 3.3.10
    url: [url]
    configure: [flags]
  gsl : [gsl-][version]    # default 2.8
    url: [url]
    configure: [flags]
```

The only mandatory entries are `fab` and `mpi`, so the following would be perfectly acceptable:
```yml
MyCluster:
  fab: ucx-1.15.0
  mpi: openmpi-4.1.6
```

### Custom URL :construction:
By default, all libraries are downloaded from a [static repository](https://github.com/leowerneck/apptainer_libs). If you want to use a flavor or version that is not available in it, then you can provide the download URL, for example:
```yml
MyCluster:
  fab: ucx-1.15.0
  mpi: mpich-4.3.1
    url: https://www.mpich.org/static/downloads/4.3.1/mpich-4.3.1.tar.gz
```

### Custom Configure Flags :construction:
Most packages are installed using:
```bash
curl -OL $PACKAGE_URL
tar xzvf ${PACKAGE_FLAVOR}-${PACKAGE_VERSION}.tar.gz
cd ${PACKAGE_FLAVOR}-${PACKAGE_VERSION}
./configure --prefix=${LIBS_ROOT} ${PACKAGE_DEFAULT_CONFIGURE_FLAGS}
make ${PACKAGE_DEFAULT_MAKE_FLAGS}
make install
```
Not all packages work like this. Some packages do not use `configure` at all (like [OpenBLAS](https://github.com/OpenMathLib/OpenBLAS)), while some package flavors or versions may require specific flags to work. Because of this, you can override `PACKAGE_DEFAULT_CONFIGURE_FLAGS` with your own flags.

For example, say you would like to install `mpich-4.3.1` with `ucx-1.15.0`, but currently the repository only supports `openmpi-4.1.6`. The configure flags for `mpich` are different than the ones for `openmpi`, so you could manually override them with the following:
```yml
MyCluster:
  fab: ucx-1.15.0
  mpi: mpich-4.3.1
    url: https://www.mpich.org/static/downloads/4.3.1/mpich-4.3.1.tar.gz
    configure:
      - --with-ucx=${LIBS_ROOT}
      - --with-device=ch4:ucx
      - --with-hwloc=/usr
    # or (not recommended, for readability)
    # configure: [--with-ucx=${LIBS_ROOT}, --with-device=ch4:ucx, --with-hwloc=/usr]
```

Custom configure flags are generally only required when introducing new fabric or mpi flavors, as the parser will select appropriate flags for known combinations.
