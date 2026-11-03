# %% [markdown]
# #Part 1 - Position and Python Basics

# %% Setup
import numpy as np
import pandas as pd

print(np.__version__, pd.__version__)

# %% [markdown] 
# ## Part 1.4 Python language features used throughout NumPy and pandas
# In this code, I attempt to demonstrate each of the five language features we went over in class using 
# the 'state_province' and 'formation' information from the otb_fossil.csv.

# %% Part 1 - Languages Code

# using list comprehension
formations = ['Kanapoi', 'Koobi Fora', 'Nachukui', 'Nawata', 'Shungura', 'Usno']
provinces = ['South Ethiopia', 'Marsabit', 'Turkana']
 
formation_labels = [f"{f} Fm." for f in formations]
kenyan_provinces = [p for p in provinces if p != 'South Ethiopia']
print(formation_labels)
print(kenyan_provinces)
 
# using dictionary comprehension
formation_province = {'Kanapoi': 'Turkana', 'Koobi Fora': 'Marsabit', 'Nachukui': 'Turkana',
                      'Nawata': 'Turkana', 'Shungura': 'South Ethiopia', 'Usno': 'South Ethiopia'}
 
formation_ages = {'Kanapoi': (4.20, 4.12), 'Koobi Fora': (4.30, 1.42), 'Nachukui': (5.00, 0.75),
                  'Nawata': (6.50, 6.50), 'Shungura': (3.50, 1.35), 'Usno': (3.21, 3.05)} #oldest and youngest ages
 
turkana_formations = {f: p for f, p in formation_province.items() if p == 'Turkana'}
age_span = {f: round(oldest - youngest, 2) for f, (oldest, youngest) in formation_ages.items()}
print(turkana_formations)
print(age_span)

# using enumerate and zip
province_counts = [580, 291, 372] #number of specimens per province
 
for province, n in zip(provinces, province_counts):
    print(f"{province}: {n} specimens")
 
for rank, formation in enumerate(sorted(formations), start=1):
    print(rank, formation, '->', formation_province[formation])
 
# using *args and **kwargs
def describe_province(province, *formation_names, **details):
    """One province, any number of formations, any extra details."""
    print(f"{province}: {', '.join(formation_names)}")
    for key, value in details.items():
        print(f"    {key} = {value}")
 
describe_province('Turkana', 'Kanapoi', 'Nachukui', 'Nawata', country='Kenya', n_specimens=372)
describe_province('South Ethiopia', 'Shungura', 'Usno', 'Koobi Fora', country='Ethiopia')

# using lambda functions
oldest_first = sorted(formation_ages, key=lambda f: formation_ages[f][0], reverse=True) #order formations from oldest to youngest
biggest = max(zip(provinces, province_counts), key=lambda pair: pair[1]) #province with the most specimens
print(oldest_first)
print(biggest)

#  %% [markdown]
# ## 1.5 Deliverables - Part 1
# What is a virtual environment and why do we need it?
#
# A virtual environment is a separate project directory with its own python interpreter and requirements. 
# A virtual environment is needed because what is coded here is separate from the overall project, 
# so nothing globally will be changed.


# %% [markdown]
# ## Part 2 — NumPy
 
# %% Part 2 — Code
# 2.1 1-D array of stratigraphic ages
ages = np.array([4.17, 3.97, 3.44, 3.30, 2.95, 2.71, 2.52, 2.33, 2.05, 1.88, 1.61, 1.53])
print(ages.dtype)
print(ages.shape)
print(ages.ndim)

# 2.2 vectorized arithmetic
ages_ka = ages * 1000 #Ma -> ka
print(ages_ka)
 
# 2-D array
# 6 specimens × 3 measurements (corpus height, corpus breadth, M1 length) [used characters from project]
measurements = np.array([
    [32.1, 20.4, 13.2],
    [28.7, 18.9, 12.6],
    [36.5, 24.1, 14.8],
    [41.2, 26.8, 16.1],
    [27.9, 17.6, 12.1],
    [30.3, 19.5, 12.9],
])
print(measurements.shape)
print(measurements[3, :])      
print(measurements[:, 2])      

# 2.4 Axis operations 
col_means = measurements.mean(axis=0) #mean of each measurement
row_stds = measurements.std(axis=1) #spread of measurements within each specimen
print(col_means)
print(row_stds)

 
# 2.3 Boolean and fancy indexing
window = ages[(ages > 1.9) & (ages < 2.6)]
print(window)
 
idx = np.array([0, 5, 7])
print(ages[idx])
 
edges = ages[(ages >= 2.58) | (ages < 1.7)]
print(edges)
 
