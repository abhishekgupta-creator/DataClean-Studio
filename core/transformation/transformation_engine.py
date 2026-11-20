"""DashEasy - Data Transformation Engine."""
import pandas as pd
from datetime import date
import calendar


class TransformationError(Exception):
    """Custom exception for transformation errors."""


class TransformationEngine:
    """Perform data transformation operations using Pandas."""

    def __init__(self, dataframe):
        if not isinstance(dataframe, pd.DataFrame):
            raise TransformationError("Invalid dataset.")
        self.original_df = dataframe.copy(deep=True)
        self.df = dataframe.copy(deep=True)

    def reset(self):
        self.df = self.original_df.copy(deep=True)
        return self.get_dataframe()

    def get_dataframe(self):
        return self.df.copy(deep=True)

    def _validate_new_column(self, new_column):
        if not isinstance(new_column, str) or not new_column.strip():
            raise TransformationError("Enter a column name.")

        new_column = new_column.strip()
        if new_column in self.df.columns:
            raise TransformationError(
                f"Column '{new_column}' already exists."
            )
        return new_column

    def _numeric_column(self, column):
        if column not in self.df.columns:
            raise TransformationError(
                f"Column '{column}' not found."
            )
        try:
            return pd.to_numeric(self.df[column], errors="raise")
        except (ValueError, TypeError) as error:
            raise TransformationError(
                f"Column '{column}' must contain numeric values."
            ) from error

    def _calculate(self, first, operation, second):
        operations = {
            "Add": lambda: first + second,
            "Subtract": lambda: first - second,
            "Multiply": lambda: first * second,
            "Divide": lambda: first / second,
        }

        if operation not in operations:
            raise TransformationError("Invalid calculation.")

        if operation == "Divide":
            if isinstance(second, pd.Series):
                if second.eq(0).any():
                    raise TransformationError(
                        "Cannot divide by zero. Check the second column."
                    )
            elif float(second) == 0:
                raise TransformationError("Cannot divide by zero.")

        try:
            return operations[operation]()
        except (ValueError, TypeError, ZeroDivisionError) as error:
            raise TransformationError(str(error)) from error

    def create_column(
        self, new_column, source_column, operation, value
    ):
        """Create a calculated column using a fixed numeric value."""
        new_column = self._validate_new_column(new_column)
        first = self._numeric_column(source_column)

        try:
            number = float(value)
        except (ValueError, TypeError) as error:
            raise TransformationError(
                "Enter a valid numeric value."
            ) from error

        self.df[new_column] = self._calculate(
            first, operation, number
        )
        return self.get_dataframe()

    def create_column_percentage(
        self, new_column, source_column, operation, percentage
    ):
        """Create a new column by adjusting values by a percentage."""
        new_column = self._validate_new_column(new_column)
        first = self._numeric_column(source_column)

        try:
            raw_percentage = (
                str(percentage).strip().replace("%", "").strip()
            )
            rate = float(raw_percentage) / 100.0
        except (ValueError, TypeError) as error:
            raise TransformationError(
                "Enter a valid percentage, for example 5 or 10%."
            ) from error

        if rate < 0:
            raise TransformationError(
                "Enter a positive percentage. Use Subtract to reduce the value."
            )

        if operation == "Add":
            factor = 1 + rate
        elif operation == "Subtract":
            factor = 1 - rate
        elif operation == "Multiply":
            factor = rate
        elif operation == "Divide":
            if rate == 0:
                raise TransformationError(
                    "Percentage cannot be zero for division."
                )
            factor = 1 / rate
        else:
            raise TransformationError(
                "Invalid percentage calculation."
            )

        self.df[new_column] = first * factor
        return self.get_dataframe()

    def create_column_from_columns(
        self, new_column, first_column, operation, second_column
    ):
        """Create a calculated column using two existing columns."""
        new_column = self._validate_new_column(new_column)

        if first_column == second_column:
            raise TransformationError(
                "Please select two different columns."
            )

        first = self._numeric_column(first_column)
        second = self._numeric_column(second_column)

        self.df[new_column] = self._calculate(
            first, operation, second
        )
        return self.get_dataframe()

    @staticmethod
    def _experience_parts(start_value, end_value):
        if pd.isna(start_value) or pd.isna(end_value):
            return None

        start = pd.Timestamp(start_value).date()
        end = pd.Timestamp(end_value).date()

        if start > end:
            return None

        total_months = (
            (end.year - start.year) * 12
            + end.month - start.month
        )

        if end.day < start.day:
            total_months -= 1

        years, months = divmod(total_months, 12)

        target_month = start.month - 1 + total_months
        year = start.year + target_month // 12
        month = target_month % 12 + 1
        day = min(
            start.day,
            calendar.monthrange(year, month)[1]
        )

        anniversary = date(year, month, day)
        days = (end - anniversary).days

        return years, months, days, total_months

    def calculate_experience(
        self, new_column, source_column,
        output_format="Years + Months", end_date=None
    ):
        """Create an experience column from a joining/start date."""
        new_column = self._validate_new_column(new_column)

        if source_column not in self.df.columns:
            raise TransformationError(
                "Select a valid Joining Date column."
            )

        if end_date:
            end = pd.to_datetime(
                end_date, errors="coerce", dayfirst=False
            )
            if pd.isna(end):
                raise TransformationError(
                    "Enter End Date in YYYY-MM-DD format."
                )
        else:
            end = pd.Timestamp.today().normalize()

        dates = pd.to_datetime(
            self.df[source_column],
            format="mixed",
            errors="coerce",
            dayfirst=False,
            yearfirst=True
        )

        def format_value(start_value):
            parts = self._experience_parts(start_value, end)

            if parts is None:
                return pd.NA

            years, months, days, total_months = parts

            if output_format == "Years":
                return years
            if output_format == "Years + Months":
                return f"{years} Years, {months} Months"
            if output_format == "Total Months":
                return total_months
            if output_format == "Years + Months + Days":
                return (
                    f"{years} Years, {months} Months, {days} Days"
                )

            raise TransformationError(
                "Choose a valid experience output format."
            )

        self.df[new_column] = dates.map(format_value)
        return self.get_dataframe()

    def change_data_type(self, column, data_type):
        if column not in self.df.columns:
            raise TransformationError(
                f"Column '{column}' not found."
            )

        try:
            if data_type == "Text":
                self.df[column] = self.df[column].astype("string")

            elif data_type == "Integer":
                self.df[column] = pd.to_numeric(
                    self.df[column], errors="raise"
                ).astype("Int64")

            elif data_type == "Float":
                self.df[column] = pd.to_numeric(
                    self.df[column], errors="raise"
                )

            elif data_type == "Date":
                self.df[column] = pd.to_datetime(
                    self.df[column], errors="raise"
                )

            elif data_type == "Boolean":
                mapping = {
                    "true": True, "false": False,
                    "1": True, "0": False,
                    "yes": True, "no": False,
                }

                converted = self.df[column].map(
                    lambda value: (
                        mapping.get(str(value).strip().lower())
                        if pd.notna(value) else pd.NA
                    )
                )

                invalid = (
                    self.df[column].notna()
                    & converted.isna()
                )

                if invalid.any():
                    raise ValueError("Invalid Boolean values.")

                self.df[column] = converted.astype("boolean")

            else:
                raise TransformationError(
                    "Unsupported data type."
                )

            return self.get_dataframe()

        except (ValueError, TypeError) as error:
            raise TransformationError(str(error)) from error

    def split_column(self, column, separator, new_columns):
        if column not in self.df.columns:
            raise TransformationError("Column not found.")

        names = [
            name.strip()
            for name in new_columns
            if name.strip()
        ]

        if len(names) < 2:
            raise TransformationError(
                "Enter at least two column names."
            )

        if len(names) != len(set(names)):
            raise TransformationError(
                "Duplicate output column names."
            )

        if any(name in self.df.columns for name in names):
            raise TransformationError(
                "An output column already exists."
            )

        try:
            split_data = self.df[column].astype("string").str.split(
                separator, expand=True
            )

            if split_data.shape[1] > len(names):
                raise TransformationError(
                    "More split parts found than output columns."
                )

            for index, name in enumerate(names):
                self.df[name] = (
                    split_data[index]
                    if index in split_data.columns
                    else pd.NA
                )

            return self.get_dataframe()

        except Exception as error:
            if isinstance(error, TransformationError):
                raise
            raise TransformationError(str(error)) from error

    def merge_columns(self, columns, new_column, separator=" "):
        if len(columns) < 2:
            raise TransformationError(
                "Select at least two columns."
            )

        if any(
            column not in self.df.columns
            for column in columns
        ):
            raise TransformationError(
                "Invalid column selection."
            )

        new_column = self._validate_new_column(new_column)

        self.df[new_column] = (
            self.df[columns]
            .astype("string")
            .fillna("")
            .agg(separator.join, axis=1)
        )

        return self.get_dataframe()

    def replace_values(self, column, old_value, new_value):
        if column not in self.df.columns:
            raise TransformationError("Column not found.")

        self.df[column] = self.df[column].replace(
            old_value, new_value
        )
        return self.get_dataframe()

    def sort_data(self, column, order="Ascending"):
        if column not in self.df.columns:
            raise TransformationError("Column not found.")

        if order not in ("Ascending", "Descending"):
            raise TransformationError("Invalid sort order.")

        self.df = self.df.sort_values(
            by=column,
            ascending=(order == "Ascending"),
            na_position="last"
        ).reset_index(drop=True)

        return self.get_dataframe()

    def filter_rows(self, column, condition, value):
        if column not in self.df.columns:
            raise TransformationError("Column not found.")

        series = self.df[column]

        conditions = {
            "Equals": lambda: series == value,
            "Not Equals": lambda: series != value,
            "Contains": lambda: series.astype("string").str.contains(
                str(value), case=False, na=False, regex=False
            ),
            "Greater Than": lambda: (
                pd.to_numeric(series, errors="raise") > float(value)
            ),
            "Less Than": lambda: (
                pd.to_numeric(series, errors="raise") < float(value)
            ),
            "Greater Than or Equal": lambda: (
                pd.to_numeric(series, errors="raise") >= float(value)
            ),
            "Less Than or Equal": lambda: (
                pd.to_numeric(series, errors="raise") <= float(value)
            ),
            "Is Empty": lambda: series.isna(),
            "Is Not Empty": lambda: series.notna(),
        }

        if condition not in conditions:
            raise TransformationError("Invalid filter condition.")

        try:
            mask = conditions[condition]()
            self.df = self.df.loc[mask].reset_index(drop=True)
            return self.get_dataframe()

        except (ValueError, TypeError) as error:
            raise TransformationError(str(error)) from error

    def conditional_percentage_column(
        self, new_column, source_column, operator, threshold,
        true_percentage, false_percentage
    ):
        """Create a percentage-adjusted numeric column using a threshold rule."""
        if source_column not in self.df.columns:
            raise TransformationError("Source column not found.")

        new_column = self._validate_new_column(new_column)

        try:
            values = pd.to_numeric(
                self.df[source_column], errors="raise"
            )
            threshold_value = float(
                str(threshold).replace(",", "").strip()
            )
            true_rate = (
                float(
                    str(true_percentage).strip().replace("%", "")
                ) / 100
            )
            false_rate = (
                float(
                    str(false_percentage).strip().replace("%", "")
                ) / 100
            )

        except (ValueError, TypeError) as error:
            raise TransformationError(
                "Enter a valid numeric threshold and percentages "
                "(for example 50000, 10%, 5%)."
            ) from error

        if true_rate < 0 or false_rate < 0:
            raise TransformationError(
                "Bonus percentages cannot be negative."
            )

        comparisons = {
            ">": lambda: values > threshold_value,
            "<": lambda: values < threshold_value,
            ">=": lambda: values >= threshold_value,
            "<=": lambda: values <= threshold_value,
            "Equals": lambda: values == threshold_value,
            "Not Equals": lambda: values != threshold_value,
        }

        if operator not in comparisons:
            raise TransformationError(
                "Select a valid condition operator."
            )

        mask = comparisons[operator]()

        rates = pd.Series(
            false_rate,
            index=self.df.index,
            dtype="float64"
        )
        rates.loc[mask] = true_rate

        self.df[new_column] = values * (1 + rates)
        return self.get_dataframe()

    def conditional_column(
        self, new_column, source_column, operator,
        condition_value, true_value, false_value
    ):
        if source_column not in self.df.columns:
            raise TransformationError("Source column not found.")

        new_column = self._validate_new_column(new_column)
        series = self.df[source_column]

        if operator in (">", "<", ">=", "<="):
            series = pd.to_numeric(series, errors="raise")
            condition_value = float(condition_value)

        comparisons = {
            "Equals": lambda: series == condition_value,
            "Not Equals": lambda: series != condition_value,
            ">": lambda: series > condition_value,
            "<": lambda: series < condition_value,
            ">=": lambda: series >= condition_value,
            "<=": lambda: series <= condition_value,
        }

        if operator not in comparisons:
            raise TransformationError(
                "Invalid condition operator."
            )

        self.df[new_column] = comparisons[operator]().map(
            {True: true_value, False: false_value}
        )

        return self.get_dataframe()