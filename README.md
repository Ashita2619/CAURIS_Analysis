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
- Runs the Pre-Mycosnp workflow
- Takes in the samplesheet and give you Fungal taxonomic classification and Candida auris clade typing, using de novo assemblies

<br />
<br />

### **Workflow 1:** [Main_mycosnp](/docs/run_mycosnp.md)
- Takes the specific csv files for each group of clades (I,II,III,IV,V)
- Runs the Main MycoSNP workflow

  
<br />
<br />
