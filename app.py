import streamlit as st
import pandas as pd
from datetime import datetime
import argparse
from common import (
    init_gsheet_streamlit,
    init_gsheet_local,
    log_to_gsheet,
    get_inference_data,
    predict_colleges,
)

def main(local_run=False):
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Header
    st.markdown("<div class='header'><h1>NEET College Predictor (2024)</h1></div>", unsafe_allow_html=True)

    if local_run:
        sheet = init_gsheet_local()
    else:
        sheet = init_gsheet_streamlit()

    inference = get_inference_data()

    col1, col2 = st.columns(2)

    with col1:
        rank = st.number_input("Enter your rank", min_value=1)

        candidate_categories = inference["Candidate Category"].dropna().drop_duplicates().sort_values().reset_index(drop=True)
        courses = inference["Course"].dropna().drop_duplicates().sort_values().reset_index(drop=True)
        quotas = inference["Quota"].dropna().drop_duplicates().sort_values().reset_index(drop=True)

        if "General" in candidate_categories.values:
            default_category_index = int(candidate_categories[candidate_categories == "General"].index[0])
        else:
            default_category_index = 0

        if "MBBS" in courses.values:
            default_courses_index = int(courses[courses == "MBBS"].index[0])
        else:
            default_courses_index = 0

        if "All India" in quotas.values:
            default_quotas_index = int(quotas[quotas == "All India"].index[0])
        else:
            default_quotas_index = 0

        candidate_category = st.selectbox("Select your Candidate Category", candidate_categories, index=default_category_index)
        course = st.selectbox("Select Course", courses, index=default_courses_index)
        quota = st.selectbox("Select Quota", quotas, index=default_quotas_index)

    if st.button("Predict Colleges"):
        log_to_gsheet(sheet, rank, candidate_category, course, quota)
        result = predict_colleges(inference, rank, candidate_category, course, quota)

        with col2:
            if result.empty:
                st.warning("No matching colleges found for the given inputs.")
            else:
                st.success(f"Found {len(result)} matching colleges.")
                for i, row in result.iterrows():
                    with st.expander(f"{row['Institute']} - {row['Course']}"):
                        st.write(f"**Quota:** {row['Quota']}")
                        st.write(f"**Candidate Category:** {row['Candidate Category']}")
                        st.write(f"**Min Rank:** {row['Min_Rank']}")
                        st.write(f"**Max Rank:** {row['Max_Rank']}")
                        st.write(f"**Probability:** {row['Probability']:.2f}%")

    # Footer
    st.markdown("<div class='footer'><p>Made with ❤️ by Jules</p></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", action="store_true", help="Run the app in local mode")
    args = parser.parse_args()
    main(local_run=args.local)
