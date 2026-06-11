from DB_Push.WF_3_helper import demographics_import
import os


def run_DB_push(runner_path, sample_hsn, assembly_metrics, clade_data, run_date, csv_paths):

    sample_hsn = [str(x).split("-")[0] for x in sample_hsn]
    sample_hsn = list(dict.fromkeys(sample_hsn))
    
    excel_path = os.path.join("/epi/home/ashita.jawali@kdhe.state.ks.us/WGS_Drive/Cauris/sample_fastq")
    
    #print("Normalized HSNs:", sample_hsn)
    #print("sample_hsn:", sample_hsn)
    #print("assembly_metrics keys:", list(assembly_metrics.keys()))
    #print("clade_data keys:", list(clade_data.keys()))

    if not sample_hsn:
        raise ValueError("sample_hsn is empty before LIMS query")

    import_demo = demographics_import(runner_path)

    import_demo.get_lims_demographics(sample_hsn, run_date, csv_paths)
    #print("LIMS rows:", len(import_demo.lims_df))
    #print("NO LIMS rows:", len(import_demo.no_lims_hsn))
    
    # IMPORTANT
    import_demo.format_lims_df()
    #print("After format_lims_df:")
    #print("LIMS rows:", len(import_demo.lims_df))
    #print(import_demo.lims_df.head())

    # Build metrics dataframe
    import_demo.create_metrics_df(assembly_metrics)
    print("Metrics rows:", len(import_demo.metrics_df))

    # Build clade dataframe
    import_demo.create_clade_df(clade_data)
    #print("Clade rows:", len(import_demo.clade_df))

    # Merge everything
    import_demo.merge_dfs()
    #print("Merged rows:", len(import_demo.df))
    
    #print("\nDUPLICATE COLUMNS:")
    dups = import_demo.df.columns[import_demo.df.columns.duplicated()]
    #print(list(dups))

    #print("\nALL COLUMNS:")
    #print(import_demo.df.columns.tolist())

    # Final formatting
    import_demo.format_dfs()

    # Push to DB
    import_demo.database_push(excel_path)
    
