from openpyxl import load_workbook
import pandas as pd
import numpy as np
import calendar

# For local testing purposes; in production we should error out in this case
delete_empty_rows = True

file = "data-trimmed.xlsx"
file = "data.xlsx"
df = pd.read_excel(file)

error = None

# Month names in French are used in the spreadsheet so we convert to month numbers
months = {
    "janvier": 1,
    "février": 2,
    "mars": 3,
    "avril": 4,
    "mai": 5,
    "juin": 6,
    "juillet": 7,
    "août": 8,
    "septembre": 9,
    "octobre": 10,
    "novembre": 11,
    "décembre": 12,
}

# We only keep the relevant columns...
columns_to_keep = ["année", "mois calcul volume", "PN_PRLVT_ECHANGES", "num_compteur", "volume retenu calendaire"]
df = df[columns_to_keep]

col_names = {
    "mois calcul volume": "month", 
    "année": "year",
    "PN_PRLVT_ECHANGES": "type",
    "num_compteur": "meter_number",
    "volume retenu calendaire": "quantity",
}

# Rename to English and single words
df.rename(columns = col_names, inplace = True)

# We will add the period name by stating "month name month year" as a string
df["period_name"] = df["month"].astype(str) + " " + df["year"].astype(str) 

# Convert the month names to numbers
df["month"] = df["month"].replace(months)

# Now we can create start date YYYY-MM-01, which we then convert into a datetime object
df["start_date"] = df["year"].astype(str) + "-" + df["month"].astype(str) + "-01"
df["start_date"] = pd.to_datetime(df["start_date"])

# And we use this to set the end date to the last day of that month
df["end_date"] = df["start_date"] + pd.offsets.MonthEnd()

# We no longer need month/year columns so let's drop them...
df = df.drop(["month", "year"], axis=1)

# Check if any of the columns that are important contain empty cells...
if df["start_date"].isnull().sum() or df["end_date"].isnull().sum() > 0:
    error = "Error converting the dates. Please ensure all dates are set."

if df["type"].isnull().sum() > 0:
    error = f"There are {df['type'].isnull().sum()} rows that do not have a value in the PN_PRLVT_ECHANGES column. Please check and correct or remove these rows."

if df["meter_number"].isnull().sum() > 0:
    error = f"There are {df['meter_number'].isnull().sum()} rows that do not have a value in the 'num_compteur' column. Please check and correct or remove these rows."

df["material"] = "water"
df["material_code"] = "EMP7.1"
df["unit"] = "m3"
df = df[["period_name", "start_date", "end_date", "material", "material_code", "quantity", "unit", "meter_number", "type"]]

print(df)
#print(df.meter_number.unique().tolist())

if delete_empty_rows:
    df = df.dropna(subset=["meter_number"])
elif error:
    print(error)

# These datasheets contain different types of flow. Now that we have formatted the file in the right shape, we 
# will select each flow type and save the results in separate files, so that they can be imported into the 
# corresponding dataset.
files = {
    "production.csv": "PRODUCTION D'EAU POTABLE",
    "extraction.csv": "PRELEVEMENT D'EAU RESSOURCE",
    "import.csv": "ACHAT D'EAU POTABLE A",
    "export.csv": "VENTE D'EAU POTABLE A",
}

for filename,type in files.items():
    export_df = df[df["type"] == type]
    export_df.drop(["type"], axis=1)
    export_df.to_csv(filename, index=None)

