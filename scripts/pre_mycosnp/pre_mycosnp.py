import subprocess
import sys
import os

def run_pre_mycosnp(run_dir):
    # Extract run_date from run_dir
    run_date = os.path.basename(run_dir.rstrip("/"))
    
    samplesheet = os.path.join(run_dir, "samplesheet.csv")
    
    output_dir = f"/epi/home/ashita.jawali@kdhe.state.ks.us/WGS_Drive/Cauris/Output/Pre_mycosnp/{run_date}"

    if not os.path.exists(samplesheet):
        raise FileNotFoundError(f"SampleSheet not found: {samplesheet}")

    cmd = (
        f"cd {run_dir} && "
        "source $HOME/.bashrc && "
        "source /epi/home/ashita.jawali@kdhe.state.ks.us/mambaforge/etc/profile.d/conda.sh && "
        "conda activate nextflow && "
        "nextflow run CDCgov/mycosnp-nf "
        "--workflow PRE_MYCOSNP "
        "-profile docker "
        f"--input {samplesheet} "
        #"--add_sra_file srr.csv "
        f"--outdir {output_dir} "
    )

    subprocess.run(cmd, shell=True, executable="/bin/bash")
    



