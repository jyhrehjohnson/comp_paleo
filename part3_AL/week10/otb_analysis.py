# %% [markdown]
# #Part 1 - Position and Python Basics
# ## In Part 1, I attempt to demonstrate each of the five language features we went over in class using the 'state_province' and 'formation' information from the otb_fossil.csv

# %% Setup
import numpy as np
import pandas as pd

print(np.__version__, pd.__version__)

# %% [markdown] 
# # Part 1.4 Python language features used throughout NumPy and pandas

# %% Part 1 - list comprehension
formations = ['Kanapoi', 'Koobi Fora', 'Nachukui', 'Nawata', 'Shungura', 'Usno']
provinces = ['South Ethiopia', 'Marsabit', 'Turkana']
 
formation_labels = [f"{f} Fm." for f in formations]
kenyan_provinces = [p for p in provinces if p != 'South Ethiopia']
print(formation_labels)
print(kenyan_provinces)
 
# %% Part 1 — dictionary comprehension
formation_province = {'Kanapoi': 'Turkana', 'Koobi Fora': 'Marsabit', 'Nachukui': 'Turkana',
                      'Nawata': 'Turkana', 'Shungura': 'South Ethiopia', 'Usno': 'South Ethiopia'}
 
# Oldest and youngest earliest_chronometric_age per formation in this dataset (Ma)
formation_ages = {'Kanapoi': (4.20, 4.12), 'Koobi Fora': (4.30, 1.42), 'Nachukui': (5.00, 0.75),
                  'Nawata': (6.50, 6.50), 'Shungura': (3.50, 1.35), 'Usno': (3.21, 3.05)}
 
turkana_formations = {f: p for f, p in formation_province.items() if p == 'Turkana'}
age_span = {f: round(oldest - youngest, 2) for f, (oldest, youngest) in formation_ages.items()}
print(turkana_formations)
print(age_span)

# %% Part 1 — enumerate and zip
province_counts = [580, 291, 372]       #specimens per province
 
for province, n in zip(provinces, province_counts):
    print(f"{province}: {n} specimens")
 
for rank, formation in enumerate(sorted(formations), start=1):
    print(rank, formation, '->', formation_province[formation])
 
# %% Part 1 — *args and **kwargs
def describe_province(province, *formation_names, **details):
    """One province, any number of formations, any extra details."""
    print(f"{province}: {', '.join(formation_names)}")
    for key, value in details.items():
        print(f"    {key} = {value}")
 
describe_province('Turkana', 'Kanapoi', 'Nachukui', 'Nawata', country='Kenya', n_specimens=372)
describe_province('South Ethiopia', 'Shungura', 'Usno', 'Koobi Fora', country='Ethiopia')

# %% Part 1 — lambda
# Formations ordered from oldest to youngest specimen age
oldest_first = sorted(formation_ages, key=lambda f: formation_ages[f][0], reverse=True)
# Province with the most specimens
biggest = max(zip(provinces, province_counts), key=lambda pair: pair[1])
print(oldest_first)
print(biggest)

#  %% [markdown]
# ## 1.5 Deliverables - Part 1
# What is a virtual environment and why do we need it?
#
# A virtual environment is a separate project directory with its own python interpreter and requirements. 
# A virtual environment is needed because what is coded here is separate from the overall project, so nothing globally will be changed.


# %% [markdown]
# ## Part 2 — NumPy
 
# %% Part 2 — 1-D array of stratigraphic ages
ages = np.array([4.17, 3.97, 3.44, 3.30, 2.95, 2.71, 2.52, 2.33, 2.05, 1.88, 1.61, 1.53])
print(ages.dtype)
print(ages.shape)
print(ages.ndim)
 
ages_ka = ages * 1000          # Ma -> ka
print(ages_ka)
 
# %% Part 2 — 2-D array
# 6 specimens × 3 measurements (corpus height, corpus breadth, M1 length; all mm)
measurements = np.array([
    [32.1, 20.4, 13.2],
    [28.7, 18.9, 12.6],
    [36.5, 24.1, 14.8],
    [41.2, 26.8, 16.1],
    [27.9, 17.6, 12.1],
    [30.3, 19.5, 12.9],
])
print(measurements.shape)
print(measurements[3, :])      # fourth specimen, all measurements
print(measurements[:, 2])      # all specimens, M1 length only
 
