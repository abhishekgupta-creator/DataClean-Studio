"""DashEasy - comprehensive, undoable pandas data-cleaning engine."""



from datetime import datetime, date

import re



import pandas as pd





class CleaningEngine:

    TEXT_OPERATIONS = {

        "trim_spaces",

        "remove_extra_spaces",

        "uppercase",

        "lowercase",

        "proper_case",

        "remove_special_chars",

        "remove_numbers",

        "remove_letters",

        "find_replace",

        "standardize_categories",

        "remove_currency_symbols",

        "remove_commas",

    }



    DATE_OPERATIONS = {

        "extract_year",

        "extract_month",

        "extract_day",

        "extract_day_name",

    }




    @staticmethod
    def _experience_parts(start_value, end_value):
        """Return completed years, months and remaining days."""
        if pd.isna(start_value) or pd.isna(end_value):
            return None

        start = pd.Timestamp(start_value).date()
        end = pd.Timestamp(end_value).date()

        if start > end:
            return None

        total_months = (end.year - start.year) * 12 + (end.month - start.month)
        if end.day < start.day:
            total_months -= 1

        years, months = divmod(total_months, 12)

        # Add completed months to the start date, clamping month-end dates.
        target_month = start.month - 1 + total_months
        year = start.year + target_month // 12
        month = target_month % 12 + 1
        import calendar
        day = min(start.day, calendar.monthrange(year, month)[1])
        anniversary = date(year, month, day)
        days = (end - anniversary).days

        return years, months, days, total_months

    @classmethod
    def _format_experience(cls, start_value, end_value, output_format):
        parts = cls._experience_parts(start_value, end_value)
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
            return f"{years} Years, {months} Months, {days} Days"

        raise ValueError("Choose a valid experience output format.")

    def __init__(self, dataframe=None):

        self.original_dataframe = None

        self.working_dataframe = None



        self.undo_stack = []

        self.redo_stack = []

        self.history = []



        if dataframe is not None:

            self.set_dataframe(dataframe)



    # ---------------------------------------------------------

    # DATAFRAME MANAGEMENT

    # ---------------------------------------------------------



    def set_dataframe(self, dataframe):

        if not isinstance(dataframe, pd.DataFrame):

            raise TypeError("Expected a pandas DataFrame.")



        self.original_dataframe = dataframe.copy(deep=True)

        self.working_dataframe = dataframe.copy(deep=True)



        self.undo_stack.clear()

        self.redo_stack.clear()

        self.history.clear()



    def get_dataframe(self):

        if self.working_dataframe is None:

            return None



        return self.working_dataframe.copy(deep=True)



    def get_history(self):

        return [item.copy() for item in self.history]



    def clear_history(self):

        self.history.clear()



    # ---------------------------------------------------------

    # DATE PARSING

    # ---------------------------------------------------------



    @staticmethod

    def _parse_date_column(series):

        """

        Parse date values without swapping month and day.



        Supports:

        - YYYY-MM-DD

        - Excel datetime values

        - Other recognizable date representations



        For this dataset, ISO year-month-day is preferred.

        Missing and invalid dates become NaT.

        """



        if pd.api.types.is_datetime64_any_dtype(series):

            return pd.to_datetime(series, errors="coerce")



        # First, parse ISO dates such as 2024-01-10.

        # format='mixed' supports a column containing different

        # date representations while yearfirst avoids day/month swapping.

        try:

            parsed = pd.to_datetime(

                series,

                format="mixed",

                errors="coerce",

                dayfirst=False,

                yearfirst=True,

            )

        except (ValueError, TypeError):

            parsed = pd.to_datetime(

                series,

                errors="coerce",

                dayfirst=False,

                yearfirst=True,

            )



        return parsed



    # ---------------------------------------------------------

    # COLUMN HELPERS

    # ---------------------------------------------------------



    @staticmethod

    def _normalize_columns(column, dataframe):

        if isinstance(column, (list, tuple, set)):

            cols = list(column)



        elif column is None:

            cols = []



        else:

            cols = [column]



        invalid = [

            c for c in cols

            if c not in dataframe.columns

        ]



        if invalid:

            raise ValueError(

                f"Invalid column selection: {invalid}"

            )



        return cols



    @staticmethod

    def _text_map(series, fn):

        return series.map(

            lambda x: fn(x) if isinstance(x, str) else x

        )



    # ---------------------------------------------------------

    # OPERATION HISTORY

    # ---------------------------------------------------------



    def _record(

        self,

        operation,

        column,

        before,

        result,

        details,

    ):

        if isinstance(column, list):

            column_name = ", ".join(map(str, column))

        else:

            column_name = column or "All Columns"



        self.history.append({

            "time": datetime.now().strftime("%H:%M:%S"),

            "date": datetime.now().strftime("%d-%m-%Y"),

            "operation": operation.replace("_", " ").title(),

            "column": column_name,

            "rows_before": len(before),

            "rows_after": len(result),

            "rows_affected": abs(len(before) - len(result)),

            "columns_before": len(before.columns),

            "columns_after": len(result.columns),

            "details": details,

            "status": "Applied",

        })



    def _history_action(

        self,

        name,

        before,

        after,

        details,

        status,

    ):

        return {

            "time": datetime.now().strftime("%H:%M:%S"),

            "date": datetime.now().strftime("%d-%m-%Y"),

            "operation": name,

            "column": "All Columns",

            "rows_before": len(before),

            "rows_after": len(after),

            "rows_affected": abs(len(before) - len(after)),

            "columns_before": len(before.columns),

            "columns_after": len(after.columns),

            "details": details,

            "status": status,

        }



    # ---------------------------------------------------------

    # MAIN APPLY METHOD

    # ---------------------------------------------------------



    def apply(

        self,

        operation,

        column=None,

        value=None,

        **kwargs,

    ):

        if self.working_dataframe is None:

            raise ValueError("No dataset loaded.")



        df = self.working_dataframe.copy(deep=True)

        result = df.copy(deep=True)



        cols = self._normalize_columns(column, df)



        val = "" if value is None else str(value)



        details = ""



        # Operations that work on the entire dataset

        all_ops = {

            "remove_duplicates",

            "remove_duplicate_columns",

            "remove_empty_rows",

            "remove_empty_columns",

            "drop_missing_rows",

            "remove_rows_condition",

            "sort_rows",

            "standardize_column_names",

        }



        # -----------------------------------------------------

        # DATASET-WIDE OPERATIONS

        # -----------------------------------------------------



        if operation in all_ops:



            if operation == "remove_duplicates":

                result = df.drop_duplicates(

                    subset=cols or None

                ).copy()



                details = "Duplicate rows removed."



            elif operation == "remove_duplicate_columns":

                result = df.loc[

                    :, ~df.columns.duplicated()

                ].copy()



                details = "Duplicate-name columns removed."



            elif operation == "remove_empty_rows":

                result = df.dropna(how="all").copy()



                details = "Completely empty rows removed."



            elif operation == "remove_empty_columns":

                result = df.dropna(

                    axis=1,

                    how="all",

                ).copy()



                details = "Completely empty columns removed."



            elif operation == "drop_missing_rows":

                result = df.dropna(

                    subset=cols or None

                ).copy()



                details = "Rows with missing values removed."



            elif operation == "remove_rows_condition":



                if len(cols) != 1:

                    raise ValueError(

                        "Select exactly one column for conditional removal."

                    )



                if ":" not in val:

                    raise ValueError(

                        "Enter condition like contains:abc or >:100"

                    )



                op, target = val.split(":", 1)

                s = df[cols[0]]



                if op == "contains":

                    mask = s.astype(str).str.contains(

                        target,

                        case=False,

                        na=False,

                    )



                elif op == "=":

                    mask = s.astype(str) == target



                elif op == "!=":

                    mask = s.astype(str) != target



                elif op in {">", "<", ">=", "<="}:

                    numeric = pd.to_numeric(

                        s,

                        errors="coerce",

                    )



                    t = float(target)



                    comparisons = {

                        ">": numeric > t,

                        "<": numeric < t,

                        ">=": numeric >= t,

                        "<=": numeric <= t,

                    }



                    mask = comparisons[op]



                else:

                    raise ValueError(

                        "Supported operators: =, !=, contains, >, <, >=, <="

                    )



                result = df.loc[~mask].copy()



                details = (

                    f"Rows matching {op}:{target} removed."

                )



            elif operation == "sort_rows":



                if len(cols) != 1:

                    raise ValueError(

                        "Select one column to sort."

                    )



                result = df.sort_values(

                    cols[0],

                    ascending=val.lower() != "descending",

                    na_position="last",

                ).copy()



                details = (

                    f"Sorted by {cols[0]} "

                    f"({val or 'ascending'})."

                )



            elif operation == "standardize_column_names":



                new_names = [

                    re.sub(

                        r"[^a-zA-Z0-9]+",

                        "_",

                        str(c).strip(),

                    ).strip("_").lower()

                    for c in result.columns

                ]



                if len(set(new_names)) != len(new_names):

                    raise ValueError(

                        "Standardized names would create duplicates. "

                        "Rename columns manually."

                    )



                result.columns = new_names



                details = (

                    "Column names standardized to snake_case."

                )



        # -----------------------------------------------------

        # COLUMN-BASED OPERATIONS

        # -----------------------------------------------------



        else:



            if not cols:

                raise ValueError(

                    "Select at least one column."

                )



            # REMOVE COLUMNS / MISSING ROWS

            if operation in {

                "remove_column",

                "remove_missing_column",

            }:



                if operation == "remove_column":

                    result = df.drop(

                        columns=cols

                    ).copy()



                    details = (

                        f"Removed {len(cols)} column(s)."

                    )



                else:

                    result = df.dropna(

                        subset=cols

                    ).copy()



                    details = (

                        "Rows missing selected values removed."

                    )



            # RENAME COLUMN

            elif operation == "rename_column":



                if len(cols) != 1:

                    raise ValueError(

                        "Select exactly one column to rename."

                    )



                if not val.strip():

                    raise ValueError(

                        "Enter a new column name."

                    )



                if (

                    val in df.columns

                    and val != cols[0]

                ):

                    raise ValueError(

                        "That column name already exists."

                    )



                result = df.rename(

                    columns={cols[0]: val.strip()}

                ).copy()



                details = (

                    f"Renamed {cols[0]} to {val.strip()}."

                )



            # REORDER COLUMN

            elif operation == "reorder_column":



                if len(cols) != 1:

                    raise ValueError(

                        "Select one column to move."

                    )



                try:

                    position = int(val)



                except ValueError:

                    raise ValueError(

                        "Enter the new position (starting from 1)."

                    )



                if position < 1 or position > len(df.columns):

                    raise ValueError(

                        f"Position must be between 1 and {len(df.columns)}."

                    )



                ordered = list(df.columns)



                ordered.remove(cols[0])

                ordered.insert(position - 1, cols[0])



                result = df[ordered].copy()



                details = (

                    f"Moved {cols[0]} to position {position}."

                )



            # -------------------------------------------------

            # MISSING VALUE OPERATIONS

            # -------------------------------------------------



            elif operation in {

                "fill_missing_value",

                "fill_missing_mean",

                "fill_missing_median",

                "fill_missing_mode",

                "forward_fill",

                "backward_fill",

            }:



                for c in cols:

                    s = result[c]



                    if operation == "fill_missing_value":



                        replacement = val



                        if pd.api.types.is_numeric_dtype(s):

                            try:

                                replacement = float(val)



                                if replacement.is_integer():

                                    replacement = int(replacement)



                            except ValueError:

                                pass



                        result[c] = s.fillna(replacement)



                    elif operation == "fill_missing_mean":



                        if not pd.api.types.is_numeric_dtype(s):

                            raise ValueError(

                                f"Mean requires numeric column: {c}"

                            )



                        result[c] = s.fillna(s.mean())



                    elif operation == "fill_missing_median":



                        if not pd.api.types.is_numeric_dtype(s):

                            raise ValueError(

                                f"Median requires numeric column: {c}"

                            )



                        result[c] = s.fillna(s.median())



                    elif operation == "fill_missing_mode":



                        modes = s.mode(dropna=True)



                        if not modes.empty:

                            result[c] = s.fillna(modes.iloc[0])



                    elif operation == "forward_fill":

                        result[c] = s.ffill()



                    elif operation == "backward_fill":

                        result[c] = s.bfill()



                details = (

                    f"Missing values handled in {len(cols)} column(s)."

                )



            # -------------------------------------------------

            # TEXT CLEANING OPERATIONS

            # -------------------------------------------------



            elif operation in self.TEXT_OPERATIONS:



                for c in cols:

                    s = result[c]



                    if operation == "trim_spaces":

                        fn = str.strip



                    elif operation == "remove_extra_spaces":

                        fn = lambda x: re.sub(

                            r"\s+",

                            " ",

                            x,

                        ).strip()



                    elif operation == "uppercase":

                        fn = str.upper



                    elif operation == "lowercase":

                        fn = str.lower



                    elif operation == "proper_case":

                        fn = str.title



                    elif operation == "remove_special_chars":

                        fn = lambda x: re.sub(

                            r"[^\w\s.-]",

                            "",

                            x,

                        )



                    elif operation == "remove_numbers":

                        fn = lambda x: re.sub(

                            r"\d+",

                            "",

                            x,

                        )



                    elif operation == "remove_letters":

                        fn = lambda x: re.sub(

                            r"[A-Za-z]+",

                            "",

                            x,

                        )



                    elif operation == "find_replace":



                        if "|" not in val:

                            raise ValueError(

                                "Enter find and replace separated by |, "

                                "e.g. old|new"

                            )



                        old, new = val.split("|", 1)



                        fn = lambda x: x.replace(old, new)



                    elif operation == "standardize_categories":

                        fn = lambda x: re.sub(

                            r"\s+",

                            " ",

                            x,

                        ).strip().title()



                    elif operation == "remove_currency_symbols":

                        fn = lambda x: re.sub(

                            r"[₹$€£¥]",

                            "",

                            x,

                        ).strip()



                    else:

                        fn = lambda x: x.replace(",", "")



                    result[c] = self._text_map(s, fn)



                details = (

                    f"{operation.replace('_', ' ').title()} "

                    f"applied to {len(cols)} column(s)."

                )



            # -------------------------------------------------

            # NUMBERS, DATE AND DATA TYPE OPERATIONS

            # -------------------------------------------------



            elif operation in {

                "convert_numeric",

                "convert_datetime",

                "round_numbers",

                "extract_year",

                "extract_month",

                "extract_day",

                "extract_day_name",

                "calculate_experience",

                "change_to_string",

                "change_to_integer",

                "change_to_float",

                "remove_outliers",

            }:



                for c in cols:

                    s = result[c]



                    if operation == "calculate_experience":
                        end_date_value = kwargs.get("end_date") or None
                        if end_date_value:
                            end_date = pd.to_datetime(
                                end_date_value, errors="coerce", dayfirst=False
                            )
                            if pd.isna(end_date):
                                raise ValueError("Enter End Date in YYYY-MM-DD format.")
                        else:
                            end_date = pd.Timestamp.today().normalize()

                        output_format = val or "Years + Months"
                        parsed_dates = self._parse_date_column(s)
                        result[f"{c}_experience"] = parsed_dates.map(
                            lambda item: self._format_experience(
                                item, end_date, output_format
                            )
                        )

                    elif operation == "convert_numeric":



                        cleaned = (

                            s.astype("string")

                            .str.replace(",", "", regex=False)

                            .str.replace(

                                r"[₹$€£¥]",

                                "",

                                regex=True,

                            )

                            .str.strip()

                        )



                        result[c] = pd.to_numeric(

                            cleaned,

                            errors="coerce",

                        )



                    elif operation == "convert_datetime":



                        result[c] = self._parse_date_column(s)



                    elif operation == "round_numbers":



                        try:

                            digits = int(val or 0)



                        except ValueError:

                            raise ValueError(

                                "Enter a valid number of decimal places."

                            )



                        if not pd.api.types.is_numeric_dtype(s):

                            raise ValueError(

                                f"Round requires numeric column: {c}"

                            )



                        result[c] = s.round(digits)



                    # DATE EXTRACTION

                    elif operation in self.DATE_OPERATIONS:



                        dt = self._parse_date_column(s)



                        if operation == "extract_year":



                            result[f"{c}_year"] = (

                                dt.dt.year.astype("Int64")

                            )



                        elif operation == "extract_month":



                            result[f"{c}_month"] = (

                                dt.dt.month.astype("Int64")

                            )



                        elif operation == "extract_day":



                            result[f"{c}_day"] = (

                                dt.dt.day.astype("Int64")

                            )



                        elif operation == "extract_day_name":



                            result[f"{c}_day_name"] = (

                                dt.dt.day_name()

                                .astype("string")

                            )



                        details = (

                            f"Extracted {operation.replace('extract_', '')} "

                            f"from {c}."

                        )



                    elif operation == "change_to_string":



                        result[c] = s.astype("string")



                    elif operation == "change_to_integer":



                        result[c] = (

                            pd.to_numeric(

                                s,

                                errors="coerce",

                            )

                            .round()

                            .astype("Int64")

                        )



                    elif operation == "change_to_float":



                        result[c] = pd.to_numeric(

                            s,

                            errors="coerce",

                        ).astype("float64")



                    elif operation == "remove_outliers":



                        numeric = pd.to_numeric(

                            s,

                            errors="coerce",

                        )



                        q1 = numeric.quantile(0.25)

                        q3 = numeric.quantile(0.75)



                        iqr = q3 - q1



                        mask = (

                            (numeric < q1 - 1.5 * iqr)

                            | (numeric > q3 + 1.5 * iqr)

                        )



                        result = result.loc[

                            ~mask.fillna(False)

                        ].copy()



                if operation not in self.DATE_OPERATIONS:

                    details = (

                        f"Applied {operation.replace('_', ' ')} "

                        f"to selected columns."

                    )



            # -------------------------------------------------

            # REPLACE NEGATIVE VALUES

            # -------------------------------------------------



            elif operation == "replace_negative":



                for c in cols:

                    numeric = pd.to_numeric(

                        result[c],

                        errors="coerce",

                    )



                    replacement = float(val or 0)



                    result.loc[

                        numeric < 0,

                        c,

                    ] = replacement



                details = "Negative numeric values replaced."



            # -------------------------------------------------

            # SPLIT COLUMN

            # -------------------------------------------------



            elif operation == "split_column":



                if len(cols) != 1:

                    raise ValueError(

                        "Select one column to split."

                    )



                delimiter = val if val else ","



                split = (

                    result[cols[0]]

                    .astype("string")

                    .str.split(delimiter, expand=True)

                )



                for i in range(split.shape[1]):

                    new_column = f"{cols[0]}_{i + 1}"



                    if new_column in result.columns:

                        raise ValueError(

                            f"Column {new_column} already exists."

                        )



                    result[new_column] = split[i]



                details = (

                    f"Split {cols[0]} using '{delimiter}'."

                )



            # -------------------------------------------------

            # COMBINE COLUMNS

            # -------------------------------------------------



            elif operation == "combine_columns":



                if len(cols) < 2:

                    raise ValueError(

                        "Select at least two columns to combine."

                    )



                name = val.strip() or "Combined Column"



                if name in result.columns:

                    raise ValueError(

                        f"Column '{name}' already exists."

                    )



                result[name] = (

                    result[cols]

                    .fillna("")

                    .astype(str)

                    .agg(" ".join, axis=1)

                    .str.strip()

                )



                details = (

                    f"Combined {len(cols)} columns into {name}."

                )



            else:

                raise ValueError(

                    f"Unsupported operation: {operation}"

                )



        # -----------------------------------------------------

        # SAVE CHANGES FOR UNDO / HISTORY

        # -----------------------------------------------------



        if not result.equals(self.working_dataframe):



            self.undo_stack.append(

                self.working_dataframe.copy(deep=True)

            )



            self.redo_stack.clear()



            self.working_dataframe = result.copy(deep=True)



            self._record(

                operation,

                cols,

                df,

                result,

                details,

            )



        return self.get_dataframe()



    # ---------------------------------------------------------

    # UNDO

    # ---------------------------------------------------------



    def undo(self):



        if not self.undo_stack:

            return self.get_dataframe()



        current = self.working_dataframe.copy(deep=True)



        self.redo_stack.append(current)



        self.working_dataframe = self.undo_stack.pop()



        self.history.append(

            self._history_action(

                "Undo",

                current,

                self.working_dataframe,

                "Previous state restored.",

                "Undone",

            )

        )



        return self.get_dataframe()



    # ---------------------------------------------------------

    # REDO

    # ---------------------------------------------------------



    def redo(self):



        if not self.redo_stack:

            return self.get_dataframe()



        current = self.working_dataframe.copy(deep=True)



        self.undo_stack.append(current)



        self.working_dataframe = self.redo_stack.pop()



        self.history.append(

            self._history_action(

                "Redo",

                current,

                self.working_dataframe,

                "Undone state restored.",

                "Restored",

            )

        )



        return self.get_dataframe()



    # ---------------------------------------------------------

    # RESET ORIGINAL DATA

    # ---------------------------------------------------------



    def reset(self):



        if self.original_dataframe is None:

            return None



        before = self.working_dataframe.copy(deep=True)



        self.undo_stack.append(before)

        self.redo_stack.clear()



        self.working_dataframe = (

            self.original_dataframe.copy(deep=True)

        )



        self.history.append(

            self._history_action(

                "Reset Original",

                before,

                self.working_dataframe,

                "Original imported dataset restored.",

                "Applied",

            )

        )



        return self.get_dataframe()



    # ---------------------------------------------------------

    # DATA QUALITY STATISTICS

    # ---------------------------------------------------------



    def get_statistics(self):



        if self.working_dataframe is None:

            return {}



        df = self.working_dataframe



        return {

            "rows": len(df),

            "columns": len(df.columns),

            "missing_values": int(

                df.isna().sum().sum()

            ),

            "duplicate_rows": int(

                df.duplicated().sum()

            ),

            "empty_rows": int(

                df.isna().all(axis=1).sum()

            ),

        }



    # ---------------------------------------------------------

    # ORIGINAL VS CLEANED COMPARISON

    # ---------------------------------------------------------



    def get_comparison(self):



        if (

            self.original_dataframe is None

            or self.working_dataframe is None

        ):

            return {}



        original = self.original_dataframe

        cleaned = self.working_dataframe



        return {

            "original_rows": len(original),

            "cleaned_rows": len(cleaned),



            "original_columns": len(original.columns),

            "cleaned_columns": len(cleaned.columns),



            "original_missing": int(

                original.isna().sum().sum()

            ),



            "cleaned_missing": int(

                cleaned.isna().sum().sum()

            ),



            "original_duplicates": int(

                original.duplicated().sum()

            ),



            "cleaned_duplicates": int(

                cleaned.duplicated().sum()

            ),

        }