# %% [markdown]
# ### Why NumPy vs. Python loops
# 
# NumPy operations are faster than Python loops because Python for loops handle each element separately as there own independent objects
# and NumPy compiles same type data together and runs on the combined data all at once. A for loop is needed when steps in a code depend
# on each other. For instance, with MorphoDelim, I need to use a Python for loop during my two delimitation protocols (sequential and simultaneous) 
# as the simulations need to run randomly. A vectorized operation would force values to my simulation.
 
# %% [markdown]
# ## Part 3 — pandas
 
# %% Part 3 - Code
# 3.1 Series
specimen_counts = pd.Series(
    [143, 61, 228, 37, 95, 172],
    index=['Lomekwi', 'Kaitio', 'Ileret', 'Kangatukuseo', 'Allia Bay', 'Shungura'],
)
print(specimen_counts['Ileret']) #labels     
print(specimen_counts.iloc[2])     
print(specimen_counts[specimen_counts > 100]) #boolean filter
 
# 3.2 — DataFrame
specimens = pd.DataFrame({
    'specimen_id': ['01', '02', '03', '04', '05',
                    '06', '07', '08', '09', '10'],
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
 
# 3.4 - Indexing ().loc and .iloc)
print(specimens.loc[specimens['locality'] == 'Ileret', ['specimen_id', 'taxon', 'age_ma']])
print(specimens.iloc[2:5, 0:3])
 
# 3.5 - Derived columns
specimens['age_ka'] = specimens['age_ma'] * 1000
specimens['epoch'] = specimens['age_ma'].apply(lambda x: 'Pleistocene' if x < 2.58 else 'Pliocene')
specimens['identified'] = specimens['taxon'].notnull()
print(specimens.head())
 
# 3.6 - Sorting and grouping
specimens = specimens.sort_values('age_ma', ascending=False)
print(specimens)
 
print(specimens['taxon'].value_counts())
 
by_locality = specimens.groupby('locality')['age_ma'].agg(['mean', 'min', 'max', 'count'])
print(by_locality)
 
# %% [markdown]
# ## Summary
#
# The Allia Bay locality has the oldest mean age of 3.7 Ma, the remaining localities means are 2.5 Ma or less. 
# Ileret and Kaito have the most number of specimens (n=3) while Lomekwi and Shungura have the least (n=1).  
 
# %% [markdown]
# ## Part 4 — OTB analysis
 
# %% Part 4 — load the data
# Used the first option and ran it in my own terminal
#
# psql -d informatics -c "\COPY ( \
#    SELECT f.catalog_number, f.organism_id, f.preparations, t.scientific_name, \
#           l.place, l.locality, l.country, \
#           f.earliest_chronometric_age, f.latest_chronometric_age, f.verbatim_chronometric_age \
#    FROM fossils f \
#    JOIN taxa t USING (taxon_id) \
#    JOIN localities l USING (locality_id) \
#    ORDER BY f.catalog_number \
#  ) TO 'otb_export.csv' CSV HEADER"

df = pd.read_csv('otb_export.csv') #load in data from psql 

# %% Inspect that the data loaded correctly
print(df.shape)
print(df.dtypes)
print(df.isnull().sum())
print(df.describe())
 
# %% Part 4 — quality checks
print(df.loc[df['earliest_chronometric_age'] < df['latest_chronometric_age'], 'catalog_number'])
 
# Specimens whose ages were recorded only as bounds (">3.97", "< 4.07±0.02") have no numeric age
print(df.loc[df['earliest_chronometric_age'].isnull(), 'verbatim_chronometric_age'].value_counts(dropna=False))
 
# %% Part 4 — derived columns
df['avg_age'] = df[['earliest_chronometric_age', 'latest_chronometric_age']].mean(axis=1)
df['taxon_short'] = df['scientific_name'].str.split().str[0]    # genus only
 
# %% Q1 — How many specimens belong to each taxon?
print(df['scientific_name'].value_counts())

 
# %% [markdown]
# ## **Q1.** How many specimens belong to each taxon?
#
# | scientific_name                                     | count  |
# |-----------------------------------------------------|--------|
# | Hominini                                            |    335 |
# | Australopithecus anamensis Leakey et al., 1995      |    242 |
# | Paranthropus boisei (Leakey, 1959)                  |    205 |
# | Homo erectus (Dubois, 1892)                         |    154 |
# | Homo habilis Leakey, Tobias & Napier, 1964          |    100 |
# | Homo Linnaeus, 1758                                 |     91 |
# | Paranthropus aethiopicus (Arambourg & Coppens, 1967)|     66 |
# | Australopithecus Dart, 1925                         |     28 |
# | Paranthropus Broom, 1938                            |     20 |
# | Kenyanthropus platyops Leakey et al., 2001          |      2 |

# %% Q2 — What is the mean, minimum, and maximum chronometric age for each locality?
by_place = df.groupby('place')['avg_age'].agg(['mean', 'min', 'max', 'count'])
print(by_place.sort_values('mean', ascending=False))

# %% [markdown]
# ## **Q2.** What is the mean, minimum, and maximum chronometric age for each locality?

# | place     |      mean    | min   | max    | count |
# |---------------|----------|-------|--------|-------|          
# | Lothagam      | 4.300000 | 3.500 | 5.7500 |     7 |
# | Kanapoi       | 4.124645 | 4.095 | 4.1515 |   179 |
# | Allia Bay     | 3.739362 | 2.700 | 4.1000 |    47 |
# | South Turkwel | 3.390000 | 3.390 | 3.3900 |    12 |
# | Fejej         | 3.245455 | 1.925 | 4.0000 |    11 |
# | White Sands   | 3.200000 | 3.200 | 3.2000 |    11 |
# | Brown Sands   | 3.050000 | 3.050 | 3.0500 |    11 |
# | Type Area     | 2.360996 | 1.450 | 3.4300 |   251 |
# | Nachukui      | 2.214202 | 0.750 | 3.5300 |   163 |
# | Koobi Fora    | 1.850887 | 1.420 | 3.4000 |   293 |
# | Kalam Area    | 1.847500 | 1.350 | 2.3050 |     6 |
# | Ileret        | 1.645223 | 1.400 | 4.3000 |   224 |
 
# %% Q3 — Which skeletal element is most commonly recovered?
print(df['preparations'].value_counts())

# %% [markdown]
# ## **Q3.** Which skeletal element is most commonly recovered?
# 
# | skeletal element  | count |
# |-------------------|-------|
# | Tooth             | 688   | 
# | Postcranium       | 260   | 
# | Cranium           | 176   | 
# | Mandible          | 119   |

# Teeth (n=688) are the most commonly recovered skeletal element. 
 
# %% Q4 — Are there any localities where all specimens share the same taxon?
taxa_per_place = df.groupby('place')['scientific_name'].nunique()
print(taxa_per_place[taxa_per_place == 1])
print(df.groupby('place').size()[taxa_per_place == 1])    # how many specimens at each
 
# %% [markdown]
# ## **Q4.** Are there any localities where all specimens share the same taxon?
#
# A. anamensis specimens come from Kanapoi. 
 
# %% Part 4 — NumPy on earliest_chronometric_age
ages = df['earliest_chronometric_age'].to_numpy()
ages = ages[~np.isnan(ages)] #get rid of missing ages
 
mean = ages.mean()
sd = ages.std()
within = ages[(ages > mean - sd) & (ages < mean + sd)]
proportion = len(within) / len(ages)
 
print(mean)
print(sd)
print(proportion)
 
# %% [markdown]
# Mean = 2.4852962962962963
# Standard deviation = 0.9741868164581002
# Proportion + 0.7135802469135802
 
# %% Part 4 — Add epoch column
df['epoch'] = df['avg_age'].apply(lambda x: None if pd.isnull(x) else ('Pleistocene' if x < 2.58 else 'Pliocene')) #keep missing data as missing
print(df['epoch'].value_counts(dropna=False))
 
# %% Part 4 — taxon composition by epoch
print(df.groupby('epoch')['scientific_name'].value_counts().unstack(fill_value=0).T) 
print(df.groupby('epoch')['taxon_short'].value_counts(normalize=True).unstack(fill_value=0).T)
 
# %% [markdown]
# ## Epoch comparison
#                                              
# | scientific_name                               |                       epoch |                                       
# |-----------------------------------------------|-----------------------------|                                                         
# |-----------------------------------------------|        Pleistocene  Pliocene|                                                   
# | Australopithecus Dart, 1925                   |                0        28  |
# | Australopithecus anamensis Leakey et al., 1995|                0       226  |
# | Hominini                                      |              209       124  |
# | Homo Linnaeus, 1758                           |               83         0  |
# | Homo erectus (Dubois, 1892)                   |              153         0  |
# | Homo habilis Leakey, Tobias & Napier, 1964    |              100         0  |
# | Kenyanthropus platyops Leakey et al., 2001    |                0         2  |
# | Paranthropus Broom, 1938                      |               20         0  |
# | Paranthropus aethiopicus (Arambourg & Coppens |               63         3  |
# | Paranthropus boisei (Leakey, 1959)            |              204         0  |
#
#
# |------------------|------------------------|
# | taxon_short      |        epoch           |
# |------------------|------------------------|
# |------------------|  Pleistocene Pliocene  |
# | Australopithecus |    0.000000  0.663185  |
# | Hominini         |    0.251202  0.323760  |
# | Homo             |    0.403846  0.000000  |
# | Kenyanthropus    |    0.000000  0.005222  |
# | Paranthropus     |    0.344952  0.007833  |

# The Pleistocene has 832 specimens, while the Pliocene has 383 specimens. 
# Australopithecus and Kenyanthropus are the only taxa that appear in the Pliocene only.
# Homo appears in the Pleistocene only. Paranthropus and Hominini span both epochs. 