# edited the category of Rank : 73045 (unknown -> General, else need to drop the row) in R3.csv
# generate_inference_table.py

import pandas as pd
import numpy as np

# -------------------------------
# File paths
R1_FILE = "R1.csv"
R2_FILE = "R2.csv"
R3_FILE = "R3.csv"

# -------------------------------
# Load CSVs
r1_cols = ["Sno", "Rank", "Allocated Quota", "Allotted Institute", "Course", "Allotted Category", "Candidate Category", "Remarks"]
r2_cols = ["Sno", "Rank", "R1 Allocated Quota", "R1 Allotted Institute", "R1 Course", "R1 Remarks",
           "R2 Allocated Quota", "R2 Allotted Institute", "R2 Course", "Allotted Category", "Candidate Category", "Option No.", "Remarks"]
r3_cols = ["Sno", "Rank", "R1 Allocated Quota", "R1 Allotted Institute", "R1 Course", "R1 Remarks",
           "R2 Allocated Quota", "R2 Allotted Institute", "R2 Course", "R2 Remarks",
           "R3 Allocated Quota", "R3 Allotted Institute", "R3 Course", "Allotted Category", "Candidate Category", "Option No.", "Remarks"]

r1 = pd.read_csv(R1_FILE, names=r1_cols).replace("", np.nan)
r2 = pd.read_csv(R2_FILE, names=r2_cols).replace("", np.nan)
r3 = pd.read_csv(R3_FILE, names=r3_cols).replace("", np.nan)

# -------------------------------
# Build final allocations
final_alloc = []

for idx, row in r3.iterrows():
    rank = row["Rank"]

    # If student has seat in R3
    if pd.notna(row["R3 Allotted Institute"]):
        final_alloc.append({
            "Rank": rank,
            "Institute": row["R3 Allotted Institute"],
            "Course": row["R3 Course"],
            "Quota": row["R3 Allocated Quota"],
            "Category": row["Allotted Category"],
            "Candidate Category": row["Candidate Category"],
            "Round": "R3"
        })
    
    # If seat not in R3, but in R2
    elif pd.notna(row["R2 Allotted Institute"]):
        # Get corresponding row from R2
        r2_row = r2[r2["Rank"] == rank]
        if not r2_row.empty:
            r2_row = r2_row.iloc[0]
            final_alloc.append({
                "Rank": rank,
                "Institute": r2_row["R2 Allotted Institute"],
                "Course": r2_row["R2 Course"],
                "Quota": r2_row["R2 Allocated Quota"],
                "Category": r2_row["Allotted Category"],
                "Candidate Category": r2_row["Candidate Category"],
                "Round": "R2"
            })
    
    # If only seat in R1
    elif pd.notna(row["R1 Allotted Institute"]):
        # Get corresponding row from R1
        r1_row = r1[r1["Rank"] == rank]
        if not r1_row.empty:
            r1_row = r1_row.iloc[0]
            final_alloc.append({
                "Rank": rank,
                "Institute": r1_row["Allotted Institute"],
                "Course": r1_row["Course"],
                "Quota": r1_row["Allocated Quota"],
                "Category": r1_row["Allotted Category"],
                "Candidate Category": r1_row["Candidate Category"],
                "Round": "R1"
            })

final_df = pd.DataFrame(final_alloc)


# debug
# final_df.to_csv("debug_final_df.csv", index=False)
# final_df is missing candidcate category and alloted category details for R1 and R2
# -------------------------------
final_df["Rank"] = pd.to_numeric(final_df["Rank"], errors="coerce")
# final_df.to_csv("debug_final_df_.csv", index=False)
# print(len(final_df))
# error here dropping rows with nan value for the col in the below set
final_df = final_df.dropna(subset=["Rank", "Institute", "Course", "Quota", "Category", "Candidate Category"])
# print(len(final_df))
# final_df.to_csv("debug_final_df_after_dropping.csv", index=False)

# final_df.to_csv("debug_final_df_2.csv", index=False)
# -------------------------------
# Inference table generation
rank_stats = final_df.groupby(
    ["Institute", "Course", "Quota", "Candidate Category"]
).agg(
    Min_Rank=("Rank", "min"),
    Max_Rank=("Rank", "max"),
    Count=("Rank", "count")
).reset_index()

percentile_40 = final_df.groupby(["Institute"]).agg(
    Percentile_40=("Rank", lambda x: np.percentile(x, 40))
).reset_index()

inference = pd.merge(rank_stats, percentile_40, on="Institute", how="left")

round_info = final_df.groupby(
    ["Institute", "Course", "Quota", "Candidate Category"]
).agg(
    Most_Probable_Round=("Round", lambda x: x.mode().iloc[0] if not x.mode().empty else "NA")
).reset_index()

inference = pd.merge(inference, round_info, on=["Institute", "Course", "Quota", "Candidate Category"], how="left")

# Save to CSV
inference.to_csv("inference_table.csv", index=False)
print("✅ inference_table.csv has been created successfully.")
