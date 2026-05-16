"""
This is the project's loader file. It does the following:

- Checks if the online_retail_II.xlsx file exists in data/raw/
- Reads the two Excel tabs (Year 2009-2010 and Year 2010-2011)
- Concatenates the two into a single DataFrame
- Converts InvoiceDate to datetime
- Saves to data/processed/ as Parquet
"""

import logging
import shutil
from pathlib import Path
import zipfile

import pandas as pd

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data/raw"
PROCESSED_DIR = BASE_DIR / "data/processed"

def check_file_exists(*paths: Path) -> None:
    """Check if the specified file exists."""
    for path in paths:
        if not path.exists():
            logger.error(f"File not found: {path}")
            raise FileNotFoundError(
                f"File not found: {path}\n"
                "Download the dataset from UCI ML Repository:\n"
                "https://archive.ics.uci.edu/dataset/502/online+retail+ii\n"
                "and place it in data/raw/"
            )

def load_and_process_data() -> pd.DataFrame:
    """Load the Excel file, concatenate the sheets, and process the data."""
    file_path = RAW_DIR / "online+retail+ii.zip"
    check_file_exists(file_path)

    logger.info(f"Extracting {file_path} to {RAW_DIR}")
    with zipfile.ZipFile(file_path, "r") as zip_ref:
        zip_ref.extractall(RAW_DIR)
    
    file_path = RAW_DIR / "online_retail_II.xlsx"
    logger.info(f"Loading data from {file_path}")
    df_2009_2010 = pd.read_excel(file_path, sheet_name="Year 2009-2010", dtype={"Invoice": str, "StockCode": str, "Customer ID": str, "Country": str, "Description": str, "Quantity": int, "Price": float}, engine='calamine')
    df_2010_2011 = pd.read_excel(file_path, sheet_name="Year 2010-2011", dtype={"Invoice": str, "StockCode": str, "Customer ID": str, "Country": str, "Description": str, "Quantity": int, "Price": float}, engine='calamine')

    logger.info("Concatenating dataframes")
    df = pd.concat([df_2009_2010, df_2010_2011], ignore_index=True)
    logger.info(f"Column types:\n{df.dtypes}")

    logger.info("Converting InvoiceDate to datetime")
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    logger.info(f"Missing values in InvoiceDate: {df['InvoiceDate'].isna().sum()}")

    return df


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)s  %(message)s",
        datefmt="%H:%M:%S",
    )
        
    logger.info("Starting data loading and processing")
    df = load_and_process_data()

    output_path = PROCESSED_DIR / "online_retail_ii.parquet"
    logger.info(f"Saving processed data to {output_path}")
    df.to_parquet(output_path, index=False)
    logger.info("Data loading and processing completed successfully")
