import pandas as pd


def load_summary_data(summary_csv):

    df = pd.read_csv(summary_csv)

    sample_HSN = df["Sample"].tolist()

    clade_data = {}

    assembly_metrics = {}

    for _, row in df.iterrows():

        hsn = str(row["Sample"])

        #################################################
        # CLADE
        #################################################

        clade = str(
            row.get("Subtype_Closest_Match", "")
        ).split("-")[0]

        clade_data[hsn] = {

            "clade": clade
        }

        #################################################
        # METRICS
        #################################################

        assembly_metrics[hsn] = [{

            "assembly_length": 
                row.get(
                    "Sample_Assembly_Length",
                    ""
                ),

            "avg_depth_coverage":
                row.get(
                    "Avg_Depth_Coverage",
                    ""
                ),

            "trimmed_reads":
                row.get(
                    "Trimmed_Reads",
                    ""
                )
        }]

    return (
        sample_HSN,
        clade_data,
        assembly_metrics
    )
