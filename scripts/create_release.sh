#!/bin/sh

set -e

if [ $# -ne 1 ]; then
    echo "Usage: ./create_release.sh <release version, Major.Minor.Patch format>"
    exit 1
fi

# Set the release version
RELEASE_VERSION="$1"

# Set basename
BASENAME=et_apptainer

# Release name
RELEASE_NAME=${BASENAME}-v${RELEASE_VERSION}

# Clean up any previous releases
rm -rf "$RELEASE_NAME" "${RELEASE_NAME}".tar.gz

# Build the container up to the fourth layer
make layer4_lib.sif

# Set up the release
mkdir "${RELEASE_NAME}"
cp layer4_lib.sif "${RELEASE_NAME}"/os_fab_mpi_lib.sif
cp layer5_et.def "${RELEASE_NAME}"/et.def
sed -i 's/layer4_lib.sif/os_fab_mpi_lib.sif/' "${RELEASE_NAME}"/et.def
cp bns.th "${RELEASE_NAME}"/bns.th
cat << 'EOF' > "${RELEASE_NAME}"/Makefile
# Makefile for layered Apptainer Einstein Toolkit build

THORNLIST ?= bns.th

LIB_IMAGE := os_fab_mpi_lib.sif
ET_INPUT  := et.def
ET_IMAGE  := et_$(THORNLIST:.th=).sif

# Get full path to the thornlist
THORNLIST_FULLPATH := $(shell realpath $(THORNLIST))

all: $(ET_IMAGE)

$(ET_IMAGE): $(ET_INPUT) $(LIB_IMAGE)
	@echo "=== Building Layer 5 --- Einstein Toolkit ==="
	apptainer build --force                              \
		--bind $(THORNLIST_FULLPATH):/input_thornlist.th \
		$(ET_IMAGE) $(ET_INPUT)

clean:
	@echo "=== Cleaning up Einstein  Toolkit image ==="
	rm -f $(ET_IMAGE)
EOF

# Copy the necessary files to the rele
tar czvf "${RELEASE_NAME}".tar.gz "${RELEASE_NAME}"

# Clean up
rm -rf "${RELEASE_NAME}"
