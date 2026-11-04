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

# %% [markdown]
# ## 1.8 Deliverables - Part 1
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

# %% [markdown]
# ## 2.6 Deliverable - Part 2
# [2]
# explaining why you might exclude Australopithecus from a study focused on the Turkana Basin — what does
# the geographic distribution of the species in your dataset tell you?
#
# Australopithecus ECVs come from outside the Omo-Turkana Basin:
# Au. afarensis from Hadar, Au. africanus from South African cave sites, and
# Au. garhi from Bouri. The Turkana Australopithecus record (Au. anamensis at
# Kanapoi and Allia Bay) is mostly jaws and teeth, with no measurable
# endocasts. Keeping them would attach brain sizes from other regions to
# Turkana fossils. Paranthropus and Homo are both present and measured in
# the basin.
#
#
# [3]
# **Interpretation.** (Read the bins from Pliocene up to Late Pleistocene,
# since the labels run youngest to oldest.) Mean ECV does increase toward
# the present, but most of that comes from *which taxa* are in each bin:
# older bins are mostly Paranthropus (about 400-550 cm³), and younger bins
# contain only Homo after Paranthropus disappears around 1.4 Ma.
#
# Grouping by grade shows the trend is not the same in each grade:
# * `mega` (Paranthropus) stays fairly flat.
# * `trans` (H. habilis) only appears in one bin and has a wide range
#   (KNM-ER 1813 at ~500 vs KNM-ER 1470 and 1590 at ~750-790).
# * `pre.mod` (Homo erectus and later) increases, but the youngest bin has
#   few specimens.
#
# So the pooled trend mostly reflects one group replacing another, with
# smaller change inside each grade. Cells with only 1-2 specimens should not
# be over-interpreted.

# %% [markdown]
# ## Part 3 - Joining Data

# %% 3.2 Preparing the join
fossils = pd.read_sql("SELECT f.*, t.scientific_name FROM fossils f JOIN taxa t USING (taxon_id)",
    engine
)

fossils['taxon_name'] = fossils['scientific_name'].str.strip()
 
print("OTB taxa:", sorted(fossils['taxon_name'].unique()))
print("ECV taxa:", sorted(ecv_hominin['taxon'].unique()))

# %% Abbreviate genus names in ECV table
ecv_hominin['taxon'] = ecv_hominin['taxon'].str.replace('P. ', 'Paranthropus ', regex=False)
ecv_hominin['taxon'] = ecv_hominin['taxon'].str.replace('H. ', 'Homo ', regex=False)

# %% Change KNM-ER 1470 from H. rudolfensis to H. habilis
ecv_hominin.loc[ecv_hominin['ID'] == 'KNM-ER 1470', 'taxon'] = 'Homo rudolfensis'

# %% Summarize by taxon
ecv_by_taxon = (
    ecv_hominin
    .groupby('taxon')['ecv_median_cm3']
    .agg(ecv_mean='mean', ecv_median='median',
         ecv_min='min', ecv_max='max', ecv_n='count')
    .reset_index()
)
print(ecv_by_taxon)
 
# Left join onto the fossils
fossils_ecv = pd.merge(
    fossils,
    ecv_by_taxon,
    left_on='taxon_name', right_on='taxon',
    how='left'
)
print(fossils.shape)
print(fossils_ecv.shape)
 
print(fossils_ecv[['catalog_number', 'taxon_name', 'ecv_mean']].head(10))

# %%
print(fossils_ecv['ecv_mean'].isnull().sum())
no_ecv = fossils_ecv[fossils_ecv['ecv_mean'].isnull]
print(no_ecv['taxon_nam'].value_counts())

# %% Specimen-level inner join
specimen_join = pd.merge(
    fossils,
    ecv_hominin[['ID', 'ecv_median_cm3', 'age_lo_Ma', 'age_hi_Ma', 'n_estimates']],
    left_on='catalog_number', right_on='ID',
    how='inner'
)
print(f"{len(specimen_join)} OTB fossils matched a published ECV measurement")
print(specimen_join[['catalog_number', 'taxon_name', 'ecv_median_cm3', 'n_estimates']])

# %% Add a time bin to the OTB fossils using stratigraphic ages
fossils_ecv['age_mid_Ma'] = (fossils_ecv['age_min_ma'] + fossils_ecv['age_max_ma']) / 2
fossils_ecv['time_bin'] = pd.cut(fossils_ecv['age_mid_Ma'], bins=bins, labels=labels)
 
pivot = fossils_ecv.pivot_table(
    values='ecv_mean',
    index='taxon_name',
    columns='time_bin',
    aggfunc='mean'
)
print(pivot)

