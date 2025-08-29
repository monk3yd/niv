import importlib
import sys
import pkgutil

# A dictionary to hold the discovered transform functions.
TRANSFORMS = {}

# Use pkgutil to reliably find all modules within this 'transforms' subpackage.
# __path__ is a special attribute of packages that lists the directories to search.
# This works correctly for both local development and installed packages.
for _, module_name, _ in pkgutil.iter_modules(__path__):
    try:
        # Dynamically import the module using its name.
        # The '.' is crucial for a relative import within the same package.
        module = importlib.import_module(f".{module_name}", package=__package__)

        # Check if the imported module has a function named 'transform'.
        if hasattr(module, "transform"):
            # If it does, add it to our dictionary of available transforms.
            TRANSFORMS[module_name] = module.transform
        else:
            # This handles cases where a file might be a helper module, not a transform.
            pass

    except ImportError as e:
        # If an import fails (e.g., a missing dependency),
        # print a clear warning to the user instead of crashing silently.
        print(
            f"[WARNING] Could not import transform '{module_name}'. Skipping. Error: {e}",
            file=sys.stderr
        )
