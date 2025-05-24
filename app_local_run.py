# NEET College Predictor to run locally using Streamlit
# This code is designed to run locally and does not require any external hosting.
# credentials.json should be in the same directory as app.py
# oauth2 might be outdated, use the reference code in app.py
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

def init_gsheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("Neet_Predictor_log_Streamlit").sheet1  
    return sheet

def log_to_gsheet(rank, category, course, quota):
    sheet = init_gsheet()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([timestamp, rank, category, course, quota])

# -------------------------------
# Load inference table
inference = pd.read_csv("inference_table.csv")

# Prepare UI selections
st.title("NEET College Predictor (2024)")

rank = st.number_input("Enter your rank", min_value=1)

# Dynamically create selection options
candidate_categories = inference["Candidate Category"].dropna().drop_duplicates().sort_values().reset_index(drop=True)
courses = inference["Course"].dropna().drop_duplicates().sort_values().reset_index(drop=True)
quotas = inference["Quota"].dropna().drop_duplicates().sort_values().reset_index(drop=True)

# Set default index for candidate category
if "General" in candidate_categories.values:
    default_category_index = int(candidate_categories[candidate_categories == "General"].index[0])
else:
    default_category_index = 0

# Set default index for courses and quotas
if "MBBS" in courses.values:
    default_courses_index = int(courses[courses == "MBBS"].index[0])
else:
    default_courses_index = 0

# Set default index for quotas
if "All India" in quotas.values:
    default_quotas_index = int(quotas[quotas == "All India"].index[0])



candidate_category = st.selectbox("Select your Candidate Category", candidate_categories, index=default_category_index)
course = st.selectbox("Select Course", courses, index=default_courses_index)
quota = st.selectbox("Select Quota", quotas, index=default_quotas_index)
# -------------------------------
# Predict colleges based on user input

if st.button("Predict Colleges"):
    log_to_gsheet(rank, candidate_category, course, quota)

    result = inference[
        (inference["Candidate Category"] == candidate_category) &
        (inference["Course"] == course) &
        (inference["Quota"] == quota) &
        (inference["Max_Rank"] >= rank)
    ].sort_values(by="Percentile_40", ascending=True).drop_duplicates(subset=["Institute", "Course"]).reset_index(drop=True)

    if result.empty:
        st.warning("No matching colleges found for the given inputs.")
    else:
        st.success(f"Found {len(result)} matching colleges.")
        st.dataframe(result)
