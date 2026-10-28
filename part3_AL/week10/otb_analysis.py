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
# # Part 2 - Numpy
# ## Part 2.1 The ndarray

# %%
import numpy as np

age_ma_list = (1.55, 2.32, 3.21, 3.3, 4.5, 3.89, 1.87)
ages = np.array([1.87, 2.35, 1.65, 2.10, 1.92, 2.44, 1.73])
print(ages.dtype)    # float64
print(ages.shape)    # (7,)
print(ages.ndim)     # 1

# 2 - D array
# 3 specimens × 4 measurements (length, width, height, mass)
measurements = np.array(
    [
        [45.2, 12.1, 8.3, 0.14],
        [38.7, 10.5, 7.1, 0.09],
        [51.0, 14.2, 9.6, 0.21],
    ]
)

print(measurements.shape)   # (3, 4)
print(measurements[0, :])   # first specimen, all measurements
print(measurements[:, 2])   # all specimens, height only

# %% [markdown]
# ## Part 2.2 Vectorized arithematic

# %% Vectorized arithematic
ages_bp = ages * 1_000_000
log_ages = np.log(ages)
z_scores = (ages - ages.mean()) / ages.std()

# %% [markdown]
# ## Part 2.3 Boolean indexing and fancy indexing

# %% Boolean indexing
old = ages[ages > 2.0]          # specimens older than 2 Ma
print(old)                      # array of selected values

# Compound conditions require & and |, not 'and' / 'or'
window = ages[(ages > 1.8) & (ages < 2.2)]

# %% [markdown]
# ## Part 2.4 - Axis operations

# %% Axis operations
# Column means (mean of each measurement across all specimens)
col_means = measurements.mean(axis=0)   # shape (4,)

# Row means (mean measurement per specimen)
row_means = measurements.mean(axis=1)   # shape (3,)

# %% [markdown]
# ## Part 3 - pandas

# %% Part 3.1 Series
import pandas as pd

specimen_counts = pd.Series(
    [312, 187, 244, 98, 402],
    index=['FLK', 'KBS', 'Natron', 'Chesowanja', 'Turkana'],
)
print(specimen_counts['KBS'])          # 187  — label-based access
print(specimen_counts[2])              # 244  — integer position
print(specimen_counts[specimen_counts > 200])   # boolean filter

counts_2022 = pd.Series({'FLK': 312, 'KBS': 187, 'Natron': 244})
counts_2023 = pd.Series({'FLK': 19,  'KBS': 41,  'Natron': 8})
total = counts_2022 + counts_2023    # aligns on locality name

# %% Part 3.2 DataFrame
specimens = pd.DataFrame({
    'specimen_id': ['OTB-001', 'OTB-002', 'OTB-003', 'OTB-004'],
    'taxon':       ['Australopithecus', 'Paranthropus', 'Homo', 'Australopithecus'],
    'locality':    ['FLK', 'KBS', 'FLK', 'Natron'],
    'age_ma':      [1.87, 2.35, 1.65, 2.10],
    'element':     ['femur', 'mandible', 'cranium', 'tibia'],
})

#df = pd.read_csv('otb_specimens.csv')

from sqlalchemy import create_engine
from config import DSN

engine = create_engine(DSN)
df = pd.read_sql('SELECT * FROM specimens JOIN taxa USING (taxon_id)', engine)