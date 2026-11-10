# %% [markdown]
# week11

# %% Setup
import json
import os

import matplotlib.pyplot as plt
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

# %% 1.5 Load the full csv
ecv_full = pd.read_csv(week11 + "ecv_by_specimen.csv", dtype={"ID": str})
print(ecv_full.shape)
print(ecv_full.dtypes)
print(ecv_full.head())

# %% 1.6 Check JSON subset
print(set(ecv_otb.columns) == set(ecv_full.columns))  # Comes back True
print(ecv_otb["ID"].isin(ecv_full["ID"]).all())  # Comes back True

# %% 1.7 Load otb fossils from Postgres
fossils_sql = pd.read_sql(
    "SELECT * FROM fossils", engine
)  # make sure Postgres server is connected

# %% Export to csv and reload
fossils_sql.to_csv(week11 + "fossils_export.csv", index=False)
fossils_csv = pd.read_csv(week11 + "fossils_export.csv")

# %% Check - compare dtypes
print("From SQL:")
print(fossils_sql.dtypes)
print("From CSV:")
print(fossils_csv.dtypes)

# %% [markdown]
# ## 1.8 Deliverables - Part 1
# [1]
# INPUT: print(ecv_otb.dtypes)
#        print(ecv_otb.shape)
#
# OUTPUT:
# ID                    str
# taxon                 str
# grade                 str
# ecv_median_cm3    float64
# n_estimates         int64
# age_mid_Ma        float64
# age_lo_Ma         float64
# age_hi_Ma         float64
# dtype: object
# (20, 8)
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
# - When using catalog numbers. If a dataset stores the prefix ("KNM-ER") in one column and
# the number ("1470") in another, pandas would read the number column as 'int64'. That drops
# leading zeros and an integer column will not match a text column when
# joining. Using dtype = catalog_number: str keeps the values as text.

# [3]
# **Identifying at least two columns where the dtype differs and explain why the same data
# produces different types depending on the source format.**
# - No columns differ in dtype between read_sql and read_csv.
#
# OUTPUT
# From SQL:
# catalog_number                                    str
# organism_id                                       str
# preparations                                      str
# year                                          float64
# discovered_by                                     str
# taxon_id                                        int64
# date_identified                                   str
# verbatim_identification                           str
# locality_id                                     int64
# formation                                         str
# member                                            str
# bed                                               str
# earliest_period_or_lowest_system                  str
# latest_period_or_highest_system                   str
# earliest_epoch_or_lowest_series                   str
# latest_epoch_or_highest_series                    str
# earliest_age_or_lowest_stage                      str
# latest_age_or_highest_stage                       str
# earliest_chronometric_age                     float64
# earliest_chronometric_age_reference_system        str
# latest_chronometric_age                       float64
# latest_chronometric_age_reference_system          str
# verbatim_chronometric_age                         str
# date_created                                      str
# dtype: object

# From CSV:
# catalog_number                                    str
# organism_id                                       str
# preparations                                      str
# year                                          float64
# discovered_by                                     str
# taxon_id                                        int64
# date_identified                                   str
# verbatim_identification                           str
# locality_id                                     int64
# formation                                         str
# member                                            str
# bed                                               str
# earliest_period_or_lowest_system                  str
# latest_period_or_highest_system                   str
# earliest_epoch_or_lowest_series                   str
# latest_epoch_or_highest_series                    str
# earliest_age_or_lowest_stage                      str
# latest_age_or_highest_stage                       str
# earliest_chronometric_age                     float64
# earliest_chronometric_age_reference_system        str
# latest_chronometric_age                       float64
# latest_chronometric_age_reference_system          str
# verbatim_chronometric_age                         str
# date_created                                      str
# dtype: object

# %% [markdown]
# ## Part 2 - Data Cleaning

# %% 2.1 Missing values
print(ecv_full.isnull().sum())
# Missing ECVs are left as NaN, not filled with the mean (a missing ECV means the
# braincase could not be measured). groupby means skip NaN automatically.

# %% 2.2 Data quality
print(ecv_full["n_estimates"].value_counts().sort_index())
single = (ecv_full["n_estimates"] == 1).sum()
print(f"{single} of {len(ecv_full)} specimens have n_estimates == 1")
print(ecv_full.groupby(ecv_full["n_estimates"] > 1)["ecv_median_cm3"].mean())

