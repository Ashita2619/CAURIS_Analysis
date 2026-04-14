def run_DB_push(
    runner_path,
    sample_hsn,
    assembly_metrics,
    clade_data,   # 👈 NEW
    run_date,
    csv_paths,
    CDC=False
):

    if not CDC:
        sample_hsn = [x.split("-")[0] for x in sample_hsn]
        sample_hsn = list(dict.fromkeys(sample_hsn))

        assembly_metrics = rname_dict(assembly_metrics)
        clade_data = rname_dict(clade_data)   # 👈 normalize

    import_demo = demographics_import(runner_path)

    # 🧬 Pull demographics
    sample_hsn = import_demo.get_lims_demographics(
        sample_hsn, run_date, csv_paths
    )
    print("lims imported")

    import_demo.format_lims_df()

    # 📊 Metrics
    import_demo.create_metrics_df(assembly_metrics, CDC)

    # 🧬 Clade typing (NEW)
    import_demo.create_clade_df(clade_data)

    # 🔗 Merge everything
    import_demo.merge_dfs()

    import_demo.format_dfs()

    # 💾 Push to DB
    import_demo.database_push(csv_paths, run_date)
