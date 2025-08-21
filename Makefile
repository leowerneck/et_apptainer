# Makefile for layered Apptainer build

# Thorn list, defaults to bns.th
THORNLIST ?= bns.th

# Define inputs
OS_INPUT  := layer1_os.def
FAB_INPUT := layer2_fab.def
MPI_INPUT := layer3_mpi.def
LIB_INPUT := layer4_lib.def
ET_INPUT  := layer5_et.def

# Set image names
OS_IMAGE  := $(OS_INPUT:.def=.sif)
FAB_IMAGE := $(FAB_INPUT:.def=.sif)
MPI_IMAGE := $(MPI_INPUT:.def=.sif)
LIB_IMAGE := $(LIB_INPUT:.def=.sif)
ET_IMAGE  := et_$(THORNLIST:.th=).sif

# Get full path to thornlist
THORNLIST_FULLPATH := $(shell realpath $(THORNLIST))

# Default target: build the final image
all: $(ET_IMAGE)

# Rule to build the final Einstein Toolkit image
# This depends on the ET definition file, the OS base image, and the thornlist
$(ET_IMAGE): $(ET_INPUT) $(LIB_IMAGE)
	@echo "=== Building Layer 5 --- Einstein Toolkit ==="
	apptainer build --force                            \
		--bind $(THORNLIST_FULLPATH):/input_thornlist.th \
		$(ET_IMAGE) $(ET_INPUT)

$(LIB_IMAGE): $(LIB_INPUT) $(MPI_IMAGE)
	@echo "=== Building Layer 4 --- External Libraries ==="
	apptainer build --force $(LIB_IMAGE) $(LIB_INPUT)

$(MPI_IMAGE): $(MPI_INPUT) $(FAB_IMAGE)
	@echo "=== Building Layer 3 --- MPI ==="
	apptainer build --force $(MPI_IMAGE) $(MPI_INPUT)

$(FAB_IMAGE): $(FAB_INPUT) $(OS_IMAGE)
	@echo "=== Building Layer 2 --- Interconnect Fabric ==="
	apptainer build --force $(FAB_IMAGE) $(FAB_INPUT)

$(OS_IMAGE): $(OS_INPUT)
	@echo "=== Building Layer 1 --- Base OS Image ==="
	apptainer build --force $(OS_IMAGE) $(OS_INPUT)

# Rule to clean up generated images
clean:
	@echo "=== Cleaning up generated images ==="
	rm -f $(OS_IMAGE) $(FAB_IMAGE) $(MPI_IMAGE) $(LIB_IMAGE) $(ET_IMAGE)

.PHONY: all clean