# %% 3.6 [markdown]
# ## Deliverable - Part 3
# **Changes made and why:**
#
# 1. **Abbreviations** ("P. boisei" → "Paranthropus boisei"). This is only a
#    formatting fix; the species is the same.
# 2. **KNM-ER 1470: Homo habilis → Homo rudolfensis**, for that specimen only.
#    I did not rename every "Homo habilis" to "Homo rudolfensis" (or the other
#    way around), because that would merge two species into one. Whether these
#    are separate species is exactly the kind of question species delimitation
#    tries to answer, so the data should not decide it in advance. Changing the
#    one specimen follows the classification already used in my OTB database.
# 3. **Not changed:** OTB taxa with no published endocast (e.g. Kenyanthropus
#    platyops) are left without a match. Making up a value would be wrong.
#
# **Why the row count stays the same.** A left join keeps every row of the
# left table (`fossils`). Because `ecv_by_taxon` has only one row per taxon,
# each fossil matches at most one row, so no fossil gets duplicated. Fossils
# with no match are kept and get `NaN`. Only the number of columns goes up.
# If I had joined the specimen-level ECV table on taxon instead, each fossil
# would match several ECV rows and the row count would multiply.
#
# **Why so few matches.**
# * ECV can only be measured on a fairly complete braincase. Most OTB
#   specimens are teeth, jaws, and postcrania, so only a small number could
#   ever have an ECV.
# * Catalog numbers have to match exactly. "KNM-ER 1470" and "KNM ER 1470"
#   are different strings to pandas.
# * Some ECVs are for reconstructed or composite crania, which the OTB
#   database may catalog as separate pieces.
# * Du et al. only include published ECVs, which favor famous,
#   well-preserved crania.
#
# So the taxon-level ECV for each species comes from a handful of crania but
# is applied to hundreds of OTB specimens.
# 
# # **Interpreting the pivot table.** Because `ecv_mean` was joined by taxon,
# every filled cell in a row has the same value. The table does not show
# brain size changing over time within a species. What it shows is *which
# time bins each species appears in* in the OTB record, labeled with its
# brain size. The useful comparisons are between rows: in the
# Plio-Pleistocene and Early Pleistocene bins, Paranthropus (~450-500 cm³)
# and early Homo (~600-800 cm³) occur at the same time. Taxa with no ECV do
# not show up as rows, and OTB specimens older than 3.5 Ma do not get a bin.
# 

# %% [markdown]
# ## Part 4 - OTB + ECV Analysis
# %% Mean OTB age and ECV for each taxon that has ECV data
has_ecv = fossils_ecv[fossils_ecv['ecv_mean'].notnull()]
taxon_summary = has_ecv.groupby('taxon_name').agg(
    mean_age=('age_mid_Ma', 'mean'),
    ecv_mean=('ecv_mean', 'mean')
).reset_index()
 
# Add the grade back in from the ECV table
grade_by_taxon = ecv_hominin.groupby('taxon')['grade'].first().reset_index()
taxon_summary = pd.merge(taxon_summary, grade_by_taxon,
                         left_on='taxon_name', right_on='taxon', how='left')
print(taxon_summary)
 
# Scatter plot, one color per grade
colors = {'mega': 'red', 'trans': 'green', 'pre.mod': 'blue'}
 
plt.figure(figsize=(8, 6))
for grade in taxon_summary['grade'].unique():
    subset = taxon_summary[taxon_summary['grade'] == grade]
    plt.scatter(subset['mean_age'], subset['ecv_mean'],
                color=colors[grade], label=grade_labels[grade], s=60)
 
# Taxon labels next to each point
for i, row in taxon_summary.iterrows():
    plt.text(row['mean_age'], row['ecv_mean'] + 10, row['taxon_name'], fontsize=8)
 
plt.xlabel('Mean specimen age (Ma)')
plt.ylabel('Mean ECV (cm³)')
plt.gca().invert_xaxis()        # older on the left
plt.legend()
plt.tight_layout()
plt.savefig('ecv_vs_age.png')
plt.show()
 
# %% Histogram of n_estimates
plt.figure(figsize=(6, 4))
plt.hist(ecv_hominin['n_estimates'], bins=[0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5])
plt.xlabel('n_estimates')
plt.ylabel('Number of specimens')
plt.savefig('n_estimates_hist.png')
plt.show()
 
frac_single = (ecv_hominin['n_estimates'] == 1).sum() / len(ecv_hominin)
print(f"Fraction with only one estimate: {frac_single:.2f}")

# %% Locality with the most distinct taxa
diversity = fossils_ecv.groupby('locality')['taxon_name'].nunique().sort_values(ascending=False)
print(diversity.head())
 
top_locality = diversity.index[0]
print("Most diverse locality:", top_locality)
 
at_locality = fossils_ecv[fossils_ecv['locality'] == top_locality]
locality_taxa = at_locality.groupby('taxon_name')['ecv_mean'].mean()
print(locality_taxa)
 
print("Mean ECV across taxa:", locality_taxa.mean())
print("Range:", locality_taxa.min(), "to", locality_taxa.max())
print("Age span:", at_locality['age_mid_Ma'].min(), "to", at_locality['age_mid_Ma'].max())

# %% [markdown]
# ## 4. Deliverable - Part 4
#
#  **Reliability.** (Use the printed fraction; in the 20-specimen OTB subset
# it is 10 of 20, or 0.50.) For specimens with only one published estimate,
# `ecv_median_cm3` is not really a median. It is one researcher's
# measurement, with that study's method and assumptions and no way to see
# how much other studies would disagree. A median of two is just the average
# of two values. Only specimens with 3 or more estimates give a stable
# summary. Small differences between taxa should be treated carefully when
# they depend on single-estimate specimens (e.g. KNM-WT 15000 at 909 cm³
# has n_estimates = 1).
# 
# 
#  **What the diversity means.** A locality with many taxa can mean two
# different things, and the age span printed above helps tell them apart:
#
# * **Long time span.** If the specimen ages spread over hundreds of
#   thousands of years, the locality is probably combining many layers of
#   sediment under one name. The taxa may never have lived at the same time.
# * **True coexistence.** If the ages cluster tightly (for example around the
#   KBS Tuff, ~1.87 Ma), several hominin species shared the same landscape.
#   This is the well-known Turkana pattern of P. boisei, early Homo, and
#   H. erectus overlapping between about 1.9 and 1.5 Ma.
#
# The ECV range across these taxa (Paranthropus ~450-500 vs Homo ~600-900)
# shows that if they did live together, they had very different brain
# sizes, which fits with them using different resources. Large river and
# delta deposits also collect fossils from a wide area, which can raise the
# number of taxa found at one locality.