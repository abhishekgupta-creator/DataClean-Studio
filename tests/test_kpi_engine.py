import pandas as pd
import pytest

from core.kpi import KPIEngine, KPIError


@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "Revenue": [1000, 2000, 3000, 4000],
        "Cost": [500, 1000, 1500, 2000],
        "Department": ["IT", "HR", "IT", "Sales"],
    })


def test_sum(sample_data):
    result = KPIEngine.calculate_kpi(
        sample_data, "Revenue", "SUM"
    )
    assert result["value"] == 10000


def test_average(sample_data):
    result = KPIEngine.calculate_kpi(
        sample_data, "Revenue", "AVERAGE"
    )
    assert result["value"] == 2500


def test_count(sample_data):
    result = KPIEngine.calculate_kpi(
        sample_data, "Department", "COUNT"
    )
    assert result["value"] == 4


def test_distinct_count(sample_data):
    result = KPIEngine.calculate_kpi(
        sample_data, "Department", "DISTINCT COUNT"
    )
    assert result["value"] == 3


def test_count_rows(sample_data):
    result = KPIEngine.calculate_kpi(
        sample_data, aggregation="COUNT ROWS"
    )
    assert result["value"] == 4


def test_minimum(sample_data):
    result = KPIEngine.calculate_kpi(
        sample_data, "Revenue", "MIN"
    )
    assert result["value"] == 1000


def test_maximum(sample_data):
    result = KPIEngine.calculate_kpi(
        sample_data, "Revenue", "MAX"
    )
    assert result["value"] == 4000


def test_custom_formula(sample_data):
    result = KPIEngine.calculate_custom_formula(
        sample_data,
        "Revenue - Cost",
        "Profit"
    )
    assert result["value"] == 5000


def test_invalid_column(sample_data):
    with pytest.raises(KPIError):
        KPIEngine.calculate_kpi(
            sample_data, "WrongColumn", "SUM"
        )


def test_invalid_numeric_aggregation(sample_data):
    with pytest.raises(KPIError):
        KPIEngine.calculate_kpi(
            sample_data, "Department", "SUM"
        )