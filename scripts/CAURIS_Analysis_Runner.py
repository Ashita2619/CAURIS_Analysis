import os
from pre_mycosnp.pre_mycosnp import run_pre_mycosnp
from main_mycosnp.run_mycosnp import run_main_mycosnp

def run_full_pipeline(run_dir):
    # Step 1: PRE_MYCOSNP
    run_pre_mycosnp(run_dir)

    # Step 2: run MycoSNP per clade
    run_date = os.path.basename(run_dir.rstrip("/"))
    summary_csv = os.path.join(
        "/epi/home/ashita.jawali@kdhe.state.ks.us/WGS_Drive/Cauris/Output/Pre_mycosnp",
        run_date,
        "combined", "pre-mycosnp_summary", "pre-mycosnp-summary.csv"
    )

    if not os.path.exists(summary_csv):
        raise FileNotFoundError(f"pre-mycosnp-summary.csv not found: {summary_csv}")

    run_main_mycosnp(summary_csv, run_dir)
    print("Pipeline complete!")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python CAURIS_analysis_runner.py <run_date>")
        sys.exit(1)
    run_full_pipeline(sys.argv[1])
