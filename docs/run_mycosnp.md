# Workflow 1 Script
_______________________________________

## MAIN_MYCOSNP Workflow

<br />

## Overview

<br />

The run_mycosnp.py script runs the MAIN_MYCOSNP workflow from the CDCgov/mycosnp-nf Nextflow pipeline.

This step:

1. Reads the pre-mycosnp-summary.csv generated from the PRE_MYCOSNP workflow.
2. Extracts clade information for each sample.
3. Splits samples by clade.
4. Selects the appropriate clade-specific reference genome.
5. Runs the MAIN_MYCOSNP workflow separately for each clade.

<br />

## Reference Genomes 

<br />

Each Clade is mapped to a specific reference genome:
| Clade | Reference FASTA |
| :--- | :---: | 
| Clade_I  | [CladeI.fna](https://www.ncbi.nlm.nih.gov/datasets/genome/GCA_016772135.1/)  | 
| Clade_II | [CladeII.fna](https://www.ncbi.nlm.nih.gov/datasets/genome/GCF_003013715.1/) | 
| Clade_III| [CladeIII.fna](https://www.ncbi.nlm.nih.gov/datasets/genome/GCF_002775015.1/)| 
| Clade_IV | [CladeIV.fna](https://www.ncbi.nlm.nih.gov/datasets/genome/GCA_008275145.1/) | 
| Clade_V  | [CladeV.fna](https://www.ncbi.nlm.nih.gov/datasets/genome/GCA_016809505.1/)  | 

<br />

These refernces are defined inside run_mycosnp.py

## What the script does

<br />

For each detected clade:
1. Fillters samples belonging to that clade.
2. Creates a clade-specific samplesheet.
3. Runs the nextflow command to run the mycosnp pipeline.