# %% 2.3 Grade labels
grade_labels = {
    "archaic": "Archaic australopith",
    "mega": "Robust australopith / Paranthropus",
    "trans": "Transitional (H. habilis)",
    "pre.mod": "Pre-modern Homo",
}
ecv_full["grade_label"] = ecv_full["grade"].map(grade_labels)
print(ecv_full["grade_label"].value_counts())

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

# %% [markdown]
# ## 2.6 Deliverable - Part 2
# [2]
# **Explain why you might exclude Australopithecus from a study focused on the
# Turkana Basin — what does the geographic distribution of the species in your
# dataset tell you?**
#
# Australopithecus ECVs come from outside the Omo-Turkana Basin:
# Au. afarensis is from Hadar, Au. africanus is from South Africa, and
# Au. garhi is from Bouri. The Turkana Australopithecus record is mostly teeth and mandibles, with no endocasts to measure.
# Paranthropus and Homo are both present and have speciemens that can be measured
# from the basin.
#
#
# [3]
# **Interpretation.**
# Mean ECV increases toward the present or modern time.
# Older bins are mostly Paranthropus (about 400-550 cm³) while younger bins
# contain only Homo after Paranthropus disappears around 1.4 Ma.
#
# When looking at things by grade the trend is not the same for each grade:
# - `mega` (Paranthropus) stays the same.
# - `trans` (H. habilis) only appears in one bin but has a wide range ~500 (KNM-ER 1813) to ~750-790 (KNM-ER 1470).
# - `pre.mod` (Homo erectus and later) increases, but the youngest bin has
#   few specimens.

# %% [markdown]
# ## Part 3 - Joining Data

# %% 3.2 Preparing the join
fossils = pd.read_sql(
    "SELECT f.*, t.scientific_name FROM fossils f JOIN taxa t USING (taxon_id)", engine
)

# Fix names
name_fix = {
    'Australopithecus Dart, 1925': 'Australopithecus',
    'Australopithecus anamensis Leakey et al., 1995': 'Australopithecus anamensis',
    'Hominini': 'Hominini',
    'Homo Linnaeus, 1758': 'Homo',
    'Homo erectus (Dubois, 1892)': 'Homo erectus',
    'Homo habilis Leakey, Tobias & Napier, 1964': 'Homo habilis',
    'Kenyanthropus platyops Leakey et al., 2001': 'Kenyanthropus platyops',
    'Paranthropus Broom, 1938': 'Paranthropus',
    'Paranthropus aethiopicus (Arambourg & Coppens, 1967)': 'Paranthropus aethiopicus',
    'Paranthropus boisei (Leakey, 1959)': 'Paranthropus boisei',
}

fossils['taxon_name'] = fossils['scientific_name'].replace(name_fix)

print("OTB taxa:", sorted(fossils["taxon_name"].unique()))
print("ECV taxa:", sorted(ecv_hominin["taxon"].unique()))

# %% Abbreviate genus names in ECV table
ecv_hominin["taxon"] = ecv_hominin["taxon"].str.replace(
    "P. ", "Paranthropus ", regex=False
)
ecv_hominin["taxon"] = ecv_hominin["taxon"].str.replace("H. ", "Homo ", regex=False)

# %% Reclassify KNM-ER 1470 as Homo rudolfensis in both tables
# (changes the pandas copies only; the database is not changed)
print(fossils.loc[fossils["catalog_number"] == "KNM-ER 1470", ["catalog_number", "taxon_name"]])

fossils.loc[fossils["catalog_number"] == "KNM-ER 1470", "taxon_name"] = "Homo rudolfensis"
ecv_hominin.loc[ecv_hominin["ID"] == "KNM-ER 1470", "taxon"] = "Homo rudolfensis"

print(fossils.loc[fossils["catalog_number"] == "KNM-ER 1470", ["catalog_number", "taxon_name"]])
print(ecv_hominin.loc[ecv_hominin["ID"] == "KNM-ER 1470", ["ID", "taxon"]])

# %% Summarize by taxon
ecv_by_taxon = (
    ecv_hominin.groupby("taxon")["ecv_median_cm3"]
    .agg(
        ecv_mean="mean",
        ecv_median="median",
        ecv_min="min",
        ecv_max="max",
        ecv_n="count",
    )
    .reset_index()
)
print(ecv_by_taxon)

