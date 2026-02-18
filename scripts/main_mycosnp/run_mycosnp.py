import pandas as pd
import os
import subprocess
import glob

Clades = {
    "cladeI": "/epi/home/ashita.jawali@kdhe.state.ks.us/Documents/GitHub/CAuris/scripts/refs/CladeI.fna",
    "cladeII": "/epi/home/ashita.jawali@kdhe.state.ks.us/Documents/GitHub/CAuris/scripts/refs/CladeII.fna",
    "cladeIII": "/epi/home/ashita.jawali@kdhe.state.ks.us/Documents/GitHub/CAuris/scripts/refs/CladeIII.fna",
    "cladeIV": "/epi/home/ashita.jawali@kdhe.state.ks.us/Documents/GitHub/CAuris/scripts/refs/CladeIV.fna",
    "cladeV": "/epi/home/ashita.jawali@kdhe.state.ks.us/Documents/GitHub/CAuris/scripts/refs/CladeV.fna"
}

def run_main_mycosnp(summary_csv, run_dir):

    df = pd.read_csv(summary_csv)

    run_date = os.path.basename(run_dir.rstrip("/"))

    output_base = os.path.join(
        "/epi/home/ashita.jawali@kdhe.state.ks.us/WGS_Drive/Cauris/Output/Main_mycosnp",
        run_date
    )
    os.makedirs(output_base, exist_ok=True)

    # Standardize clade names (extract "cladeIII" etc.)
    df['clade_key'] = df['Subtype_Closest_Match'].apply(
        lambda x: x.split("-")[0] if pd.notna(x) else None
    )

    # Process each clade
    for clade_name, group_df in df.groupby('clade_key'):

        if clade_name in Clades:

            ref_path = Clades[clade_name]

            # Create clade-specific samplesheet
            csv_file = os.path.join(run_dir, f"samplesheet_{clade_name}.csv")

            with open(csv_file, "w") as f:
                f.write("sample,fastq_1,fastq_2\n")

                for sample in group_df["Sample"]:

                    r1_files = glob.glob(
                        f"/epi/home/ashita.jawali@kdhe.state.ks.us/WGS_Drive/Cauris/sample_fastq/{run_date}/{sample}*_R1_*.fastq.gz"
                    )

                    r2_files = glob.glob(
                        f"/epi/home/ashita.jawali@kdhe.state.ks.us/WGS_Drive/Cauris/sample_fastq/{run_date}/{sample}*_R2_*.fastq.gz"
                    )

                    if r1_files and r2_files:
                        f.write(f"{sample},{r1_files[0]},{r2_files[0]}\n")
                    else:
                        print(f"FASTQ files not found for sample {sample}")

            print(f"Created {csv_file} for {clade_name}")

            # Create output directory
            clade_output_dir = os.path.join(output_base, clade_name)
            os.makedirs(clade_output_dir, exist_ok=True)

            # Build Nextflow command
            cmd = (
                f"cd {run_dir} && "
                "source $HOME/.bashrc && "
                "source /epi/home/ashita.jawali@kdhe.state.ks.us/mambaforge/etc/profile.d/conda.sh && "
                "conda activate nextflow && "
                "nextflow run CDCgov/mycosnp-nf "
                "-profile docker "
                f"--input {csv_file} "
                f"--fasta {ref_path} "
                f"--outdir {clade_output_dir}"
            )

            print(f"Running pipeline for {clade_name}...")
            result = subprocess.run(cmd, shell=True, executable="/bin/bash")

            if result.returncode != 0:
                print(f"Pipeline failed for {clade_name}")

        else:
            print(f"Warning: Clade '{clade_name}' not found in Clades dictionary.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python run_mycosnp.py <summary_csv> <run_dir>")
        sys.exit(1)

    run_main_mycosnp(sys.argv[1], sys.argv[2])
