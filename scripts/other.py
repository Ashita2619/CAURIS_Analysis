# other_cauris.py

import datetime
import pandas as pd
import numpy as np
import os
import re

import warnings

#########################################################
# FORMAT FUNCTIONS
#########################################################

def format_facility(row, facility_replace_dict):

    if pd.isna(row['facility']):
        return None
    elif row['facility'] == "" or str(row['facility']).lower() == "nan" :
        return None
    else:
        facility = str(row['facility']).lower()
        for key in facility_replace_dict.keys():
            facility = facility.replace(key, facility_replace_dict[key])
        return facility.lower()


def parse_category(row, parse_category_dict):
    facility = str(row['facility']).lower()
    for key in parse_category_dict.keys():
        if re.search(key, facility):
            return parse_category_dict[key]
    return None
    
def format_sex(row, col):
    if col not in row.index:
        return None
        
    val = str(row[col]).strip().upper()
    if pd.isna(row[col]) or val in ["","UNKNOWN","U"]:
        return "Unknown"
    if val in ["M","MALE"]:
        return "Male"
    if val in ["F","FEMALE"]:
        return "Female"
    return "Unknown"


def format_source(row, obj):
    """Map source to standard code using format_source_dict."""
    source = str(row.get("source", "")).lower()
    return obj.format_source_dict.get(source, "OT")


def format_f_name(row, obj):
    """Extract first name from full name."""
    name = str(row.get("name", ""))
    parts = name.strip().split()
    if len(parts) > 1:
        return parts[0]
    return name


def format_l_name(row, obj=None):
    name = str(row.get("name", "")).strip()
    parts = name.split()
    if len(parts)>2:
       return ""
       
    last = parts[-1]
    if obj is not None and last.lower() is getattr(obj, 'not_real_l_names', []):
        return ""
    return last.title()

def format_race(row, obj= None):
    if pd.isna(row['race']) or row['race'] == "U":
        return "Unknown"
    elif row['race'] == "":
        return "Unknown"
    elif str(row['race']).upper() == "W":
        return "White"
    else:
        return str(row['race'])
        
        
def format_dob(row, obj):
    """Ensure dob is a datetime object."""
    dob = row.get("dob")
    if pd.isna(dob):
        return pd.NaT
    try:
        return pd.to_datetime(dob)
    except:
        return pd.NaT


def format_doc(row, obj):
    """Ensure collection date is datetime."""
    doc = row.get("doc")
    if pd.isna(doc):
        return pd.NaT
    try:
        return pd.to_datetime(doc)
    except:
        return pd.NaT


def format_date_recd(row, obj):
    """Ensure date received is datetime."""
    date_recd = row.get("date_recd")
    if pd.isna(date_recd):
        return pd.NaT
    try:
        return pd.to_datetime(date_recd)
    except:
        return pd.NaT


def format_pcr_run_date(row, obj):
    """Ensure PCR run date is datetime."""
    date = row.get("pcr_run_date")
    if pd.isna(date):
        return pd.NaT
    try:
        return pd.to_datetime(date)
    except:
        return pd.NaT


def wgs_run_date(row, obj):
    """Ensure WGS run date is datetime."""
    date = row.get("wgs_run_date")
    if pd.isna(date):
        return pd.NaT
    try:
        return pd.to_datetime(date)
    except:
        return pd.NaT

def get_age(row, obj=None):

    try:
        born = pd.to_datetime(row["dob"]).date()
    except Exception:
        return -1

    try:
        tested = pd.to_datetime(row["doc"]).date()
    except Exception:
        tested = datetime.date.today()

    if pd.isnull(born) or pd.isnull(tested):
        return -1

    days_in_year = 365.2425

    age = int((tested - born).days / days_in_year)

    return age

def get_today(row, obj= None):
    return datetime.datetime.today().strftime("%Y-%m-%d")

def format_age(row, obj):
    """Calculate age from dob and PCR run date."""
    dob = row.get("dob")
    pcr_date = row.get("pcr_run_date")
    if pd.isna(dob) or pd.isna(pcr_date):
        return np.nan
    return (pcr_date - dob).days // 365
    
    
def format_state(row, state_abbrev):
    if len(str(row["state"])) >=3:
        return str(row["state"])
    elif (not pd.isna(row['state'])):
        return state_abbrev[str(row["state"])]
    else:
        return "unknown"
    
def format_date(row, colName):

    val = row.get(colName, None)

    if isinstance(val, pd.Series):
        val = val.iloc[0] if len(val) else None

    if pd.isna(val):
        return np.nan

    return pd.to_datetime(val, errors="coerce")
        
        
#def get_sex(row, obj):
    #if row["sex"] == "Male":
        #return "M"


#########################################################
# GENERIC FUNCTION TO ADD COLUMNS
#########################################################

def add_cols(obj=None, df=None, col_lst=None, col_func_map=None):

    for k in col_lst:

        if k not in col_func_map:
            if k not in df.columns:
                df[k] = None
            continue

        v = col_func_map[k]

        func_name = v[0]
        func = globals()[func_name]

        arg = v[1] if len(v) > 1 else obj

        try:
            if isinstance(arg, str) and hasattr(obj, arg):
                arg = getattr(obj, arg)

            df[k] = df.apply(lambda row: func(row, arg), axis=1)

        except Exception as e:
            raise RuntimeError(
                f"Error processing column '{k}' with function '{func_name}': {e}"
            )

    return df
