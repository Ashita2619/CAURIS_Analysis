import subprocess
import os

def run_pre_mycosnp(run_dir):
    run_date = os.path.basename(run_dir.rstrip("/"))

    samplesheet = os.path.join(run_dir, "samplesheet.csv")
    srr_file = os.path.join(run_dir, "srr.csv")

    output_dir = f"/epi/home/ashita.jawali@kdhe.state.ks.us/WGS_Drive/Cauris/Output/Pre_mycosnp/{run_date}"

    # Decide which input to use
    if os.path.exists(samplesheet):
        file_flag = f"--input {samplesheet} "
    elif os.path.exists(srr_file):
        file_flag = f"--add_sra_file {srr_file} "
    else:
        raise FileNotFoundError("Neither samplesheet.csv nor srr.csv found")

    cmd = (
        f"cd {run_dir} && "
        "source $HOME/.bashrc && "
        "source /epi/home/ashita.jawali@kdhe.state.ks.us/mambaforge/etc/profile.d/conda.sh && "
        "conda activate nextflow && "
        "nextflow run CDCgov/mycosnp-nf "
        "--workflow PRE_MYCOSNP "
        "-profile docker "
        f"{file_flag}"
        f"--outdir {output_dir}"
    )

    subprocess.run(cmd, shell=True, executable="/bin/bash", check=True)
