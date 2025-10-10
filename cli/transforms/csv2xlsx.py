import polars as pl
import xlsxwriter
import subprocess
from tqdm import tqdm


def transform(input_file: str, output_file: str):
    """
    Converts a large CSV file to an XLSX (Excel) file with a progress bar, 
    using a memory-efficient streaming approach.
    """
    # Get the total number of rows for the progress bar.
    total_rows = get_line_count(input_file)

    # Use xlsxwriter's constant_memory mode for writing large files.
    # This mode writes data row by row and doesn't keep the entire file in memory.
    workbook = xlsxwriter.Workbook(
        output_file,
        {
            "constant_memory": True,
            "strings_to_urls": False,
            "use_zip64": True,
        }
    )
    worksheet = workbook.add_worksheet()

    # Create a batched CSV reader to process the file in chunks.
    # The batch_size can be adjusted based on your available RAM.
    reader = pl.read_csv_batched(input_file, batch_size=50000, infer_schema_length=100000)

    # Initialize variables for the loop
    header_written = False
    current_row = 1

    # Initialize progress bar
    with tqdm(total=total_rows, desc="Converting CSV to XLSX", unit="rows") as pbar:
        # Loop unitl no more batches are returned.
        while True:

            # Fetch the next batch (we fetch one at a time).
            batches = reader.next_batches(1)

            # If the list of batches is empty, we're done.
            if not batches:
                break

            batch_df = batches[0]

            # Write the header only onece from the first batch.
            if not header_written:
                header = batch_df.columns
                worksheet.write_row(0, 0, header)
                header_written = True

            # Write the rows from the current batch.
            for row in batch_df.iter_rows():
                worksheet.write_row(current_row, 0, row)
                current_row += 1

            # Update the progress bar.
            pbar.update(len(batch_df))

    # Close the workbook to save the file.
    workbook.close()


def get_line_count(file_path):
    """Counts the number of lines in a file without loading it into memory."""
    try:
        # A fast way to count lines on Unix-like systems.
        return int(subprocess.check_output(['wc', '-l', file_path]).split()[0]) - 1
    except (FileNotFoundError, ValueError):
        # Fallback for other systems or if 'wc' is not available.
        with open(file_path, 'r') as f:
            count = sum(1 for line in f)
        return count - 1 if count > 0 else 0
