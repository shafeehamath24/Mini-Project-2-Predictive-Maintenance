# Stage 10 — Fix the dataset paths

import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

df = pd.read_csv(BASE_DIR / "ai4i2020.csv")

print("DATA ENGINEERING STARTED")

df = df.drop(columns=["UDI", "Product ID"])

df["Type"] = df["Type"].map({
    "L": 0,
    "M": 1,
    "H": 2
})

df = df.dropna()

df.to_csv(BASE_DIR / "processed_machine_data.csv", index=False)

print("Original records: 10000")
print("Processed records:", len(df))
print("Processed columns:", len(df.columns))
print("Missing values after processing:", df.isnull().sum().sum())
print("Saved: processed_machine_data.csv")






# =====================================




# Stage 7 — Prepare the data for the project

# import pandas as pd

# df = pd.read_csv("ai4i2020.csv")

# print("DATA ENGINEERING STARTED")

# df = df.drop(columns=["UDI", "Product ID"])

# df["Type"] = df["Type"].map({
#     "L": 0,
#     "M": 1,
#     "H": 2
# })

# df = df.dropna()

# df.to_csv("processed_machine_data.csv", index=False)

# print("Original records:", 10000)
# print("Processed records:", len(df))
# print("Processed columns:", len(df.columns))
# print("Missing values after processing:", df.isnull().sum().sum())
# print("Saved: processed_machine_data.csv")








