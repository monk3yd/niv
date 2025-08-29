import os
import sys
import tempfile
import typer
from typing import Callable, Optional
from typing_extensions import Annotated

from .transforms import TRANSFORMS

# --- MANUAL VERSION CHECK ---
# This is a workaround for a persistent Typer/Click error in this environment.
# We handle the --version flag manually before Typer even runs.
if "--version" in sys.argv:
    print("Niv Transforms v0.1.0")
    sys.exit(0)


# Create the main Typer application instance.
app = typer.Typer(
    name="niv",
    help="An extensible CLI to apply various transformations.",
    add_completion=False,
    no_args_is_help=True
)

@app.callback()
def main():
    """
    An extensible CLI to apply various transformations.
    """
    ...


def _command_factory(name: str, transform_func: Callable):
    """
    This factory creates a unique function for each subcommand.
    This is necessary to genrate a CLI with dynamic subcommands where
    each can have its own help text and parameters.
    """
    def command(
        input_file: Annotated[
            str,
            typer.Option(
                "--input",
                "-i",
                help="Path to the input file.",
                exists=True,
                file_okay=True,
                dir_okay=False,
                readable=True,
                resolve_path=True
            )
        ],
        output_file: Annotated[
            Optional[str],
            typer.Option(
                "--output",
                "-o",
                help="Path for the output file. If not provided, prints standard output.",
                file_okay=True,
                dir_okay=False,
                writable=True,
                resolve_path=True
            )
        ] = None,
    ):
        """
        Dynamically generated command to apply the transform.
        The help text for this command is derived from the transform function's docstring.
        """
        try:
            if output_file:
                # If an output file is specified, run the transform directly.
                transform_func(input_file, output_file)
                typer.secho(f"Successfully created output file: {output_file}", fg=typer.colors.GREEN)
            else:
                # If not output file, run transform on a temporary file and print result to stdout.
                # This keeps the transform function's contract simple (file-in, file-out)
                fd, temp_path = tempfile.mkstemp(suffix=".tmp", text=True)
                os.close(fd)  # Close descriptor, we only need the path

                try:
                    transform_func(input_file, temp_path)
                    with open(temp_path, "r", encoding="utf-8") as file:
                        result = file.read()

                    # Write result to standard output, allowing for redirection (e.g., > out.txt)
                    sys.stdout.write(result)
                finally:
                    # Ensure the temporary file is always deleted.
                    os.remove(temp_path)

        except Exception as err:
            typer.secho(f"An error occurred during transformation: {err}", fg=typer.colors.RED, err=True)
            raise typer.Exit(1)

    # Use the first line of the transform function's docstring as the CLI help text.
    docstring = transform_func.__doc__ or f"Applies the '{name}' transform."
    command.__doc__ = docstring.strip().split("\n")[0]

    return command


# --- DYNAMIC SUBCOMMAND CREATION ---
# Iterate over all discovered transforms and register them as subcommands.
for name, func in TRANSFORMS.items():
    # Sanitize the name for the CLI
    command_name = name.replace("_", "-")

    # Create the command function using the factory
    command_func = _command_factory(name, func)

    # Add the generated function to the Typer app as a command
    app.command(name=command_name)(command_func)


if __name__ == "__main__":
    app()

