# General Package for State Lab C. auris Detection

# Running Analysis
The pipeline runs the [CDCgov/mycosnp-nf](https://github.com/CDCgov/mycosnp-nf) Nextflow workflow for detection of **Candida auris** Variants, Clades, SNP distances and Phylogenetic Analysis.

Run [CAURIS Runner Script] (scripts/CAURIS_Analysis_Runner.py) which takes the rundate (MMDDYY)
```python 
  python CAURIS_Analysis_Runner.py RunDate
```
 > See 

<br />

# The package contains the following workflows in their respective subdirectories:
<br />


### **Workflow 0:** [Pre_mycosnp](/docs/pre_mycosnp.md)
- Runs the **Pre-Mycosnp** workflow
- Takes in the samplesheet and give you Fungal taxonomic classification and Candida auris clade typing, using de novo assemblies

<br />
<br />

### **Workflow 1:** [Main_mycosnp](/docs/run_mycosnp.md)
- Takes the specific csv files for each group of clades (I,II,III,IV,V)
- Runs the **Main MycoSNP** workflow
 
<br />

# Input and Output

- **Input**: The pipeline expects a **samplesheet.csv** file containing FASTQ files for each sample.
     - The file should contain the columns **sample, fastq_1, and fastq_2**.
- **Output**: Results are saved to a directory inside /Output/ for each workflow:
     - /Output/Pre_mycosnp/{run_date}/results/combined/pre-mycosnp_summary/ for the Pre-Mycosnp workflow.
     - /Output/Main_mycosnp/{run_date}/{clade}/ for the Main MycoSNP workflow (each clade will have its own folder).

<br />

# Troubleshooting

- **Missing FASTQ files**: Ensure that the samplesheet.csv has the correct paths to the FASTQ files. <br />
        If the workflow complains that a file is missing, verify that the files exist in the specified location.
- **Nextflow/Docker issues**: Make sure that you have the necessary Nextflow and Docker versions installed. You can check the version by running: <br />
        --> nextflow -v <br />
        --> docker --version

  <br />

  # Dependencies

  - **Nextflow** (version 21.x or above)
  - **Docker** (for running workflows inside containers)
  - **Python 3.8**
 
    <br />
