# %% Imports
import json
import os

import pandas as pd
from plotnine import *
from sqlalchemy import create_engine

from config import DSN

# %% Load data
engine = create_engine(DSN)

fossils = pd.read_sql(
    """
    SELECT f.*, t.scientific_name, l.*
    FROM fossils f
    JOIN taxa t USING (taxon_id)
    JOIN localities l USING (locality_id)
    """,
    engine
)

# set the path to the week 11 folder so the file can be located.
path = os.path.join("part3_AL/week11/ecv_by_specimen.csv")
ecv_full = pd.read_csv(path)

# Grade is a ordered categorical variable. 
# We need to set the ordering or else it will default
# to alphabetical. 
grade_order = ['archaic', 'mega', 'trans', 'pre.mod']
ecv_full['grade'] = pd.Categorical(ecv_full['grade'],
	categories=grade_order,
	ordered=True)