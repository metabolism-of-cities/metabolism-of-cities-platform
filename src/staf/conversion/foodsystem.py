from openpyxl import load_workbook
import pandas as pd
import numpy as np
import calendar
from core.models import Material

CONVERSION_STEPS = {
    1: "Preliminary review of rows and columns",
    2: "Check processes",
    3: "Check food groups",
    4: "Check dates",
    5: "Check quantities",
    6: "Check optional granularity",
}

def convert_file(file, return_csv=False):

    df = pd.read_excel(file)

    error = None
    results = {}

    # Sometimes pandas reads rows that are empty and includes them; let's delete those empty rows from the dataframe
    df.dropna(how="all", inplace=True) 

    try:
        item_list = df["Process"].unique().tolist()
        text = "The following processes have been identified:"
        error = False
    except:
        text = "No 'Process' column found"
        item_list = None
        error = True

    results["Processes"] = {
        "icon": "random",
        "text": text,
        "item_list": item_list,
        "error": error,
    }

    try:
        all = df["Food group"].unique().tolist()
        error = False
        text = "The following food groups have been identified:"
        all_food_groups = Material.objects.values_list("name", flat=True).filter(catalog_id=1014866)
        item_list = []
        for each in all:
            if each not in all_food_groups:
                error = True
                text = "These food groups are not part of the official list; please check the spelling:"
                item_list.append(each)
        if not error:
            item_list = all

    except:
        item_list = None
        error = True
        text = "No 'Food group' column found"

    results["Food groups"] = {
        "icon": "apple-alt",
        "item_list": item_list,
        "error": error,
        "text": text,
    }

    try:
        item_list = df["Year"].unique().tolist()
        error = False
        text = "Data are available for the following year(s):"
    except:
        text = "No 'Year' column found"
        error = True
        item_list = None

    results["Year"] = {
        "icon": "calendar",
        "text": text,
        "item_list": item_list,
        "error": error,
    }

    try:
        invalid_numbers = df[df["Quantity (t/year)"].isnull()]
        invalid_numbers.index += 2 # Make the row numbers match those shown in a spreadsheet program
        if invalid_numbers.shape[0]:
            error = True
            columns_to_keep = ["Process", "Food name"]
            table = invalid_numbers[columns_to_keep]
            text = "We have found the following rows containing invalid quantities:"
        else:
            text = "All rows contain valid numbers"
            error = False
            table = None
    except:
        text = "No 'Quantity' column found"
        error = True
        table = None

    results["Data"] = {
        "icon": "table",
        "text": text,
        "error": error,
        "table": table,
    }

    #Material.objects.create(name=each, catalog_id=1014866)

    if not return_csv:
        return results
    else:
        df["start_date"] = df["Year"].astype(str) + "-01-01"
        df["end_date"] = df["Year"].astype(str) + "-12-31"

        df["start_date"] = pd.to_datetime(df["start_date"])
        df["end_date"] = pd.to_datetime(df["end_date"])

        # Check if any of the columns that are important contain empty cells...
        if df["start_date"].isnull().sum() or df["end_date"].isnull().sum() > 0:
            error = "Error converting the dates. Please ensure all dates are set."

        df["unit"] = "t"

        col_names = {
            "Year": "period_name",
            "Quantity (t/year)": "quantity",
            "Location": "location",
            "Segment": "segment",
            "Food name": "material",
            "Process": "process",
            "Food group": "material_code",
        }
        df.rename(columns = col_names, inplace = True)

        processes = {
            "Production": 1014853,
            "Food supply": 1014854,
            "Imports": 1014855,
            "Exports": 1014855, ##### MUST BE FIXED!!
            "Retail sales": 1014856,
            "Waste": 1014857,
            "Food consumption": 1014858,
        }

        all_food_groups = Material.objects.filter(catalog_id=1014866)
        replacements = {}
        for each in all_food_groups:
            replacements[each.name] = each.code

        df["material_code"] = df["material_code"].replace(replacements)

        df["process"] = df["process"].replace(processes)

        # Temp fix to get the right location for now
        df = df.drop(["location"], axis=1)
        df["location"] = return_csv
        df["comment"] = ""

        df = df[["period_name", "start_date", "end_date", "material", "material_code", "quantity", "unit", "location", "comment", "segment", "process"]]
        return df.to_csv(None, index=None)
