#!/usr/bin/env bash

# Name of the environment
ENV_NAME="mge_virsorter_env"

# Create the conda environment with Python 3.9
conda create -y -n $ENV_NAME python=3.9

# Activate the environment
conda activate $ENV_NAME

# Install basic dependencies via conda
conda install -y -c conda-forge pandas biopython blast bedtools

# Install MobileElementFinder dependencies
pip install editdistance==0.5.3 pysam==0.15.3 scipy==1.4.0 click==7.0

# Install MobileElementFinder itself
pip install mobileelementfinder

# Install VirSorter2 dependencies
conda install -y -c bioconda virsorter

# Optional: verify installations
echo "Checking MobileElementFinder version:"
mgefinder --version

echo "Checking VirSorter2 version:"
virsorter --version

echo "Environment setup complete! Activate with: conda activate $ENV_NAME"
