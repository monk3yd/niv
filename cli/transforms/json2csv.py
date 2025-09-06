import polars as pl


def transform(input_file: str, output_file: str):
    """
    Converts a JSON or JSON Lines file to a CSV file, flattening both nested
    objects (structs) and nested lists (arrays).
    """
    # Use Polars' robust read_json function to load the data.
    df = pl.read_json(input_file, infer_schema_length=100000)  # Number of rows

    # --- STEP 1: Handle nested lists (arrays) ---
    # Find all columns that contain lists.
    list_columns = [col for col in df.columns if isinstance(df[col].dtype, pl.List)]

    # If any list columns are found, explode them.
    # This creates a new row for each item in a list, duplicating other values.
    if list_columns:
        df = df.explode(list_columns)

    # --- STEP 2: Handle nested objects (structs) ---
    # After exploding, it's possible new struct columns exist or were already there.
    # We check for them again.
    struct_columns = [col for col in df.columns if isinstance(df[col].dtype, pl.Struct)]

    # If any struct columns are found, unnest them into new columns.
    if struct_columns:
        df = df.unnest(struct_columns)

    # Write the fully flattened DataFrame to the CSV file.
    df.write_csv(output_file)

