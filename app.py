# NEET College Predictor
import streamlit as st
import pandas as pd

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
