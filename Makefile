# Makefile for layered Apptainer build

# Thorn list, defaults to bns.th
THORNLIST ?= thornlists/bns.th

# Define inputs
OS_INPUT  := layer1_os.def
FAB_INPUT := layer2_fab.def
MPI_INPUT := layer3_mpi.def
LIB_INPUT := layer4_lib.def
ET_INPUT  := layer5_et.def

# Recipes & images directories
RECIPES_DIR := recipes
IMAGES_DIR  := images

# Full paths to definition files
OS_RECIPE  := $(RECIPES_DIR)/$(OS_INPUT)
FAB_RECIPE := $(RECIPES_DIR)/$(FAB_INPUT)
MPI_RECIPE := $(RECIPES_DIR)/$(MPI_INPUT)
LIB_RECIPE := $(RECIPES_DIR)/$(LIB_INPUT)
ET_RECIPE  := $(RECIPES_DIR)/$(ET_INPUT)

# Set image names
OS_IMAGE  := $(IMAGES_DIR)/$(OS_INPUT:.def=.sif)
FAB_IMAGE := $(IMAGES_DIR)/$(FAB_INPUT:.def=.sif)
MPI_IMAGE := $(IMAGES_DIR)/$(MPI_INPUT:.def=.sif)
LIB_IMAGE := $(IMAGES_DIR)/$(LIB_INPUT:.def=.sif)
ET_IMAGE  := et_$(basename $(notdir $(THORNLIST))).sif

# Get full path to thornlist
THORNLIST_FULLPATH := $(shell realpath $(THORNLIST))

# Default target: build the final image
all: $(ET_IMAGE)

# Ensure images directory exists
$(IMAGES_DIR):
	@mkdir -p $(IMAGES_DIR)

# Rule to build the final Einstein Toolkit image
# This depends on the ET definition file, the OS base image, and the thornlist
$(ET_IMAGE): $(IMAGES_DIR) $(ET_RECIPE) $(LIB_IMAGE)
	@echo "=== Building Layer 5 --- Einstein Toolkit ==="
	apptainer build --force                            \
		--bind $(THORNLIST_FULLPATH):/input_thornlist.th \
		$(ET_IMAGE) $(ET_RECIPE)

$(LIB_IMAGE): $(LIB_RECIPE) $(MPI_IMAGE)
	@echo "=== Building Layer 4 --- External Libraries ==="
	apptainer build --force $(LIB_IMAGE) $(LIB_RECIPE)

$(MPI_IMAGE): $(MPI_RECIPE) $(FAB_IMAGE)
	@echo "=== Building Layer 3 --- MPI ==="
	apptainer build --force $(MPI_IMAGE) $(MPI_RECIPE)

$(FAB_IMAGE): $(FAB_RECIPE) $(OS_IMAGE)
	@echo "=== Building Layer 2 --- Interconnect Fabric ==="
	apptainer build --force $(FAB_IMAGE) $(FAB_RECIPE)

$(OS_IMAGE): $(OS_RECIPE)
	@echo "=== Building Layer 1 --- Base OS Image ==="
	apptainer build --force $(OS_IMAGE) $(OS_RECIPE)

# Rule to clean up generated images
clean:
	@echo "=== Cleaning up generated images ==="
	rm -rf et_*.sif $(IMAGES_DIR)

realclean: clean
	@echo "=== Cleaning up releases ==="
	rm -rf et_apptainer-v*

.PHONY: all clean realclean
