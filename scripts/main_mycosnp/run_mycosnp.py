import pandas as pd
import os
import subprocess
import glob
import sys
import re

Clades = {
    "cladeI": "/epi/home/ashita.jawali@kdhe.state.ks.us/Documents/GitHub/CAuris/scripts/refs/CladeI.fna",
    "cladeII": "/epi/home/ashita.jawali@kdhe.state.ks.us/Documents/GitHub/CAuris/scripts/refs/CladeII.fna",
    "cladeIII": "/epi/home/ashita.jawali@kdhe.state.ks.ks.us/Documents/GitHub/CAuris/scripts/refs/CladeIII.fna",
    "cladeIV": "/epi/home/ashita.jawali@kdhe.state.ks.us/Documents/GitHub/CAuris/scripts/refs/CladeIV.fna",
    "cladeV": "/epi/home/ashita.jawali@kdhe.state.ks.us/Documents/GitHub/CAuris/scripts/refs/CladeV.fna",
    "cladeVI": "/epi/home/ashita.jawali@kdhe.state.ks.us/Documents/GitHub/CAuris/scripts/refs/CladeVI.fna"
}


def extract_clade(x):
    if pd.isna(x):
        return None

    match = re.match(r"(clade[IVX]+)-", x)
    if match:
        return match.group(1)

    return None


def run_main_mycosnp(summary_csv, run_dir):
    df = pd.read_csv(summary_csv)

    run_date = os.path.basename(run_dir.rstrip("/"))

    output_base = os.path.join(
        "/epi/home/ashita.jawali@kdhe.state.ks.us/WGS_Drive/Cauris/Output/Main_mycosnp",
        run_date
    )
    os.makedirs(output_base, exist_ok=True)

    df["clade_key"] = df["Subtype_Closest_Match"].apply(extract_clade)

    df = df[df["clade_key"].isin(Clades.keys())]
    df = df.dropna(subset=["clade_key"])

    for clade_name, group_df in df.groupby("clade_key"):

        if clade_name not in Clades:
            print(f"⚠️ Warning: Clade '{clade_name}' not found in Clades dictionary.")
            continue

        ref_path = Clades[clade_name]

        csv_file = os.path.join(run_dir, f"samplesheet_{clade_name}.csv")

        valid_samples = 0

        with open(csv_file, "w") as f:
            f.write("sample,fastq_1,fastq_2\n")

            for sample in group_df["Sample"]:

                r1_files = sorted(glob.glob(
                    f"/epi/home/ashita.jawali@kdhe.state.ks.us/WGS_Drive/Cauris/sample_fastq/{run_date}/{sample}*_R1_*.fastq.gz"
                ))

                r2_files = sorted(glob.glob(
                    f"/epi/home/ashita.jawali@kdhe.state.ks.us/WGS_Drive/Cauris/sample_fastq/{run_date}/{sample}*_R2_*.fastq.gz"
                ))

                if r1_files and r2_files:
                    f.write(f"{sample},{r1_files[0]},{r2_files[0]}\n")
                    valid_samples += 1
                else:
                    print(f"⚠️ FASTQ files not found for sample: {sample}")

        if valid_samples == 0:
            print(f"⚠️ No valid samples for {clade_name}, skipping pipeline run.")
            continue

        # 🔥 KEY CHANGE: allow singleton runs but disable phylogeny
        skip_phylogeny_flag = ""
        if valid_samples == 1:
            print(
                f"⚠️ Only 1 sample for {clade_name}. "
                "Running MycoSNP without phylogeny."
            )
            skip_phylogeny_flag = "--skip_phylogeny "

        print(f"✅ Created {csv_file} with {valid_samples} samples for {clade_name}")

        clade_output_dir = os.path.join(output_base, clade_name)
        os.makedirs(clade_output_dir, exist_ok=True)

        snpeff_flag = "--snpeff true " if clade_name == "cladeI" else ""

        cmd = (
            f"cd {run_dir} && "
            "source $HOME/.bashrc && "
            "source /epi/home/ashita.jawali@kdhe.state.ks.us/mambaforge/etc/profile.d/conda.sh && "
            "conda activate nextflow && "
            "nextflow run CDCgov/mycosnp-nf "
            "-profile docker "
            f"--input {csv_file} "
            f"--fasta {ref_path} "
            f"{snpeff_flag}"
            f"{skip_phylogeny_flag}"
            f"--outdir {clade_output_dir}"
        )

        print(f"\n🚀 Running pipeline for {clade_name}...")
        print("COMMAND:\n", cmd)

        try:
            subprocess.run(cmd, shell=True, executable="/bin/bash", check=True)
            print(f"✅ Completed {clade_name}")

        except subprocess.CalledProcessError as e:
            print(f"❌ Pipeline failed for {clade_name}")
            print(e)
            continue


if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage: python run_mycosnp.py <summary_csv> <run_dir>")
        sys.exit(1)

    run_main_mycosnp(sys.argv[1], sys.argv[2])
