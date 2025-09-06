import orjson
from flatten_json import flatten
from tqdm import tqdm



def transform(input_file: str, output_file: str):
    """
    Flattens a standard JSON file (list of objects or a single object)
    and writes the output as a standard JSON array with a progress bar.
    """
    # Step 1: Read the entire JSON file into memory with the high-speed orjson library.
    with open(input_file, "rb") as f:
        data = orjson.loads(f.read())

    all_flattened_data = []

    # Step 2: Check the type of the JSON data and process accordingly.
    if isinstance(data, list):
        # Process a list of objects with a progress bar.
        for row in tqdm(data, desc="Flattening JSON", unit=" rows"):
            all_flattened_data.append(flatten(row, separator="."))

    elif isinstance(data, dict):
        # Process a single JSON object.
        print("Input is a single JSON object; flattening...")
        all_flattened_data.append(flatten(data))

    else:
        # Handle cases where the input is not valid JSON.
        raise TypeError("Input JSON must be an object or a list of objects.")

    # Step 3: Write the collected list as a single, standard JSON array.
    with open(output_file, "wb") as f_out:
        f_out.write(orjson.dumps(all_flattened_data))


# import polars as pl
#     # Use Polars' robust read_json function to load the data.
#     df = pl.read_json(input_file, infer_schema_length=100000)
#
#     # --- STEP 1: Handle nested lists (arrays) ---
#     # Find all columns that contain lists.
#     # list_columns = [col for col in df.columns if isinstance(df[col].dtype, pl.List)]
#
#     # If any list columns are found, explode them.
#     # This creates a new row for each item in a list, duplicating other values.
#     # if list_columns:
#     #     df = df.explode(list_columns)
#
#     while True:
#         list_columns = [col for col in df.columns if isinstance(df[col].dtype, pl.List)]
#         if not list_columns:
#             break
#         # Explode the first list column found in each iteration.
#         df = df.explode(list_columns[0])
#
#     # --- STEP 2: Handle nested objects (structs) ---
#     # After exploding, it's possible new struct columns exist or were already there.
#     # We check for them again.
#     struct_columns = [col for col in df.columns if isinstance(df[col].dtype, pl.Struct)]
#     for struct_col_name in struct_columns:
#         # Get the field names from the current struct column
#         nested_fields = df.select(pl.col(struct_col_name)).schema[struct_col_name].fields
#
#         # Create a dictionary to rename the fields, prefixing them with the struct's name
#         rename_mapping = {field.name: f"{struct_col_name}_{field.name}" for field in nested_fields}
#
#         # Unnest the current struct and immediately rename its fields to avoid collisions
#         df = df.unnest(struct_col_name).rename(rename_mapping)
#
#     # If any struct columns are found, unnest them into new columns.
#     # if struct_columns:
#     #     df = df.unnest(struct_columns, name_generator=lambda name, i: f"{name}_{i}" if i > 0 else name)
#

