import pandas as pd


def transform(input_path: str, output_path: str):

    # Read the CSV data from the in-memory buffer
    df = pd.read_csv(input_path, delimiter=";")

    # Write to Excel file
    df.to_excel(output_path, index=False, engine="openpyxl")

