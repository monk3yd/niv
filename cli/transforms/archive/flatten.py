import json


def transform(input_path: str, output_path: str):

    def flatten_json(nested_json, separator='.'):
        """
        Flattens a nested JSON (dictionary) object.

        Args:
            nested_json (dict): The nested dictionary to flatten.
            separator (str): The separator to use between keys.

        Returns:
            dict: A flattened dictionary.
        """
        flat_dict = {}

        def _flatten(obj, parent_key=''):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_key = f"{parent_key}{separator}{key}" if parent_key else key
                    _flatten(value, new_key)
            elif isinstance(obj, list):
                # Iterate through list items and create an indexed key for each
                for i, item in enumerate(obj):
                    new_key = f"{parent_key}{separator}{i}" if parent_key else str(i)
                    _flatten(item, new_key)
            else:
                # Assign the value to the flattened key
                if parent_key:
                    flat_dict[parent_key] = obj

        _flatten(nested_json)
        return flat_dict

    with open(input_path, "r", encoding="utf-8") as file:
        nested_json = json.load(file)

    flattened_data_list = [flatten_json(json_obj) for json_obj in nested_json]

    # Print the flattened list of JSON objects
    print(json.dumps(flattened_data_list, indent=2, ensure_ascii=False))

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(flattened_data_list, file, indent=2, ensure_ascii=False)

