"""
This is the project's validation file. It checks the following:

- Minimum expected shape
- Required columns present
- Correct types after loader
- Number of nulls per column
- Invoices with C (cancellations)
- Negative or zero prices
- Negative quantities outside of cancellations

Run after loader.py:
  python src/ingestion/validation.py
"""

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[2]
PROCESSED_DIR = BASE_DIR / "data/processed"

REQUIRED_COLUMNS = [
    "Invoice", "StockCode", "Description", "Quantity", "InvoiceDate", "Price", "Customer ID", "Country"
]

class ValidationError(Exception):
    pass

def validate_data(df: pd.DataFrame) -> None:
    """
    Run all validation checks on the DataFrame.
    
    Returns:
        None. Raises ValidationError if any check fails.  

    Raises:
        ValidationError: If any validation check fails.
    """
    logger.info("Starting data validation")

    # Check shape
    if df.shape[0] < 500000:
        raise ValidationError(f"Expected at least 500,000 rows, found {df.shape[0]}")

    # Check required columns
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValidationError(f"Missing required columns: {missing_cols}")

    # Check types
    expected_types = {
        "Invoice": "str",
        "StockCode": "str",
        "Description": "str",
        "Quantity": "int64",
        "InvoiceDate": "datetime64[us]",
        "Price": "float64",
        "Customer ID": "str",
        "Country": "str"
    }
    for col, expected_type in expected_types.items():
        if expected_type == "str":
            is_valid_type = pd.api.types.is_string_dtype(df[col])
        elif expected_type == "int64":
            is_valid_type = pd.api.types.is_integer_dtype(df[col])
        elif expected_type == "float64":
            is_valid_type = pd.api.types.is_float_dtype(df[col])
        elif expected_type == "datetime64[us]":
            is_valid_type = pd.api.types.is_datetime64_any_dtype(df[col])
        else:
            logger.warning(f"Unknown expected type '{expected_type}' for column '{col}', skipping type check")
            is_valid_type = True
        if not is_valid_type:
            raise ValidationError(f"Column '{col}' has incorrect type. Expected {expected_type}, found {df[col].dtype}")


    # Check nulls
    null_counts = df.isnull().sum()
    logger.info(f"Null values per column:\n{null_counts}")

    # Check cancellations
    cancellations = df[df["Invoice"].str.startswith("C", na=False)]
    if not cancellations.empty:
        logger.warning(f"Found {len(cancellations)} cancellation invoices")

    # Check negative or zero prices
    invalid_prices = df[df["Price"] <= 0]
    if not invalid_prices.empty:
        logger.warning(f"Found {len(invalid_prices)} rows with non-positive prices")

    # Check negative quantities outside of cancellations
    non_cancellations = df[~df["Invoice"].str.startswith("C", na=False)]
    invalid_quantities = non_cancellations[non_cancellations["Quantity"] < 0]
    if not invalid_quantities.empty:
        logger.warning(f"Found {len(invalid_quantities)} rows with negative quantities outside of cancellations")



if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)s  %(message)s",
        datefmt="%H:%M:%S",
    )

    data_path = PROCESSED_DIR / "online_retail_ii.parquet"
    if not data_path.exists():
        logger.error(f"Processed data file not found: {data_path}")
        logger.error("Run loader.py first to create the processed data file.")
        sys.exit(1)
    logger.info(f"Loading data from {data_path}")
    df = pd.read_parquet(data_path)
    try:
        validate_data(df)
        logger.info("Data validation passed successfully")
    except ValidationError as e:
        logger.error(f"Data validation failed: {e}")
        sys.exit(1)