from sqlalchemy import create_engine, text
import pandas as pd
import re
import time
import sys
import math
import traceback
import warnings

warnings.filterwarnings("ignore")


class ms_sql_handler:

    #################################################
    # INIT
    #################################################

    def __init__(self, obj):

        self.sql_user = obj.sql_user
        self.sql_pass = obj.sql_pass
        self.sql_server = obj.sql_server
        self.sql_db = obj.sql_db

        self.avg_depth_cutoff = getattr(obj, "avg_depth_cutoff", None)
        self.percent_cvg_cutoff = getattr(obj, "percent_cvg_cutoff", None)

        self.engine = None

    #################################################
    # CONNECT
    #################################################

    def establish_db(self):

        try:

            conn_string = (
                f"mssql+pyodbc://{self.sql_user}:{self.sql_pass}"
                f"@{self.sql_server}/{self.sql_db}"
                "?driver=ODBC+Driver+17+for+SQL+Server"
            )

            self.engine = create_engine(conn_string)

            print("SQL Engine Created")

        except Exception as e:

            print("Database Connection Error:")
            print(e)

            time.sleep(5)
            sys.exit()

    #################################################
    # CLEAR TABLES
    #################################################

    def clear_db(self):

        with self.engine.connect() as conn:

            conn.execute(text("DELETE FROM dbo.Results"))
            conn.execute(text("DELETE FROM dbo.Run_Stats"))

    #################################################
    # READ FUNCTIONS
    #################################################

    def ss_read(self, query=None):

        return pd.read_sql(text(query), con=self.engine)

    def sub_read(self, query=None):

        return pd.read_sql(text(query), con=self.engine)

    def sub_lst_read(self, query=None, lst=None):

        hsn_query = "(" + ", ".join(lst) + ")"

        local_query = query.replace(
            "{hsn_query}",
            hsn_query
        )

        return pd.read_sql(
            text(local_query),
            con=self.engine
        )

    #################################################
    # SIMPLE SQL PUSH
    #################################################

    def to_sql_push(
        self,
        df=None,
        tbl_name=None,
        u_if_exists="append",
        u_index=False
    ):

        df.to_sql(
            tbl_name,
            self.engine,
            if_exists=u_if_exists,
            index=u_index
        )

    #################################################
    # LIST PUSH
    #################################################

    def lst_push(
        self,
        df_lst=None,
        df_cols=None
    ):

        with self.engine.connect() as conn:

            for row in df_lst:

                row = format_lst(row)

                row_query = (
                    "(" +
                    ", ".join(row) +
                    ")"
                )

                query = (
                    f"INSERT INTO dbo.Run_Stats "
                    f"{df_cols} "
                    f"VALUES {row_query}"
                )
                
                sql = " ".join(query)

                conn.execute(text(query))

    #################################################
    # LIST POINTER PUSH
    #################################################

    def lst_ptr_push(
        self,
        df_lst=None,
        query=None,
        full=False,
        df=None
    ):

        print("trying to connect to sql")

        if query is None:

            raise ValueError(
                "query passed to lst_ptr_push is None"
            )

        print("Query type:", type(query))

        with self.engine.connect() as conn:

            print("connection passed!")

            with conn.begin():

                for row_num in range(len(df_lst)):

                    try:

                        #################################################
                        # START QUERY
                        #################################################

                        new_query = str(query)

                        #################################################
                        # FULL DATAFRAME MODE
                        #################################################

                        if full and df is not None:

                            valid_cols = []

                            for col in df.columns:

                                value = df.iloc[row_num][col]

                                if pd.isna(value):
                                    continue

                                if str(value) in [
                                    "None",
                                    "nan",
                                    "extraction only, WGS"
                                ]:
                                    continue

                                valid_cols.append(col)

                            df_table_col_query = (
                                "(" +
                                ", ".join(valid_cols) +
                                ") "
                            )

                            new_query = new_query.replace(
                                "{df_table_col_query}",
                                df_table_col_query
                            )

                        #################################################
                        # DEBUG
                        #################################################

                        print("\n====================")
                        print("ROW:", row_num)
                        print("QUERY TYPE:", type(new_query))
                        print("RAW QUERY:")
                        print(new_query)
                        print("====================\n")

                        #################################################
                        # FIND PLACEHOLDERS
                        #################################################

                        query_track = list(
                            set(
                                re.findall(
                                    r"({.*?})",
                                    new_query
                                )
                            )
                        )

                        #################################################
                        # REPLACE PLACEHOLDERS
                        #################################################

                        for item in query_track:

                            try:

                                idx = int(item[1:-1])

                            except ValueError:

                                continue

                            try:

                                value = df_lst[row_num][idx]

                            except IndexError:

                                print(
                                    f"Missing index {idx} "
                                    f"for row {row_num}"
                                )

                                continue

                            if pd.isna(value):

                                value = "NULL"

                            else:

                                value = str(value)

                                value = value.replace(
                                    "'",
                                    ""
                                )

                            new_query = new_query.replace(
                                item,
                                value
                            )

                        #################################################
                        # CLEANUP
                        #################################################

                        replacements = {

                            "CAST('nan' AS DATE)": "NULL",
                            "'None'": "NULL",
                            "None": "NULL",
                            "'nan'": "NULL",
                            "= '',": "= NULL,",
                            '= "",': "= NULL,",
                            "= 'None',": "= NULL,",
                            "luke's": "lukes"

                        }

                        for old, new in replacements.items():

                            new_query = new_query.replace(
                                old,
                                new
                            )

                        #################################################
                        # FINAL QUERY DEBUG
                        #################################################

                        print("FINAL QUERY:")
                        print(new_query)

                        #################################################
                        # EXECUTE
                        #################################################

                        conn.execute(
                            text(new_query)
                        )

                    except Exception as e:

                        print("\nSQL ERROR")
                        print("ROW:", row_num)
                        print("ERROR:", e)

                        traceback.print_exc()

                        raise

        print("DB Push Successful")


#################################################
# FORMAT LIST
#################################################

def format_lst(lst):

    formatted = []

    for value in lst:

        if value is None:

            formatted.append("NULL")
            continue

        if pd.isna(value):

            formatted.append("NULL")
            continue

        if isinstance(value, (int, float)):

            formatted.append(str(value))
            continue

        value = str(value)

        value = value.replace(
            "'",
            ""
        )

        formatted.append(
            f"'{value}'"
        )

    return formatted
