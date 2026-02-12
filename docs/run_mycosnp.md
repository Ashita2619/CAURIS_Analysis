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
| Clade_I  | CladeI.fna  | 
| Clade_II | CladeII.fna | 
| Clade_III| CladeIII.fna| 
| Clade_IV | CladeIV.fna | 
| Clade_V  | CladeV.fna  | 

