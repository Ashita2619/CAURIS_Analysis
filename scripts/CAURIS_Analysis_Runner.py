# CAuris Pipeline

import os
from pre_mycosnp.pre_mycosnp import run_pre_mycosnp
from main_mycosnp.run_mycosnp import run_main_mycosnp
from DB_Push.WF_3_DB_Push import run_DB_push
from Helpers.summary_loader import load_summary_data


class CAURISRunner:
    def __init__(self, cache_path, csv_path):
        self.cache_path = cache_path
        self.csv_path = csv_path

    def run_full_pipeline(self, run_dir):
        # Step 1: Run PRE_MYCOSNP
        print("Running Pre MycoSNP...")
        run_pre_mycosnp(run_dir)

        # Step 2: Run MycoSNP per clade
        run_date = os.path.basename(run_dir.rstrip("/"))
        summary_csv = os.path.join(
            "/epi/home/ashita.jawali@kdhe.state.ks.us/WGS_Drive/Cauris/Output/Pre_mycosnp",
            run_date,
            "combined", "pre-mycosnp_summary", "pre-mycosnp-summary.csv"
        )

        if not os.path.exists(summary_csv):
            raise FileNotFoundError(f"pre-mycosnp-summary.csv not found: {summary_csv}")

        print("Running Main MycoSNP...")
        run_main_mycosnp(summary_csv, run_dir)
        print("Pipeline complete!")

        # Step 3: Push data to the DB (demographical and gene data)
        # Prepare data for the database push
        print("Pushing data to database...")
        sample_HSN, clade_data, assembly_metrics = load_summary_data(summary_csv)

        
        run_DB_push(self.cache_path, sample_HSN, assembly_metrics, clade_data, run_date, self.csv_path)
        print("Data pushed to DB successfully!")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python CAURIS_analysis_runner.py <run_date>")
        sys.exit(1)
    
    run_date = sys.argv[1]
    cache_path = "/epi/home/ashita.jawali@kdhe.state.ks.us/Documents/GitHub/CAuris"  # Specify your cache path
    csv_path = "/epi/home/ashita.jawali@kdhe.state.ks.us/WGS_Drive/Cauris/sample_fastq"  # Specify your CSV path

    # Create a CAURISRunner instance and run the pipeline
    runner = CAURISRunner(cache_path, csv_path)
    runner.run_full_pipeline(run_date)
