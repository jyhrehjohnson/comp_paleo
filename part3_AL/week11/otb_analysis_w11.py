# %% [markdown]
# week11

# %% Setup
import json
import os

import pandas as pd
from sqlalchemy import create_engine

from config import DSN

engine = create_engine(DSN)

# I kept getting a FileNotFound error. Eventhough the file eas in my folder it still
# couldn't find it when it came time to load the JSON file. Claude suggested adding 'week11 +'
# before the file name as a fix and it seems to work!
week11 = "/Users/jyhrehjohnson/Documents/UT/comp_paleo/part3_AL/week11/"
print(os.listdir(week11))

# %% [markdown]
# ## Part 1 - JSON and Data Loading

# %% 1.3 Load JSON file
with open(
    week11 + "ecv_otb_subset.json"
) as f:  # added week11 + to get the .json to work/for the code to call the file
    ecv_raw = json.load(f)

print(type(ecv_raw))
print(ecv_raw["source"])
print(ecv_raw["region"])
print(len(ecv_raw["specimens"]))

# %% 1.4 Make DataFrame
ecv_otb = pd.json_normalize(ecv_raw["specimens"])
print(ecv_otb.dtypes)
print(ecv_otb.shape)

# %% [markdown]
#
# **(a)** What null in JSON becomes in pandas and how it affects column dtype?
# - In Python, a null becomes 'None', which pandas stores as 'NaN'. 'Nan' is float so
# a single null in one column turns the whole column into a float.
#
# **(b)** Why ecv_median_cm3 is float64 in the CSV even when all values are whole
# numbers for some rows?
# - Columns only have one data type. With the median values having decimals the whole column
# is a float.
#
# **(c)** One scientific scenario where you would use dtype on read_csv to
# override the default inference.
# -

# %% 1.5 Load the full csv
ecv_full = pd.read_csv(week11 + "ecv_by_specimen.csv", dtype={"ID": str})
print(ecv_full.shape)
print(ecv_full.dtypes)
print(ecv_full.head())

# %% 1.6 Check JSON subset
print(set(ecv_otb.columns) == set(ecv_full.columns))  # Comes back True
print(ecv_otb["ID"].isin(ecv_full["ID"]).all())  # Comes back True

# %% 1.7 Load otb fossils from Postgres
fossils_sql = pd.read_sql("SELECT * FROM fossils", engine)

# %% Export to csv and reload
fossils_sql.to_csv(week11 + "fossils_export.csv", index=False)
fossils_csv = pd.read_csv(week11 + "fossils_export.csv")

# %% Check - compare dtypes
print("From SQL:")
print(fossils_sql.dtypes)
print("From CSV:")
print(fossils_csv.dtypes)


# %% 1.8 Deliverables - Part 1

# %% [markdown]
# [1]
#
# [2]
# **(a)** What null in JSON becomes in pandas and how it affects column dtype?
# - In Python, a null becomes 'None', which pandas stores as 'NaN'. 'Nan' is float so
# a single null in one column turns the whole column into a float.
#
# **(b)** Why ecv_median_cm3 is float64 in the CSV even when all values are whole
# numbers for some rows?
# - Columns only have one data type. With the median values having decimals the whole column
# is a float.
#
# **(c)** One scientific scenario where you would use dtype on read_csv to
# override the default inference.
# -

# [3]
# **Identifying at least two columns where the dtype differs and explain why the same data
# produces different types depending on the source format.**
# - PostgreSQL follows the database schema so it knows the data type. A CSV does not know
# the data type before hand.

# %% [markdown]
# ## Part 2 - Data Cleaning

# %% 2.1 Missing values
print(ecv_full.isnull().sum)

# %% 2.2 Data quality
print(ecv_full["n_estimates"].value_counts().sort_index())
single = (ecv_full["n_estimates"] == 1).sum()
print(f"{single} of {len(ecv_full)} specimens have n_estimates == 1")
print(ecv_full.groupby(ecv_full["n_estimates"] > 1)["ecv_median_cm3"].mean())

# %% 2.3 Grade labels
grade_labels = {
    "archaic": "Archaic austrlopith",
    "mega": "Robust australopith / Paranthropus",
    "trans": "Transitional (H. habilis)",
    "pre.mod": "Pre-modern Homo",
}
ecv_full["grade_labe"] = ecv_full["grade"].map(grade_labels)

# %% 2.4 Time bins
bins = [0.0, 1.0, 2.0, 2.6, 3.5]
labels = ["Late Pleistocene", "Early Pleistocene", "Plio-Pleistocene", "Pliocene"]
ecv_full["time_bin"] = pd.cut(ecv_full["age_mid_Ma"], bins=bins, labels=labels)
print(ecv_full["time_bin"].value_counts())

# %% Taxon unique values
print(ecv_full["taxon"].unique())

# %% Filter for Paranthropus and Homo only
ecv_full["taxon"] = ecv_full["taxon"].str.strip()
keep = ecv_full["taxon"].str.startswith(("Paranthropus", "Homo", "P.", "H."))
ecv_hominin = ecv_full[keep].copy()

print(ecv_hominin.shape)
print(ecv_hominin["taxon"].unique())

# %% ECV by time bin
ecv_by_bin = ecv_hominin.groupby("time_bin")["ecv_median_cm3"].agg(
    ["mean", "min", "max", "count"]
)
print(ecv_by_bin)

# %% ECV by time bin and grade
ecv_by_bin_grade = ecv_hominin.groupby(["time_bin", "grade"])["ecv_median_cm3"].agg(
    ["mean", "min", "max", "count"]
)
print(ecv_by_bin_grade)

# %% 2.6 Deliverable - Part 2
# [2]
# explaining why you might exclude Australopithecus from a study focused on the Turkana Basin — what does
# the geographic distribution of the species in your dataset tell you?
#
# [3]
#
