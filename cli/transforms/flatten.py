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


