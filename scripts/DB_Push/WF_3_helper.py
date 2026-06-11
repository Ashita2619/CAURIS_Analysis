import sys
sys.path.insert(0, '/epi/home/ashita.jawali@kdhe.state.ks.us/Documents/GitHub/CAuris/scripts')

from ms_sql_handler import ms_sql_handler
import pandas as pd
import cx_Oracle as co
import json
from other import add_cols
import numpy as np


class demographics_import():

    def __init__(self, cache_path):

        #print("Path:", cache_path)

        demo_cache = json.load(
            open(cache_path + "/data/demographics.json")
        )

        #print("\nWRITE QUERY LOADED:")
        #print(demo_cache["write_query_tbl1"])

        for item in demo_cache:
            setattr(self, item, demo_cache[item])

    #########################################################
    # GET DEMOGRAPHICS FROM LIMS + EXCEL
    #########################################################

    def get_lims_demographics(self, hsn, date, csv_path):

        self.wgs_run_date = (
            date[:2] + "/" + date[2:4] + "/" + "20" + date[4:]
        )

        #print(self.wgs_run_date)

        unfound_hsn = []

        conn = co.connect(self.lims_connection)

        if not hsn:
            raise ValueError("HSN list empty")

        formatted_hsn = ",".join([f"'{h}'" for h in hsn])

        query = f"""
        SELECT * FROM CANDIDDEMO
        WHERE HSN IN ({formatted_hsn})
        """

        #print(query)

        self.lims_df = pd.read_sql(query, conn)
        
        print("formatted_hsn:", formatted_hsn)
        print("LIMS rows returned:", len(self.lims_df))

        #print(self.lims_df.columns)

        try:
            excel_df = pd.read_excel(
                csv_path + "/C_auris_Metadata.xlsx",
                sheet_name='Sheet1',
                converters={'HSN': int}
            )
        except FileNotFoundError:
            excel_df = pd.DataFrame(
                columns=[
                    'HSN','First Name','Last Name',"Rec'd","WGS Rec'd",
                    'Collected','DOB','Sex','State','Source Site','CO'
                ]
            )

        found_hsn = [str(i) for i in self.lims_df['HSN'].values.tolist()]

        self.no_lims_hsn = pd.DataFrame(columns=excel_df.columns)

        for h in hsn:
            if str(h) not in found_hsn:
                try:
                    r = excel_df.query(f"HSN == {h}")
                    self.no_lims_hsn = pd.concat([r, self.no_lims_hsn], ignore_index=True)
                except Exception as e:
                    print(f"Error querying Excel for HSN {h}: {e}")
                    unfound_hsn.append(h)

        conn.close()
        print("Not found in LIMS or CSV:", unfound_hsn)

    #########################################################
    # FORMAT LIMS DATAFRAME
    #########################################################

    def format_lims_df(self):

        # Normalize LIMS columns FIRST
        self.lims_df = self.lims_df.rename(columns={
            "HSN": "hsn",
            "GENDER": "sex",
            "COUNTY": "county",
            "REPORT_DATE": "wgs_run_date"
        })
        
        print("LIMS COLS:", self.lims_df.columns)

        def safe_to_datetime(x):
            try:
                return pd.to_datetime(x)
            except:
                return pd.NaT

        # Clean Excel DF
        self.no_lims_hsn = self.no_lims_hsn.loc[:, ~self.no_lims_hsn.columns.str.contains('^Unnamed')]

        self.no_lims_hsn['name'] = (
            self.no_lims_hsn['First Name'].fillna('') + " " +
            self.no_lims_hsn['Last Name'].fillna('')
        )

        self.no_lims_hsn['HSN'] = self.no_lims_hsn['HSN'].astype(int)

        # Normalize Excel columns
        self.no_lims_hsn = self.no_lims_hsn.rename(columns={
            "Rec'd": "date_recd",
            "WGS Rec'd": "pcr_run_date",
            "HSN": "hsn",
            "Collected": "doc",
            "DOB": "dob",
            "Sex": "sex",
            "State": "state",
            "Source Site": "source",
            "CO": "county",
            "County": "county",
            "county": "county"
        })
        self.no_lims_hsn.columns = self.no_lims_hsn.columns.str.strip()

        # Convert dates
        self.no_lims_hsn['pcr_run_date'] = pd.to_datetime(self.no_lims_hsn['pcr_run_date'], errors='coerce')
        self.no_lims_hsn['date_recd'] = pd.to_datetime(self.no_lims_hsn['date_recd'], errors='coerce')
        self.no_lims_hsn['dob'] = self.no_lims_hsn['dob'].apply(safe_to_datetime)
        self.no_lims_hsn['doc'] = pd.to_datetime(self.no_lims_hsn['doc'], errors='coerce')

        drop_cols = [
            'Extracted','Sequenced','Last Name','First Name','Age',
            'Source Type','Country','Comment','WGS serotype',
            'coverage (calculated from workbook)',
            '#total reads','Clusters passing filter'
        ]

        self.no_lims_hsn = self.no_lims_hsn.drop(columns=[c for c in drop_cols if c in self.no_lims_hsn.columns])

        if 'source' not in self.lims_df.columns:
            self.lims_df['source'] = pd.NA

        self.lims_df = pd.concat([self.lims_df, self.no_lims_hsn], ignore_index=True)
        self.lims_df["county"] = self.lims_df["county"].combine_first(self.no_lims_hsn["county"])

    #########################################################
    # CREATE METRICS DF
    #########################################################

    def create_metrics_df(self, assembly_m):

        records = []

        for hsn, metrics_list in assembly_m.items():
            for metrics in metrics_list:
                records.append({
                    "hsn": int(hsn),
                    "avg_depth": metrics.get("avg_depth_coverage", ""),
                    "assembly_completeness": metrics.get("assembly_completeness", ""),
                    "Total_Num_Reads": metrics.get("trimmed_reads", "")
                })

        self.metrics_df = pd.DataFrame(records)

    #########################################################
    # CREATE CLADE DF
    #########################################################

    def create_clade_df(self, clade_data):

        records = []

        for sample, clade_info in clade_data.items():
            records.append({
                "hsn": int(sample),
                "clade": clade_info.get("clade", "")
            })

        self.clade_df = pd.DataFrame(records)

    #########################################################
    # MERGE DATAFRAMES
    #########################################################

    def merge_dfs(self):

        self.lims_df = self.lims_df.rename(columns={'HSN': 'hsn'})
        self.lims_df['hsn'] = self.lims_df['hsn'].astype(int)
        
        print("LIMS rows:", len(self.lims_df))
        print(self.lims_df[["hsn"]].head())

        print("Metrics rows:", len(self.metrics_df))
        print(self.metrics_df[["hsn"]].head())

        print("LIMS dtype:", self.lims_df["hsn"].dtype)
        print("Metrics dtype:", self.metrics_df["hsn"].dtype)

        self.df = pd.merge(self.lims_df, self.metrics_df, how="left", on="hsn")
        self.df = pd.merge(self.df, self.clade_df, how="left", on="hsn")
    

        #print(self.df.head())

    #########################################################
    # FORMAT FINAL DF
    #########################################################

    def format_dfs(self):

        self.df = self.df.rename(columns=getattr(self, 'demo_names', {}))
        
        # Remove duplicate columns
        self.df = self.df.loc[:, ~self.df.columns.duplicated(keep='last')]

        self.df = add_cols(
            obj=self,
            df=self.df,
            col_lst=getattr(self, 'add_col_lst', []),
            col_func_map=getattr(self, 'col_func_map', {})
        )

        self.df = self.df[getattr(self, 'sample_data_col_order', self.df.columns.tolist())]
       

    #########################################################
    # RUN METRICS FROM EXCEL
    #########################################################

    def assign_run_metrics(self, df, path_to_excel):

        run_metrics = pd.read_excel(
            path_to_excel + "/C_auris_Metadata.xlsx",
            sheet_name="Sheet1",
            converters={"HSN": int}
        )

        for i in range(len(df)):

            hsn = int(df.loc[i, "HSN"])
            res = run_metrics.query(f"HSN == {hsn}")

            if not res.empty:

                if "PhiX recovery" in res.columns:
                    df.at[i, "PhiX174_Recovery"] = res["PhiX recovery"].iloc[0]

                if "Q30%" in res.columns:
                    df.at[i, "Q30"] = res["Q30%"].iloc[0]

                if "Cluster density" in res.columns:
                    df.at[i, "Cluster_Density"] = res["Cluster density"].iloc[0]

        return df

    #########################################################
    # RUN ID + WGS METADATA
    #########################################################

    def assign_run_metadata(self, df, run_date, year="26", start_id=1000):

        df = df.copy()

        df["wgs_run_date"] = pd.to_datetime(run_date, errors="coerce")

        return df

    #########################################################
    # DATABASE PUSH
    #########################################################

    def database_push(self, excel_path):

        self.df = self.df.rename(columns={'hsn': 'HSN'})
        self.setup_db()

        self.df["HSN"] = self.df["HSN"].astype(str)

        # FIX METRICS + ID + RUN DATE
        self.df = self.assign_run_metrics(self.df, excel_path)
        self.df = self.assign_run_metadata(self.df, self.wgs_run_date)
        
        self.df = self.df.replace({np.nan: None})

        df_demo_lst = self.df.values.astype(str).tolist()
        print("Insterted rows:" , len(df_demo_lst))
        
        print("Rows to insert:", len(self.df))
        print(self.df[["HSN","clade"]].head(20))
       

        self.db_handler.lst_ptr_push(
            df_lst=df_demo_lst,
            query=self.write_query_tbl1
        )

        print("DB Push Successful")

    #########################################################
    # DB CONNECTION
    #########################################################

    def setup_db(self):
        self.db_handler = ms_sql_handler(self)
        self.db_handler.establish_db()
        