# Left join onto the fossils
fossils_ecv = pd.merge(
    fossils, ecv_by_taxon, left_on="taxon_name", right_on="taxon", how="left"
)
print(fossils.shape)
print(fossils_ecv.shape)

print(fossils_ecv[["catalog_number", "taxon_name", "ecv_mean"]].head(10))

# %%
print(fossils_ecv["ecv_mean"].isnull().sum())
no_ecv = fossils_ecv[fossils_ecv["ecv_mean"].isnull()]
print(no_ecv["taxon_name"].value_counts())

# %% Specimen-level inner join
specimen_join = pd.merge(
    fossils,
    ecv_hominin[["ID", "ecv_median_cm3", "age_lo_Ma", "age_hi_Ma", "n_estimates"]],
    left_on="catalog_number",
    right_on="ID",
    how="inner",
)
print(f"{len(specimen_join)} OTB fossils matched a published ECV measurement")
print(specimen_join[["catalog_number", "taxon_name", "ecv_median_cm3", "n_estimates"]])

# %% Add a time bin to the OTB fossils using stratigraphic ages
print(fossils_ecv["earliest_chronometric_age_reference_system"].unique())

fossils_ecv["age_mid_Ma"] = (fossils_ecv["earliest_chronometric_age"] + fossils_ecv["latest_chronometric_age"]) / 2
fossils_ecv["time_bin"] = pd.cut(fossils_ecv["age_mid_Ma"], bins=bins, labels=labels)
print(fossils_ecv["time_bin"].value_counts())

pivot = fossils_ecv.pivot_table(
    values="ecv_mean",
    index="taxon_name",
    columns="time_bin",
    aggfunc="mean"
)
print(pivot)

# %% [markdown]
# ## Deliverable - Part 3
# [1]
# **Changes made and why:**
# 1. **Names** 
#    The OTB database stores names with the author and year (e.g. "Homo erectus (Dubois, 1892)"), 
#    while Du et al. use the traditional name ("Homo erectus"). 
#    I used the name_fix dict to remove the publication and year. 

# 2. **Abbreviations in the ECV table** ("P. boisei" -> "Paranthropus boisei").
#    This is only a formatting change to match.

# 3. **KNM-ER 1470: Homo habilis -> Homo rudolfensis**
#    I did not rename every "Homo habilis" to "Homo rudolfensis", because that would merge the two species into one. 
#    Changing the one specimen follows the classification already used in the OTB database. The differences
#    in ecv warrant a split until other evidence is provided as to why they should both be H. habilis.
#    I did not rename all H. habilis, because that would decide the habilis/rudolfensis question for every
#    specimen. 
#
# [2]
# **Why fossils_ecv has the same number of rows as fossils.**
# A left join keeps every row of the left table (fossils). Because ecv_by_taxon
# has only one row per taxon, each fossil matches to one row, so no fossil
# is duplicated. Fossils with no match are kept and get NaN. The number of
# columns goes up: (1243, 26) -> (1243, 34).
#
# **Fossils with no ECV.** 
# 718
# This number is made up from Hominini, Homo, Australopithecus, Paranthropus. Two species have no published
# endocast: Australopithecus anamensis, Kenyanthropus platyops.
#
# [3]
# **Small number of specimen matches.** 
# - ECV can only be measured on a fairly complete braincase. Most OTB
#   specimens are teeth, mandibles, and postcrania, so only a small number specimens actually could 
#   have an ECV.
# - Catalog numbers have to be an exact match. "KNM-ER 1470" and "KNM ER 1470"
#   are different strings to pandas.
# - The OTB database catalogs multiple specimens as separate entities under the same organism_id. 
#   database may catalog as separate pieces.
# - Du et al. only include published ECVs well-preserved crania.
#
# [4]
# **Interpreting the pivot table.**
# The Plio-Pleistocene and Early Pleistocene bins, Paranthropus (~440-490 cm3)
# occurs alongside early Homo, so there are several hominin species with very different 
# brain sizes lived in the basin at the same time. 

# %% [markdown]
# ## Part 4 - OTB + ECV Analysis
# %% Mean OTB age and ECV for each taxon that has ECV data
has_ecv = fossils_ecv[fossils_ecv["ecv_mean"].notnull()]
taxon_summary = (
    has_ecv.groupby("taxon_name")
    .agg(mean_age=("age_mid_Ma", "mean"), ecv_mean=("ecv_mean", "mean"))
    .reset_index()
)

