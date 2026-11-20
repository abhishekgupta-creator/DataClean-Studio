
"""
DashEasy - File Import Engine

Supports:
- Excel (.xlsx)
- Excel (.xls) when xlrd is installed
- CSV (.csv)
- Excel sheet detection
- CSV delimiter detection
- CSV encoding handling
"""

import csv
import importlib.util
from pathlib import Path

import pandas as pd


class ImportFileError(Exception):
    """Custom exception for file import errors."""


SUPPORTED_EXTENSIONS = {".xlsx", ".xls", ".csv"}


def validate_file(file_path: str | Path) -> Path:
    """Validate the selected file."""

    path = Path(file_path)

    if not path.exists():
        raise ImportFileError("The selected file does not exist.")

    if not path.is_file():
        raise ImportFileError("The selected path is not a file.")

    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ImportFileError(
            f"Unsupported file format: {extension}"
        )

    if path.stat().st_size == 0:
        raise ImportFileError("The selected file is empty.")

    return path


def get_excel_sheet_names(file_path: str | Path) -> list[str]:
    """Return all sheet names from an Excel workbook."""

    path = validate_file(file_path)

    if path.suffix.lower() not in {".xlsx", ".xls"}:
        raise ImportFileError("Please select an Excel file.")

    if path.suffix.lower() == ".xls":
        if importlib.util.find_spec("xlrd") is None:
            raise ImportFileError(
                "Reading .xls files requires xlrd. "
                "Install it using: python -m pip install xlrd"
            )

    try:
        with pd.ExcelFile(path) as workbook:
            return workbook.sheet_names

    except ImportFileError:
        raise

    except Exception as error:
        raise ImportFileError(
            f"Unable to read Excel workbook: {error}"
        ) from error


def load_excel_file(
    file_path: str | Path,
    sheet_name: str | None = None
) -> pd.DataFrame:
    """Load an Excel worksheet into a Pandas DataFrame."""

    path = validate_file(file_path)

    if path.suffix.lower() not in {".xlsx", ".xls"}:
        raise ImportFileError("Please select an Excel file.")

    sheets = get_excel_sheet_names(path)

    if not sheets:
        raise ImportFileError(
            "The Excel workbook does not contain any worksheets."
        )

    selected_sheet = sheet_name if sheet_name is not None else sheets[0]

    if selected_sheet not in sheets:
        raise ImportFileError(
            f"Worksheet '{selected_sheet}' was not found."
        )

    try:
        dataframe = pd.read_excel(
            path,
            sheet_name=selected_sheet
        )

        return dataframe

    except Exception as error:
        raise ImportFileError(
            f"Unable to import Excel worksheet: {error}"
        ) from error


def detect_csv_encoding(file_path: str | Path) -> str:
    """Detect a supported CSV text encoding."""

    encodings = [
        "utf-8-sig",
        "utf-8",
        "cp1252",
        "latin-1",
    ]

    with open(file_path, "rb") as file:
        sample = file.read(100_000)

    for encoding in encodings:
        try:
            sample.decode(encoding)
            return encoding
        except UnicodeDecodeError:
            continue

    raise ImportFileError(
        "Unable to identify the CSV file encoding."
    )


def detect_csv_delimiter(
    file_path: str | Path,
    encoding: str
) -> str:
    """Detect CSV delimiter using a sample of the file."""

    try:
        with open(
            file_path,
            "r",
            encoding=encoding,
            newline=""
        ) as file:
            sample = file.read(100_000)

        if not sample.strip():
            raise ImportFileError("The CSV file contains no data.")

        try:
            dialect = csv.Sniffer().sniff(
                sample,
                delimiters=",;\t|"
            )
            return dialect.delimiter

        except csv.Error:
            return ","

    except UnicodeDecodeError as error:
        raise ImportFileError(
            "Unable to decode the CSV file."
        ) from error


def load_csv_file(
    file_path: str | Path,
    delimiter: str | None = None
) -> pd.DataFrame:
    """Load a CSV file into a Pandas DataFrame."""

    path = validate_file(file_path)

    if path.suffix.lower() != ".csv":
        raise ImportFileError("Please select a CSV file.")

    try:
        encoding = detect_csv_encoding(path)

        if delimiter is None:
            delimiter = detect_csv_delimiter(
                path,
                encoding
            )

        dataframe = pd.read_csv(
            path,
            encoding=encoding,
            sep=delimiter,
            low_memory=False
        )

        return dataframe

    except ImportFileError:
        raise

    except pd.errors.EmptyDataError as error:
        raise ImportFileError(
            "The CSV file does not contain readable data."
        ) from error

    except Exception as error:
        raise ImportFileError(
            f"Unable to import CSV file: {error}"
        ) from error


def load_data_file(
    file_path: str | Path,
    sheet_name: str | None = None,
    delimiter: str | None = None
) -> pd.DataFrame:
    """Automatically load an Excel or CSV file."""

    path = validate_file(file_path)

    extension = path.suffix.lower()

    if extension in {".xlsx", ".xls"}:
        return load_excel_file(
            path,
            sheet_name=sheet_name
        )

    if extension == ".csv":
        return load_csv_file(
            path,
            delimiter=delimiter
        )

    raise ImportFileError(
        "Unsupported file format."
    )
