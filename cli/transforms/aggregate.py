import orjson
from tqdm import tqdm
from pathlib import Path


def transform(input_dir: str, output_file: str):
    """
    Aggregates all JSON files in a directory into a single JSON file.
    """

    all_data = []

    # Use pathlib for path operations
    input_path = Path(input_dir)

    # Check if the directory exists
    if not input_path.is_dir():
        print(f"Error: Directory not found at {input_dir}")
        return

    # Get a list of al JSON files in the input directory
    files = list(input_path.glob("*.json"))
    if not files:
        print("No JSON files found in the directory.")
        return

    # Loop through each file and load its JSON content
    for filepath in tqdm(files, desc="Aggregating JSON files", unit="file"):
        with open(filepath, "rb") as f:
            try:
                data = orjson.loads(f.read())
                if isinstance(data, list):
                    all_data.extend(data)
                else:
                    all_data.append(data)
            except orjson.JSONDecodeError:
                print(f"Warning: Could not decode JSON from {filepath.name}. Skipping.")

    # Write the aggregated data to the output file
    with open(output_file, "wb") as f_out:
        f_out.write(orjson.dumps(all_data))


