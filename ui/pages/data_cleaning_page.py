"""DashEasy Data Cleaning page - categorized cleaning tools with preview/history."""



import pandas as pd



from PySide6.QtCore import Signal, Qt

from PySide6.QtWidgets import (

    QWidget,

    QVBoxLayout,

    QHBoxLayout,

    QGridLayout,

    QLabel,

    QPushButton,

    QComboBox,

    QLineEdit,

    QFrame,

    QTableWidget,

    QTableWidgetItem,

    QMessageBox,

    QListWidget,

    QListWidgetItem,

    QSplitter,

    QHeaderView,

    QScrollArea,

)



from core.cleaning.cleaning_engine import CleaningEngine





class CleaningPage(QWidget):

    data_applied = Signal(object)



    CATEGORIES = {

        "Remove Data": {

            "Remove Duplicate Rows": "remove_duplicates",

            "Remove Duplicate Columns": "remove_duplicate_columns",

            "Remove Completely Empty Rows": "remove_empty_rows",

            "Remove Completely Empty Columns": "remove_empty_columns",

            "Remove Rows with Missing Values": "drop_missing_rows",

            "Remove Rows Missing in Selected Column": "remove_missing_column",

            "Remove Selected Column(s)": "remove_column",

            "Remove Rows by Condition": "remove_rows_condition",

            "Sort Rows by Column": "sort_rows",

        },



        "Missing Values": {

            "Fill Missing with Custom Value": "fill_missing_value",

            "Fill Missing with Mean": "fill_missing_mean",

            "Fill Missing with Median": "fill_missing_median",

            "Fill Missing with Mode": "fill_missing_mode",

            "Forward Fill": "forward_fill",

            "Backward Fill": "backward_fill",

        },



        "Text Cleaning": {

            "Trim Extra Spaces": "trim_spaces",

            "Remove Extra Spaces Between Words": "remove_extra_spaces",

            "Convert to UPPERCASE": "uppercase",

            "Convert to lowercase": "lowercase",

            "Convert to Proper Case": "proper_case",

            "Remove Special Characters": "remove_special_chars",

            "Remove Numbers from Text": "remove_numbers",

            "Remove Letters from Text": "remove_letters",

            "Find & Replace Text": "find_replace",

            "Standardize Categories": "standardize_categories",

            "Remove Currency Symbols": "remove_currency_symbols",

            "Remove Commas": "remove_commas",

        },



        "Numbers & Data Types": {

            "Convert to Numeric": "convert_numeric",

            "Round Numbers": "round_numbers",

            "Replace Negative Values": "replace_negative",

            "Remove Numeric Outliers (IQR)": "remove_outliers",

            "Convert to String": "change_to_string",

            "Convert to Integer": "change_to_integer",

            "Convert to Float": "change_to_float",

        },



        "Date & Time": {

            "Convert to Date/Time": "convert_datetime",

            "Extract Year": "extract_year",

            "Extract Month": "extract_month",

            "Extract Day": "extract_day",

            "Extract Day Name": "extract_day_name",
            "Calculate Experience": "calculate_experience",

        },



        "Columns & Formatting": {

            "Rename Selected Column": "rename_column",

            "Reorder Column": "reorder_column",

            "Standardize Column Names": "standardize_column_names",

            "Split Column by Delimiter": "split_column",

            "Combine Selected Columns": "combine_columns",

        },

    }



    VALUE_HINTS = {

        "fill_missing_value": "Enter replacement value...",

        "rename_column": "Enter new column name...",

        "remove_rows_condition": "Condition: contains:abc or =:value or >:100",

        "sort_rows": "ascending or descending",

        "round_numbers": "Decimal places (e.g. 2)",

        "replace_negative": "Replacement number (default 0)",

        "split_column": "Delimiter (default comma)",

        "combine_columns": "New column name (optional)",

        "reorder_column": "New position (starts at 1)",

    }



    def __init__(self):

        super().__init__()



        self.engine = CleaningEngine()

        self.setup_ui()



    # ---------------------------------------------------------

    # UI SETUP

    # ---------------------------------------------------------



    def setup_ui(self):

        outer_layout = QVBoxLayout(self)

        outer_layout.setContentsMargins(0, 0, 0, 0)



        scroll_area = QScrollArea()

        scroll_area.setWidgetResizable(True)

        scroll_area.setFrameShape(QFrame.Shape.NoFrame)



        content_widget = QWidget()



        main_layout = QVBoxLayout(content_widget)

        main_layout.setContentsMargins(28, 24, 28, 24)

        main_layout.setSpacing(12)



        # Page heading

        title = QLabel("Data Cleaning")

        title.setObjectName("pageTitle")



        subtitle = QLabel(

            "Clean, standardize and validate your dataset "

            "with guided operations."

        )

        subtitle.setObjectName("pageSubtitle")



        main_layout.addWidget(title)

        main_layout.addWidget(subtitle)



        # -----------------------------------------------------

        # DATA QUALITY CARDS

        # -----------------------------------------------------



        stats_layout = QGridLayout()



        self.rows_label = QLabel("0")

        self.columns_label = QLabel("0")

        self.missing_label = QLabel("0")

        self.duplicates_label = QLabel("0")



        cards = [

            ("Total Rows", self.rows_label),

            ("Total Columns", self.columns_label),

            ("Missing Values", self.missing_label),

            ("Duplicate Rows", self.duplicates_label),

        ]



        for index, (heading, value_label) in enumerate(cards):

            card = QFrame()

            card.setObjectName("welcomeCard")



            card_layout = QVBoxLayout(card)



            heading_label = QLabel(heading)

            heading_label.setObjectName("pageSubtitle")



            value_label.setObjectName("welcomeTitle")



            card_layout.addWidget(heading_label)

            card_layout.addWidget(value_label)



            stats_layout.addWidget(card, 0, index)



        main_layout.addLayout(stats_layout)



        # -----------------------------------------------------

        # CLEANING OPERATIONS CARD

        # -----------------------------------------------------



        cleaning_card = QFrame()

        cleaning_card.setObjectName("welcomeCard")



        cleaning_layout = QVBoxLayout(cleaning_card)

        cleaning_layout.setContentsMargins(14, 14, 14, 14)

        cleaning_layout.setSpacing(10)



        heading = QLabel("Cleaning Operations")

        heading.setObjectName("welcomeTitle")



        cleaning_layout.addWidget(heading)



        # Category and operation selection

        selection_layout = QHBoxLayout()



        selection_layout.addWidget(QLabel("Category:"))



        self.category_combo = QComboBox()

        self.category_combo.addItems(list(self.CATEGORIES.keys()))



        self.category_combo.currentTextChanged.connect(

            self.populate_operations

        )



        selection_layout.addWidget(self.category_combo, 1)



        selection_layout.addWidget(QLabel("Operation:"))



        self.operation_combo = QComboBox()



        self.operation_combo.currentTextChanged.connect(

            self.update_input_visibility

        )



        selection_layout.addWidget(self.operation_combo, 2)



        cleaning_layout.addLayout(selection_layout)



        # Column selection

        column_layout = QHBoxLayout()



        column_layout.addWidget(QLabel("Select Column(s):"))



        self.column_list = QListWidget()

        self.column_list.setMinimumHeight(100)

        self.column_list.setMaximumHeight(115)



        column_layout.addWidget(self.column_list, 1)



        self.select_all_button = QPushButton("Select All")

        self.select_all_button.clicked.connect(

            self.select_all_columns

        )



        column_layout.addWidget(self.select_all_button)



        self.clear_selection_button = QPushButton("Clear")

        self.clear_selection_button.clicked.connect(

            self.clear_column_selection

        )



        column_layout.addWidget(self.clear_selection_button)



        cleaning_layout.addLayout(column_layout)



        # General value input

        self.value_input = QLineEdit()

        self.value_input.setMinimumHeight(36)

        self.value_input.setPlaceholderText("Enter value...")

        cleaning_layout.addWidget(self.value_input)



        # -----------------------------------------------------

        # FIND AND REPLACE INPUTS

        # -----------------------------------------------------



        self.find_input = QLineEdit()

        self.find_input.setMinimumHeight(36)

        self.find_input.setPlaceholderText(

            "Find Text - Enter the text you want to search..."

        )



        cleaning_layout.addWidget(self.find_input)



        self.replace_input = QLineEdit()

        self.replace_input.setMinimumHeight(36)

        self.replace_input.setPlaceholderText(

            "Replace With - Enter replacement text..."

        )



        cleaning_layout.addWidget(self.replace_input)

        self.experience_format_combo = QComboBox()
        self.experience_format_combo.addItems([
            "Years", "Years + Months", "Total Months",
            "Years + Months + Days"
        ])
        self.experience_end_date_input = QLineEdit()
        self.experience_end_date_input.setPlaceholderText(
            "End Date (YYYY-MM-DD), leave blank for today"
        )
        cleaning_layout.addWidget(self.experience_format_combo)
        cleaning_layout.addWidget(self.experience_end_date_input)

        # Apply operation button

        self.apply_operation_button = QPushButton(

            "Apply Cleaning Operation"

        )



        self.apply_operation_button.setObjectName("primaryButton")



        self.apply_operation_button.clicked.connect(

            self.apply_operation

        )



        cleaning_layout.addWidget(self.apply_operation_button)



        main_layout.addWidget(cleaning_card)



        # -----------------------------------------------------

        # UNDO / REDO / RESET / APPLY

        # -----------------------------------------------------



        actions_layout = QHBoxLayout()



        self.undo_button = QPushButton("Undo")

        self.undo_button.clicked.connect(self.undo)

        actions_layout.addWidget(self.undo_button)



        self.redo_button = QPushButton("Redo")

        self.redo_button.clicked.connect(self.redo)

        actions_layout.addWidget(self.redo_button)



        self.reset_button = QPushButton("Reset Original")

        self.reset_button.clicked.connect(self.reset_data)

        actions_layout.addWidget(self.reset_button)



        actions_layout.addStretch()



        self.apply_changes_button = QPushButton("Apply Changes")

        self.apply_changes_button.setObjectName("primaryButton")

        self.apply_changes_button.clicked.connect(self.apply_changes)



        actions_layout.addWidget(self.apply_changes_button)



        main_layout.addLayout(actions_layout)



        # -----------------------------------------------------

        # BEFORE AND AFTER COMPARISON

        # -----------------------------------------------------



        comparison_card = QFrame()

        comparison_card.setObjectName("welcomeCard")



        comparison_layout = QVBoxLayout(comparison_card)



        comparison_heading = QLabel("Before vs After Comparison")

        comparison_heading.setObjectName("sectionTitle")



        comparison_layout.addWidget(comparison_heading)



        self.comparison_label = QLabel(

            "Import a dataset to compare original and cleaned data."

        )



        self.comparison_label.setWordWrap(True)



        comparison_layout.addWidget(self.comparison_label)



        main_layout.addWidget(comparison_card)



        # -----------------------------------------------------

        # PREVIEW AND HISTORY

        # -----------------------------------------------------



        splitter = QSplitter(Qt.Orientation.Vertical)



        preview_widget = QWidget()

        preview_layout = QVBoxLayout(preview_widget)



        preview_heading = QLabel(

            "Cleaned Data Preview (First 100 Rows)"

        )



        preview_layout.addWidget(preview_heading)



        self.table = QTableWidget()

        self.table.setAlternatingRowColors(True)



        self.table.setEditTriggers(

            QTableWidget.EditTrigger.NoEditTriggers

        )



        self.table.setSelectionBehavior(

            QTableWidget.SelectionBehavior.SelectRows

        )



        self.table.horizontalHeader().setStretchLastSection(True)



        preview_layout.addWidget(self.table)



        history_widget = QWidget()

        history_layout = QVBoxLayout(history_widget)



        history_heading = QLabel("Cleaning Operation History")

        history_layout.addWidget(history_heading)



        self.history_table = QTableWidget()



        self.history_table.setColumnCount(6)



        self.history_table.setHorizontalHeaderLabels([

            "Time",

            "Operation",

            "Column",

            "Rows Before",

            "Rows After",

            "Status",

        ])



        self.history_table.setEditTriggers(

            QTableWidget.EditTrigger.NoEditTriggers

        )



        self.history_table.setAlternatingRowColors(True)



        self.history_table.horizontalHeader().setSectionResizeMode(

            QHeaderView.ResizeMode.ResizeToContents

        )



        self.history_table.horizontalHeader().setStretchLastSection(

            True

        )



        history_layout.addWidget(self.history_table)



        preview_widget.setMinimumHeight(260)

        history_widget.setMinimumHeight(190)



        splitter.addWidget(preview_widget)

        splitter.addWidget(history_widget)



        splitter.setChildrenCollapsible(False)

        splitter.setMinimumHeight(470)

        splitter.setSizes([290, 180])



        main_layout.addWidget(splitter)



        # Status

        self.status_label = QLabel(

            "Import a dataset to start cleaning."

        )



        self.status_label.setObjectName("pageSubtitle")



        main_layout.addWidget(self.status_label)



        scroll_area.setWidget(content_widget)

        outer_layout.addWidget(scroll_area)



        self.populate_operations()

        self.update_buttons()



    # ---------------------------------------------------------

    # CATEGORY AND INPUT CONTROLS

    # ---------------------------------------------------------



    def populate_operations(self, *_):

        self.operation_combo.clear()



        category = self.category_combo.currentText()



        operations = self.CATEGORIES.get(category, {})



        self.operation_combo.addItems(list(operations.keys()))



        self.update_input_visibility()



    def update_input_visibility(self, *_):

        category = self.category_combo.currentText()



        operation = self.CATEGORIES.get(category, {}).get(

            self.operation_combo.currentText()

        )



        is_find_replace = operation == "find_replace"
        is_experience = operation == "calculate_experience"

        self.find_input.setVisible(is_find_replace)

        self.replace_input.setVisible(is_find_replace)
        self.experience_format_combo.setVisible(is_experience)
        self.experience_end_date_input.setVisible(is_experience)

        hint = self.VALUE_HINTS.get(operation, "")



        self.value_input.setVisible(

            bool(hint) and not is_find_replace

        )



        self.value_input.setPlaceholderText(hint)



    # ---------------------------------------------------------

    # DATAFRAME AND COLUMN SELECTION

    # ---------------------------------------------------------



    def set_dataframe(self, dataframe):

        if isinstance(dataframe, pd.DataFrame):

            self.engine.set_dataframe(dataframe)

        else:

            self.engine.set_dataframe(pd.DataFrame())



        self.refresh_columns()

        self.refresh_view()



        self.status_label.setText(

            "Dataset loaded. Ready for cleaning."

        )



    def selected_columns(self):

        selected = []



        for index in range(self.column_list.count()):

            item = self.column_list.item(index)



            if item.checkState() == Qt.CheckState.Checked:

                selected.append(item.text())



        return selected



    def refresh_columns(self):

        self.column_list.clear()



        dataframe = self.engine.get_dataframe()



        if dataframe is not None:

            for column in dataframe.columns:

                item = QListWidgetItem(str(column))



                item.setFlags(

                    item.flags()

                    | Qt.ItemFlag.ItemIsUserCheckable

                )



                item.setCheckState(Qt.CheckState.Unchecked)



                self.column_list.addItem(item)



        self.update_buttons()



    def select_all_columns(self):

        for index in range(self.column_list.count()):

            self.column_list.item(index).setCheckState(

                Qt.CheckState.Checked

            )



    def clear_column_selection(self):

        for index in range(self.column_list.count()):

            self.column_list.item(index).setCheckState(

                Qt.CheckState.Unchecked

            )



    # ---------------------------------------------------------

    # APPLY CLEANING OPERATION

    # ---------------------------------------------------------



    def apply_operation(self):

        if self.engine.working_dataframe is None:

            QMessageBox.warning(

                self,

                "No Dataset",

                "Please import a dataset first.",

            )

            return



        category = self.category_combo.currentText()



        operation_name = self.operation_combo.currentText()



        operation = self.CATEGORIES[category][operation_name]



        columns = self.selected_columns()



        value = self.value_input.text()



        # Find & Replace

        if operation == "find_replace":

            find_text = self.find_input.text()

            replace_text = self.replace_input.text()



            if not find_text:

                QMessageBox.warning(

                    self,

                    "Find Text Required",

                    "Please enter the text you want to find.",

                )

                self.find_input.setFocus()

                return



            if "|" in find_text or "|" in replace_text:

                QMessageBox.warning(

                    self,

                    "Invalid Character",

                    "The | character cannot be used in these fields.",

                )

                return



            value = f"{find_text}|{replace_text}"



        # Operations that do not require selected columns

        dataset_operations = {

            "remove_duplicates",

            "remove_duplicate_columns",

            "remove_empty_rows",

            "remove_empty_columns",

            "drop_missing_rows",

            "standardize_column_names",

        }



        if operation == "calculate_experience" and len(columns) != 1:
            QMessageBox.warning(
                self,
                "Select One Column",
                "Please select exactly one Joining Date column.",
            )
            return

        if operation not in dataset_operations and not columns:

            QMessageBox.warning(

                self,

                "Select Column",

                "Please tick at least one column for this operation.",

            )

            return



        # Operations requiring exactly one column

        single_column_operations = {

            "rename_column",

            "reorder_column",

            "remove_rows_condition",

            "split_column",

        }



        if operation in single_column_operations and len(columns) != 1:

            QMessageBox.warning(

                self,

                "Select One Column",

                "Please select exactly one column.",

            )

            return



        if operation == "combine_columns" and len(columns) < 2:

            QMessageBox.warning(

                self,

                "Select Columns",

                "Please select at least two columns.",

            )

            return



        # Required value checks

        required_value_operations = {

            "fill_missing_value",

            "rename_column",

            "remove_rows_condition",

        }



        if operation in required_value_operations and not value.strip():

            QMessageBox.warning(

                self,

                "Input Required",

                "Please enter the required value.",

            )

            return



        try:

            self.engine.apply(

                operation,

                column=columns or None,

                value=(
                    self.experience_format_combo.currentText()
                    if operation == "calculate_experience"
                    else value
                ),
                end_date=self.experience_end_date_input.text().strip()
                if operation == "calculate_experience"
                else None,

            )



            self.value_input.clear()

            self.find_input.clear()

            self.replace_input.clear()



            self.refresh_columns()

            self.refresh_view()



            self.status_label.setText(

                f"Applied: {operation_name}"

            )



        except Exception as error:

            QMessageBox.warning(

                self,

                "Cleaning Error",

                str(error),

            )



            self.status_label.setText(

                "Cleaning operation could not be completed."

            )



    # ---------------------------------------------------------

    # REFRESH DATA PREVIEW

    # ---------------------------------------------------------



    def refresh_view(self):

        dataframe = self.engine.get_dataframe()



        if dataframe is None:

            return



        stats = self.engine.get_statistics()



        self.rows_label.setText(

            f"{stats['rows']:,}"

        )



        self.columns_label.setText(

            f"{stats['columns']:,}"

        )



        self.missing_label.setText(

            f"{stats['missing_values']:,}"

        )



        self.duplicates_label.setText(

            f"{stats['duplicate_rows']:,}"

        )



        preview = dataframe.head(100)



        self.table.clear()



        self.table.setRowCount(len(preview))

        self.table.setColumnCount(len(preview.columns))



        self.table.setHorizontalHeaderLabels(

            [str(column) for column in preview.columns]

        )



        for row_index, row in enumerate(

            preview.itertuples(index=False, name=None)

        ):

            for column_index, value in enumerate(row):

                display_value = (

                    ""

                    if pd.isna(value)

                    else str(value)

                )



                self.table.setItem(

                    row_index,

                    column_index,

                    QTableWidgetItem(display_value),

                )



        self.table.resizeColumnsToContents()



        self.refresh_comparison()

        self.refresh_history()

        self.update_buttons()



    # ---------------------------------------------------------

    # COMPARISON

    # ---------------------------------------------------------



    def refresh_comparison(self):

        comparison = self.engine.get_comparison()



        if not comparison:

            self.comparison_label.setText(

                "Import a dataset to compare original and cleaned data."

            )

            return



        self.comparison_label.setText(

            "ORIGINAL | "

            f"Rows: {comparison['original_rows']:,} | "

            f"Columns: {comparison['original_columns']:,} | "

            f"Missing: {comparison['original_missing']:,} | "

            f"Duplicates: {comparison['original_duplicates']:,}\n"

            "CLEANED | "

            f"Rows: {comparison['cleaned_rows']:,} | "

            f"Columns: {comparison['cleaned_columns']:,} | "

            f"Missing: {comparison['cleaned_missing']:,} | "

            f"Duplicates: {comparison['cleaned_duplicates']:,}"

        )



    # ---------------------------------------------------------

    # OPERATION HISTORY

    # ---------------------------------------------------------



    def refresh_history(self):

        history = self.engine.get_history()



        self.history_table.setRowCount(len(history))



        for row_index, record in enumerate(history):

            values = [

                record.get("time", ""),

                record.get("operation", ""),

                record.get("column", ""),

                str(record.get("rows_before", "")),

                str(record.get("rows_after", "")),

                record.get("status", ""),

            ]



            for column_index, value in enumerate(values):

                self.history_table.setItem(

                    row_index,

                    column_index,

                    QTableWidgetItem(str(value)),

                )



        self.history_table.scrollToBottom()



    # ---------------------------------------------------------

    # UNDO / REDO

    # ---------------------------------------------------------



    def undo(self):

        if not self.engine.undo_stack:

            return



        self.engine.undo()



        self.refresh_columns()

        self.refresh_view()



        self.status_label.setText(

            "Previous cleaning operation undone."

        )



    def redo(self):

        if not self.engine.redo_stack:

            return



        self.engine.redo()



        self.refresh_columns()

        self.refresh_view()



        self.status_label.setText(

            "Cleaning operation restored."

        )



    # ---------------------------------------------------------

    # RESET DATA

    # ---------------------------------------------------------



    def reset_data(self):

        if self.engine.original_dataframe is None:

            return



        answer = QMessageBox.question(

            self,

            "Reset Dataset",

            "Restore the original imported dataset?",

        )



        if answer == QMessageBox.StandardButton.Yes:

            self.engine.reset()



            self.refresh_columns()

            self.refresh_view()



            self.status_label.setText(

                "Original dataset restored."

            )



    # ---------------------------------------------------------

    # BUTTON STATES

    # ---------------------------------------------------------



    def update_buttons(self):

        has_data = (

            self.engine.working_dataframe is not None

        )



        self.undo_button.setEnabled(

            has_data and bool(self.engine.undo_stack)

        )



        self.redo_button.setEnabled(

            has_data and bool(self.engine.redo_stack)

        )



        self.apply_operation_button.setEnabled(has_data)



        self.reset_button.setEnabled(

            has_data

            and self.engine.original_dataframe is not None

        )



        self.apply_changes_button.setEnabled(has_data)



    # ---------------------------------------------------------

    # APPLY CLEANED DATA TO MAIN APPLICATION

    # ---------------------------------------------------------



    def apply_changes(self):

        dataframe = self.engine.get_dataframe()



        if dataframe is None:

            return



        answer = QMessageBox.question(

            self,

            "Apply Cleaning Changes",

            "Apply the cleaned dataset to DashEasy Data Preview?",

        )



        if answer == QMessageBox.StandardButton.Yes:

            self.data_applied.emit(dataframe)



            self.status_label.setText(

                "Cleaning changes applied successfully."

            )
