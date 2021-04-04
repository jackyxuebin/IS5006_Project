"""
All configurations shall be put here
"""

from pathlib import Path
import pandas as pd
import datetime
import os

#pd.options.display.max_rows = 10
#pd.options.display.max_columns = 10

## Paths 
BASE_PATH = Path(__file__).parents[1]
DB_PATH = os.path.join(BASE_PATH, "local_db")
DATA_PATH = os.path.join(DB_PATH, "data")
MODEL_PATH = os.path.join(BASE_PATH, "model")

# training and testing data
TRAINING_DATA_FILE = DATA_PATH + "/bitcoin_train_dataset_2014_2021.csv"
TESTING_DATA_FILE = DATA_PATH + "/bitcoin_test_dataset_2009_2020.csv"

# model 
# now = datetime.datetime.now()
# TRAINED_MODEL_DIR = f"{MODEL_PATH}/{now}"
# os.makedirs(TRAINED_MODEL_DIR)