col_means = measurements.mean(axis=0)   # mean of each measurement
row_stds = measurements.std(axis=1)     # spread of measurements within each specimen
print(col_means)
print(row_stds)
 
# %% Part 2 — boolean and fancy indexing
window = ages[(ages > 1.9) & (ages < 2.6)]      # specimens between 1.9 and 2.6 Ma
print(window)
 
idx = np.array([0, 5, 11])
print(ages[idx])                                # ages at positions 0, 5, 11
 
edges = ages[(ages >= 2.58) | (ages < 1.7)]     # Pliocene OR younger than 1.7 Ma
print(edges)
 
# %% [markdown]
# ### Why NumPy beats Python loops
# TODO (your own words, 3–5 sentences). Points to cover:
# - one dtype + contiguous memory → the loop runs in compiled C, with no per-element type checks
# - a Python `for` loop handles each element as a separate Python object
# - when a loop really is needed: each step depends on the previous result (e.g. a sequential
#   simulation), complex branching per item, or work on non-numeric Python objects
 
# %% [markdown]
# ## Part 3 — pandas
 
# %% Part 3 — Series
specimen_counts = pd.Series(
    [143, 61, 228, 37, 95, 172],
    index=['Lomekwi', 'Kaitio', 'Ileret', 'Kangatukuseo', 'Allia Bay', 'Shungura'],
)
print(specimen_counts['Ileret'])                    # label-based access
print(specimen_counts.iloc[2])                      # integer position (specimen_counts[2] raises KeyError in pandas 3)
print(specimen_counts[specimen_counts > 100])       # boolean filter
 
# %% Part 3 — DataFrame
specimens = pd.DataFrame({
    'specimen_id': ['DEMO-01', 'DEMO-02', 'DEMO-03', 'DEMO-04', 'DEMO-05',
                    'DEMO-06', 'DEMO-07', 'DEMO-08', 'DEMO-09', 'DEMO-10'],
    'taxon':       ['Paranthropus', 'Homo', 'Australopithecus', 'Paranthropus', 'Homo',
                    'Australopithecus', 'Homo', 'Paranthropus', None, 'Homo'],
    'locality':    ['Ileret', 'Kaitio', 'Allia Bay', 'Shungura', 'Ileret',
                    'Allia Bay', 'Ileret', 'Lomekwi', 'Kaitio', 'Kaitio'],
    'age_ma':      [1.72, 1.55, 3.45, 2.15, 1.86, 3.95, 1.49, 2.52, 1.70, 1.62],
    'element':     ['mandible', 'femur', 'molar', 'cranium', 'molar',
                    'tibia', 'mandible', 'cranium', 'molar', 'pelvis'],
})
specimens.info()
print(specimens.describe())
 
# %% Part 3 — .loc and .iloc
print(specimens.loc[specimens['locality'] == 'Ileret', ['specimen_id', 'taxon', 'age_ma']])
print(specimens.iloc[2:5, 0:3])
 
# %% Part 3 — derived columns
specimens['age_ka'] = specimens['age_ma'] * 1000
specimens['epoch'] = specimens['age_ma'].apply(lambda x: 'Pleistocene' if x < 2.58 else 'Pliocene')
specimens['identified'] = specimens['taxon'].notnull()
print(specimens.head())
 
# %% Part 3 — sorting and grouping
specimens = specimens.sort_values('age_ma', ascending=False)
print(specimens)
 
print(specimens['taxon'].value_counts())
 
by_locality = specimens.groupby('locality')['age_ma'].agg(['mean', 'min', 'max', 'count'])
print(by_locality)
 
# %% [markdown]
# ### What the summary shows
# TODO (2–3 sentences, based on the output above). Things to look at: which localities give the
# oldest mean ages, which have a wide age range, and that the unidentified specimen
# drops out of `value_counts()`.
 
# %% [markdown]
# ## Part 4 — OTB analysis
 
# %% Part 4 — load
# From the database (preferred, once the view matches this file's columns):
# from sqlalchemy import create_engine
# from config import DSN       # never hardcode credentials
# engine = create_engine(DSN)
# df = pd.read_sql('SELECT * FROM otb_fossils_export', engine)
 
