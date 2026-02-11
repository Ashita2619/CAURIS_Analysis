# Workflow 0 Script
_______________________________________

## PRE_MYCOSNP Workflow 

<br />

## Overview

<br />

- The pre_mycosnp.py script runs the PRE_MYCOSNP workflow from the CDCgov/mycosnp-nf Nextflow pipeline.
- This step determines the clade classification for each sample and generates a summary file used in downstream analysis.

<br />

## Input

A **samplesheet.csv** file located inside the run directory.

## Required Format:
```
sample, fastq_1, fastq_2
312345, 312345_R1.fastq.gz, 312345_R2.fastq.gz
```

<br />
<br />

## ⚠️ Important:

- fastq_1 and fastq_2 must contain **absolute Linux paths** to the FASTQ files.
- Files must exist at the specified locations before running the pipeline.

## pre_mycosnp.py
- Takes the run directory as input.
- Reads samplesheet.csv.
- Executed the pre_mycosnp workflow
