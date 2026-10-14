# Stage 5 — Read the dataset using Python


# import pandas as pd

# df = pd.read_csv("ai4i2020.csv")

# print("DATASET LOADED SUCCESSFULLY")
# print("Number of rows:", df.shape[0])
# print("Number of columns:", df.shape[1])

# print("\nFIRST 5 RECORDS")
# print(df.head())

# print("\nCOLUMN NAMES")
# print(df.columns.tolist())


# =====================================

# Stage 6 — Check the quality of the data

import pandas as pd

df = pd.read_csv("ai4i2020.csv")

print("DATA QUALITY REPORT")

print("\nMissing values in each column:")
print(df.isnull().sum())

print("\nDuplicate rows:", df.duplicated().sum())

print("\nMachine failure counts:")
print(df["Machine failure"].value_counts())

print("\nDataset information:")
print(df.info())