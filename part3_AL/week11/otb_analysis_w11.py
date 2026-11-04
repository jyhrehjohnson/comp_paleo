# %% [markdown]
# week11

# %% Setup
import json

import pandas as pd

# %% Checks
file_path = os.path.join(path, 'ecv_otb_subset.json')
with open('ecv_otb_subset.json') as f:
    ecv_raw = json.load(f)

print(type(ecv_raw))                    # dict
print(ecv_raw['source'])                # citation string
print(ecv_raw['region'])
print(len(ecv_raw['specimens']))        # 20 specimens
print(ecv_raw['specimens'][0])          # first record as a dict