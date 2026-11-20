
"""Automated tests for DashEasy file import engine."""

import pandas as pd
import pytest

from core.import_engine.file_loader import (
    load_data_file,
    load_excel_file,
    get_excel_sheet_names,
    ImportFileError,
)


def test_load_csv(tmp_path):
    """Test importing a CSV file."""

    file_path = tmp_path / "sales.csv"

    pd.DataFrame({
        "Product": ["Laptop", "Mouse", "Keyboard"],
        "Sales": [50000, 1000, 2000],
    }).to_csv(file_path, index=False)

    df = load_data_file(file_path)

    assert len(df) == 3
    assert len(df.columns) == 2
    assert "Product" in df.columns
    assert df["Sales"].sum() == 53000


def test_load_semicolon_csv(tmp_path):
    """Test automatic semicolon delimiter detection."""

    file_path = tmp_path / "sales_semicolon.csv"

    file_path.write_text(
        "Product;Sales\nLaptop;50000\nMouse;1000\n",
        encoding="utf-8"
    )

    df = load_data_file(file_path)

    assert len(df) == 2
    assert list(df.columns) == ["Product", "Sales"]


def test_load_excel(tmp_path):
    """Test Excel import and sheet detection."""

    file_path = tmp_path / "business_data.xlsx"

    with pd.ExcelWriter(file_path) as writer:
        pd.DataFrame({
            "Employee": ["A", "B"],
            "Salary": [30000, 40000],
        }).to_excel(
            writer,
            sheet_name="HR",
            index=False
        )

        pd.DataFrame({
            "Product": ["Laptop", "Mouse"],
            "Revenue": [50000, 1000],
        }).to_excel(
            writer,
            sheet_name="Sales",
            index=False
        )

    sheets = get_excel_sheet_names(file_path)

    assert sheets == ["HR", "Sales"]

    df = load_excel_file(
        file_path,
        sheet_name="Sales"
    )

    assert len(df) == 2
    assert "Revenue" in df.columns
    assert df["Revenue"].sum() == 51000


def test_missing_file():
    """Test handling of missing files."""

    with pytest.raises(ImportFileError):
        load_data_file("missing_file.csv")


def test_unsupported_file(tmp_path):
    """Test unsupported file format."""

    file_path = tmp_path / "document.txt"
    file_path.write_text("Sample data")

    with pytest.raises(ImportFileError):
        load_data_file(file_path)
