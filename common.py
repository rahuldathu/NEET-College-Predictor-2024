import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json

def init_gsheet_streamlit():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    json_creds = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(json_creds, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open("Neet_Predictor_log_Streamlit").sheet1
    return sheet

def init_gsheet_local():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("Neet_Predictor_log_Streamlit").sheet1
    return sheet

def log_to_gsheet(sheet, rank, category, course, quota):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([timestamp, rank, category, course, quota])

from config import INFERENCE_TABLE_FILE

def get_inference_data():
    return pd.read_csv(INFERENCE_TABLE_FILE)

def predict_colleges(inference, rank, candidate_category, course, quota):
    result = inference[
        (inference["Candidate Category"] == candidate_category) &
        (inference["Course"] == course) &
        (inference["Quota"] == quota) &
        (inference["Max_Rank"] >= rank)
    ].sort_values(by="Percentile_40", ascending=True).drop_duplicates(subset=["Institute", "Course"]).reset_index(drop=True)

    # Add probability column
    result["Probability"] = result.apply(
        lambda row: ((row["Max_Rank"] - rank) / (row["Max_Rank"] - row["Min_Rank"])) * 100
        if row["Max_Rank"] != row["Min_Rank"]
        else 100,
        axis=1,
    )
    return result