df = pd.read_csv('otb_fossils.tsv', sep='\t')
 
# %% Part 4 — inspect
print(df.shape)
print(df.dtypes)
print(df.isnull().sum())
print(df.describe())
 
# %% [markdown]
# ### First look — anything unexpected?
# TODO, based on the output above (and the next cell). Things to check:
# - Which columns have missing values, and how many specimens have no numeric age?
# - Is the earliest age ever younger than the latest?
# - Do the min/max ages fall in a plausible range? (Check the Lothagam specimens at the old end.)
 
# %% Part 4 — quality checks
print(df.loc[df['earliest_chronometric_age'] < df['latest_chronometric_age'], 'catalog_number'])
 
# Specimens whose ages were recorded only as bounds (">3.97", "< 4.07±0.02") have no numeric age
print(df.loc[df['earliest_chronometric_age'].isnull(), 'verbatim_chronometric_age'].value_counts(dropna=False))
 
# %% Part 4 — derived columns
df['avg_age'] = df[['earliest_chronometric_age', 'latest_chronometric_age']].mean(axis=1)
df['taxon_short'] = df['scientific_name'].str.split().str[0]    # genus only
 
# %% Q1 — How many specimens belong to each taxon?
print(df['scientific_name'].value_counts())
 
# Catalogued parts vs. distinct individuals (one organism_id can have several parts: a, b, c…)
print(df.groupby('scientific_name')['organism_id'].nunique().sort_values(ascending=False))
 
# %% [markdown]
# **Q1.** TODO: one sentence (most common taxon; how many are only "Hominini";
# how much multi-part specimens inflate the counts — compare the two outputs).
 
# %% Q2 — mean, minimum, and maximum chronometric age for each locality
by_place = df.groupby('place')['avg_age'].agg(['mean', 'min', 'max', 'count'])
print(by_place.sort_values('mean', ascending=False))
 
# %% [markdown]
# **Q2.** TODO: one sentence (oldest/youngest places; any with a suspiciously wide range).
 
# %% Q3 — Which skeletal element is most commonly recovered?
print(df['preparations'].value_counts())
 
# %% [markdown]
# **Q3.** TODO: one sentence (and whether it fits the usual taphonomic bias toward teeth and jaws).
 
# %% Q4 — Are there any localities where all specimens share the same taxon?
taxa_per_place = df.groupby('place')['scientific_name'].nunique()
print(taxa_per_place[taxa_per_place == 1])
print(df.groupby('place').size()[taxa_per_place == 1])    # how many specimens at each
 
# %% [markdown]
# **Q4.** TODO: one sentence. Check which taxon each one is — a place can be "single-taxon"
# because everything there is indeterminate "Hominini".
 
# %% Part 4 — NumPy on earliest_chronometric_age
ages = df['earliest_chronometric_age'].to_numpy()
ages = ages[~np.isnan(ages)]                  # drop missing ages
 
mean = ages.mean()
sd = ages.std()
within = ages[(ages > mean - sd) & (ages < mean + sd)]
proportion = len(within) / len(ages)
 
print(mean)
print(sd)
print(proportion)
 
# %% [markdown]
# For a normal distribution, ~0.68 would fall within 1 SD. TODO: say whether your value is
# higher or lower, and what that suggests about the age distribution (clustered vs. spread out
# or bimodal).
 
# %% Part 4 — epoch
# Missing ages stay missing rather than being labelled 'Pliocene' by the else branch
df['epoch'] = df['avg_age'].apply(lambda x: None if pd.isnull(x) else ('Pleistocene' if x < 2.58 else 'Pliocene'))
print(df['epoch'].value_counts(dropna=False))
 
# %% Part 4 — taxon composition by epoch
print(df.groupby('epoch')['scientific_name'].value_counts().unstack(fill_value=0).T)
print(df.groupby('epoch')['taxon_short'].value_counts(normalize=True).unstack(fill_value=0).T)
 
# %% [markdown]
# ### Epoch comparison
# TODO (3–4 sentences): which taxa/genera are confined to one epoch, which cross the boundary,
# how the sample sizes differ, and one caveat (e.g. specimens with wide age ranges straddling
# 2.58 Ma get classified only by their midpoint).