# Add the grade back in from the ECV table
grade_by_taxon = ecv_hominin.groupby("taxon")["grade"].first().reset_index()
taxon_summary = pd.merge(
    taxon_summary, grade_by_taxon, left_on="taxon_name", right_on="taxon", how="left"
)
print(taxon_summary)

# Scatter plot, one color per grade
colors = {"mega": "red", "trans": "green", "pre.mod": "blue"}

plt.figure(figsize=(8, 6))
for grade in taxon_summary["grade"].unique():
    subset = taxon_summary[taxon_summary["grade"] == grade]
    plt.scatter(
        subset["mean_age"],
        subset["ecv_mean"],
        color=colors[grade],
        label=grade_labels[grade],
        s=60,
    )

# Taxon labels next to each point
for i, row in taxon_summary.iterrows():
    plt.text(row["mean_age"], row["ecv_mean"] + 10, row["taxon_name"], fontsize=8)

plt.xlabel("Mean specimen age (Ma)")
plt.ylabel("Mean ECV (cm³)")
plt.gca().invert_xaxis()  # older on the left
plt.legend()
plt.tight_layout()
plt.savefig(week11 + "ecv_vs_age.png")
plt.show()

# %% Histogram of n_estimates
plt.figure(figsize=(6, 4))
plt.hist(ecv_hominin["n_estimates"], bins=[0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5])
plt.xlabel("n_estimates")
plt.ylabel("Number of specimens")
plt.savefig(week11 + "n_estimates_hist.png")
plt.show()

frac_single = (ecv_hominin["n_estimates"] == 1).sum() / len(ecv_hominin)
print(f"Fraction with only one estimate: {frac_single:.2f}")

# %% Add locality names from the localities table
localities = pd.read_sql("SELECT * FROM localities", engine)
print(localities.columns.tolist())  

fossils_ecv = fossils_ecv.drop(columns=["place", "place_x", "place_y"], errors="ignore") #Remove place_x and place_y

fossils_ecv = pd.merge(
    fossils_ecv, localities[["locality_id", "place"]], on="locality_id", how="left"
)
print(fossils_ecv[["catalog_number", "locality_id", "place"]].head())

# %% Locality with the most distinct taxa
diversity = (
    fossils_ecv.groupby("place")["taxon_name"].nunique().sort_values(ascending=False)
)
print(diversity.head())

top_locality = diversity.index[0]
print("Most diverse locality:", top_locality)

at_locality = fossils_ecv[fossils_ecv["place"] == top_locality]

# Which formation and member(s) this locality covers
print(at_locality[["formation", "member"]].drop_duplicates())
locality_taxa = at_locality.groupby("taxon_name")["ecv_mean"].mean()
print(locality_taxa)

print("Mean ECV across taxa:", locality_taxa.mean())
print("Range:", locality_taxa.min(), "to", locality_taxa.max())
print(
    "Age span:", at_locality["age_mid_Ma"].min(), "to", at_locality["age_mid_Ma"].max()
)

# %% [markdown]
# ## 4. Deliverable - Part 4
#
# **What fraction of specimens have only one published ECV estimate?** 
# In ecv_hominin, 0.44 (44%) of specimens have only one published ECV estimate. 
# For those specimens, ecv_median_cm3 is not really a median. It is a single measurement, 
# made with one method and one set of assumptions about missing parts of the braincase.
# A median of two estimates is just the average of two values. 
#
#
# **Most Diverse Locality.** 
# The Type Area has the most distinct taxa with 8. All of its fossils come from 
# the Shungura Formation (Omo, Ethiopia). 
#
# Four taxa are present, and have ECV
# - Paranthropus aethiopicus: 442.7 cm3
# - Paranthropus boisei: 487.9 cm3
# - Homo habilis: 633.0 cm3
# - Homo erectus: 918.7 cm3
# Mean ECV across these taxa is 620.6 cm3, with a range of 442.7 to 918.7 cm3.
#
# **What the Diversity Means.** 
# The age span points to a long temporal span. The Type Area combines about
# 2 million years of Omo River deposits under one locality name, and its
# members are stacked in time and dated by tuffs. Most Shungura hominins are also
# isolated teeth collected from the surface of each member, so this could explain all of
# the genus identifications instead of species identification.