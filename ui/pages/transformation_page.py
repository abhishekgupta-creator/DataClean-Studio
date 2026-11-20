"""DashEasy - Data Transformation Page."""
import pandas as pd
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QComboBox, QLineEdit, QTableWidget, QTableWidgetItem,
    QMessageBox, QListWidget, QAbstractItemView, QFormLayout,
    QSizePolicy, QScrollArea, QHeaderView, QAbstractScrollArea,
    QListWidgetItem
)
from core.transformation import TransformationEngine, TransformationError


class TransformationPage(QWidget):
    """Interactive data transformation interface."""

    data_changed = Signal(object)

    OPERATIONS = [
        "Change Data Type",
        "Create New Column",
        "Calculate Experience",
        "Split Column",
        "Merge Columns",
        "Replace Values",
        "Sort Data",
        "Filter Rows",
        "Conditional Column",
        "Conditional Percentage Column",
    ]

    def __init__(self):
        super().__init__()
        self.original_df = None
        self.current_df = None
        self.undo_stack = []
        self.setup_ui()

    def setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        content.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred
        )

        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(28, 24, 28, 24)
        main_layout.setSpacing(16)

        scroll.setWidget(content)
        root_layout.addWidget(scroll)

        title = QLabel("Data Transformation")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Transform, calculate, filter and organize your data.")
        subtitle.setObjectName("pageSubtitle")
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        self.info_label = QLabel("No dataset loaded.")
        self.info_label.setObjectName("sectionTitle")
        main_layout.addWidget(self.info_label)

        card = QFrame()
        card.setObjectName("welcomeCard")
        card.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred
        )
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(22, 20, 22, 20)
        card_layout.setSpacing(16)

        heading = QLabel("Transformation Operations")
        heading.setObjectName("welcomeTitle")
        card_layout.addWidget(heading)

        self.operation_combo = QComboBox()
        self.operation_combo.addItems(self.OPERATIONS)

        self.column_combo = QComboBox()
        self.columns_list = QListWidget()
        self.columns_list.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
        )
        self.columns_list.setMinimumHeight(75)
        self.columns_list.setMaximumHeight(110)

        self.data_type_combo = QComboBox()
        self.data_type_combo.addItems(
            ["Text", "Integer", "Float", "Date", "Boolean"]
        )

        self.new_column_edit = QLineEdit()
        self.new_column_edit.setPlaceholderText("Enter new column name")

        self.calculation_mode_combo = QComboBox()
        self.calculation_mode_combo.addItems([
            "Fixed Value", "Percentage", "Another Column"
        ])

        self.calculation_combo = QComboBox()
        self.calculation_combo.addItems(
            ["Add", "Subtract", "Multiply", "Divide"]
        )

        self.second_column_combo = QComboBox()

        self.value_edit = QLineEdit()
        self.value_edit.setPlaceholderText("Enter numeric value")

        self.replacement_edit = QLineEdit()
        self.replacement_edit.setPlaceholderText("Enter replacement value")

        self.separator_edit = QLineEdit()
        self.separator_edit.setText(" ")

        self.split_names_edit = QLineEdit()
        self.split_names_edit.setPlaceholderText(
            "Example: First_Name, Last_Name"
        )

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Ascending", "Descending"])

        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "Equals", "Not Equals", "Contains", "Greater Than",
            "Less Than", "Greater Than or Equal",
            "Less Than or Equal", "Is Empty", "Is Not Empty"
        ])

        self.condition_combo = QComboBox()
        self.condition_combo.addItems([
            "Equals", "Not Equals", ">", "<", ">=", "<="
        ])

        self.true_value_edit = QLineEdit()
        self.true_value_edit.setPlaceholderText("Value if TRUE")

        self.false_value_edit = QLineEdit()
        self.false_value_edit.setPlaceholderText("Value if FALSE")

        self.conditional_threshold_edit = QLineEdit()
        self.conditional_threshold_edit.setPlaceholderText("e.g. 50000")

        self.conditional_true_percent_edit = QLineEdit()
        self.conditional_true_percent_edit.setPlaceholderText("e.g. 10%")

        self.conditional_false_percent_edit = QLineEdit()
        self.conditional_false_percent_edit.setPlaceholderText("e.g. 5% or 8%")

        self.experience_format_combo = QComboBox()
        self.experience_format_combo.addItems([
            "Years", "Years + Months", "Total Months",
            "Years + Months + Days"
        ])

        self.experience_end_date_edit = QLineEdit()
        self.experience_end_date_edit.setPlaceholderText(
            "YYYY-MM-DD (leave blank for today)"
        )

        form = QFormLayout()
        form.setSpacing(13)
        form.setContentsMargins(0, 4, 0, 4)
        form.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
        )
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        form.setLabelAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        self.form_fields = {}

        def add_field(key, label, widget):
            label_widget = QLabel(label)
            widget.setMinimumWidth(0)
            widget.setMaximumWidth(1000)
            widget.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Fixed
            )
            if isinstance(widget, QListWidget):
                widget.setSizePolicy(
                    QSizePolicy.Policy.Expanding,
                    QSizePolicy.Policy.Fixed
                )
            form.addRow(label_widget, widget)
            self.form_fields[key] = (label_widget, widget)

        add_field("operation", "Operation:", self.operation_combo)
        add_field("column", "Select Column:", self.column_combo)
        add_field("columns", "Select Multiple Columns:", self.columns_list)
        add_field("data_type", "New Data Type:", self.data_type_combo)
        add_field("calculation_mode", "Calculation Mode:", self.calculation_mode_combo)
        add_field("new_column", "New Column Name:", self.new_column_edit)
        add_field("calculation", "Calculation:", self.calculation_combo)
        add_field("second_column", "Second Column:", self.second_column_combo)
        add_field("value", "Value / Condition:", self.value_edit)
        add_field("replacement", "Replace With:", self.replacement_edit)
        add_field("separator", "Separator:", self.separator_edit)
        add_field("split_names", "Output Column Names:", self.split_names_edit)
        add_field("sort", "Sort Order:", self.sort_combo)
        add_field("filter", "Filter Condition:", self.filter_combo)
        add_field("condition", "IF Condition:", self.condition_combo)
        add_field("true_value", "If TRUE:", self.true_value_edit)
        add_field("false_value", "If FALSE:", self.false_value_edit)
        add_field("conditional_threshold", "Salary Threshold:", self.conditional_threshold_edit)
        add_field("conditional_true_percent", "Bonus % if condition TRUE:", self.conditional_true_percent_edit)
        add_field("conditional_false_percent", "Bonus % if condition FALSE:", self.conditional_false_percent_edit)
        add_field("experience_format", "Experience Format:", self.experience_format_combo)
        add_field("experience_end_date", "End Date:", self.experience_end_date_edit)

        card_layout.addLayout(form)

        self.apply_button = QPushButton("Apply Transformation")
        self.apply_button.setObjectName("primaryButton")
        self.apply_button.setMinimumHeight(44)
        self.apply_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.apply_button.clicked.connect(self.apply_transformation)
        card_layout.addWidget(self.apply_button)
        main_layout.addWidget(card)

        controls = QHBoxLayout()
        self.undo_button = QPushButton("Undo")
        self.undo_button.clicked.connect(self.undo)
        self.reset_button = QPushButton("Reset Original")
        self.reset_button.clicked.connect(self.reset_data)
        controls.addWidget(self.undo_button)
        controls.addWidget(self.reset_button)
        controls.addStretch()
        main_layout.addLayout(controls)

        preview_title = QLabel("Transformed Data Preview")
        preview_title.setObjectName("sectionTitle")
        main_layout.addWidget(preview_title)

        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.table.setSizeAdjustPolicy(
            QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored
        )
        self.table.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Interactive
        )
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.setMinimumHeight(280)
        main_layout.addWidget(self.table)

        self.status_label = QLabel("Load a dataset to start transforming.")
        self.status_label.setObjectName("pageSubtitle")
        main_layout.addWidget(self.status_label)

        self.operation_combo.currentTextChanged.connect(
            self.update_operation_fields
        )
        self.calculation_mode_combo.currentTextChanged.connect(
            self.update_operation_fields
        )

        self.update_operation_fields()
        self.update_buttons()

    def update_operation_fields(self):
        operation = self.operation_combo.currentText()
        mode = self.calculation_mode_combo.currentText()

        visible_fields = {
            "Change Data Type": ["column", "data_type"],
            "Create New Column": [
                "calculation_mode", "new_column", "calculation"
            ],
            "Calculate Experience": [
                "column", "new_column", "experience_format",
                "experience_end_date"
            ],
            "Split Column": ["column", "separator", "split_names"],
            "Merge Columns": ["columns", "new_column", "separator"],
            "Replace Values": ["column", "value", "replacement"],
            "Sort Data": ["column", "sort"],
            "Filter Rows": ["column", "filter", "value"],
            "Conditional Column": [
                "column", "new_column", "condition",
                "value", "true_value", "false_value"
            ],
            "Conditional Percentage Column": [
                "column", "new_column", "condition",
                "conditional_threshold", "conditional_true_percent",
                "conditional_false_percent"
            ],
        }

        visible = set(visible_fields.get(operation, []))

        if operation == "Create New Column":
            if mode in ("Fixed Value", "Percentage"):
                visible.update(["column", "value"])
            else:
                visible.update(["column", "second_column"])

        for key, (label, widget) in self.form_fields.items():
            show = key == "operation" or key in visible
            label.setVisible(show)
            widget.setVisible(show)

    def set_dataframe(self, dataframe):
        if dataframe is None:
            self.clear_data()
            return

        if not isinstance(dataframe, pd.DataFrame):
            QMessageBox.warning(
                self, "Invalid Dataset",
                "Please provide a valid Pandas DataFrame."
            )
            return

        self.original_df = dataframe.copy(deep=True)
        self.current_df = dataframe.copy(deep=True)
        self.undo_stack.clear()
        self.refresh_columns()
        self.refresh_preview()
        self.update_buttons()
        self.status_label.setText(
            "Dataset loaded. Ready for transformation."
        )

    def clear_data(self):
        self.original_df = None
        self.current_df = None
        self.undo_stack.clear()
        self.column_combo.clear()
        self.second_column_combo.clear()
        self.columns_list.clear()
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        self.info_label.setText("No dataset loaded.")
        self.status_label.setText("Import a dataset first.")
        self.update_buttons()

    def refresh_columns(self, preferred_column=None):
        if self.current_df is None:
            return

        if preferred_column is None:
            preferred_column = self.column_combo.currentData()

        self.column_combo.blockSignals(True)
        self.second_column_combo.blockSignals(True)
        self.column_combo.clear()
        self.second_column_combo.clear()
        self.columns_list.clear()

        for col in self.current_df.columns:
            self.column_combo.addItem(str(col), col)
            self.second_column_combo.addItem(str(col), col)
            item = QListWidgetItem(str(col))
            item.setData(Qt.ItemDataRole.UserRole, col)
            self.columns_list.addItem(item)

        index = self.column_combo.findData(preferred_column)
        if index >= 0:
            self.column_combo.setCurrentIndex(index)

        self.column_combo.blockSignals(False)
        self.second_column_combo.blockSignals(False)

    def get_selected_column(self):
        return self.column_combo.currentData()

    def get_second_selected_column(self):
        return self.second_column_combo.currentData()

    def apply_split_column(self):
        column = self.get_selected_column()
        if column not in self.current_df.columns:
            raise TransformationError("Please select a valid column.")

        names = [
            name.strip()
            for name in self.split_names_edit.text().split(",")
            if name.strip()
        ]

        if len(names) < 2:
            raise TransformationError("Enter at least two output column names.")
        if len(names) != len(set(names)):
            raise TransformationError("Output column names must be unique.")

        for name in names:
            if name in self.current_df.columns:
                raise TransformationError(f"Column '{name}' already exists.")

        separator = self.separator_edit.text()
        if separator == "":
            raise TransformationError("Please enter a separator.")

        series = self.current_df[column].astype("string")
        split_separator = None if separator.isspace() else separator
        split_data = series.str.split(
            pat=split_separator, n=len(names) - 1, expand=True
        )
        split_data = split_data.reindex(columns=range(len(names)))

        result = self.current_df.copy(deep=True)
        for index, name in enumerate(names):
            result[name] = split_data[index]
        return result

    def apply_transformation(self):
        if self.current_df is None:
            QMessageBox.warning(
                self, "No Dataset",
                "Please import a dataset first."
            )
            return

        if self.current_df.empty:
            QMessageBox.warning(
                self, "Empty Dataset",
                "The dataset contains no rows to transform."
            )
            return

        operation = self.operation_combo.currentText()
        column = self.get_selected_column()

        if operation != "Merge Columns":
            if operation != "Create New Column" or (
                self.calculation_mode_combo.currentText()
                in ("Fixed Value", "Percentage", "Another Column")
            ):
                if column not in self.current_df.columns:
                    QMessageBox.warning(
                        self, "Select Column",
                        "Please select a valid column."
                    )
                    return

        engine = TransformationEngine(self.current_df)

        try:
            if operation == "Change Data Type":
                result = engine.change_data_type(
                    column, self.data_type_combo.currentText()
                )

            elif operation == "Create New Column":
                new_name = self.new_column_edit.text().strip()
                if not new_name:
                    raise TransformationError("Enter a name for the new column.")

                mode = self.calculation_mode_combo.currentText()
                calculation = self.calculation_combo.currentText()

                if mode == "Fixed Value":
                    result = engine.create_column(
                        new_name, column, calculation,
                        self.value_edit.text().strip()
                    )
                elif mode == "Percentage":
                    result = engine.create_column_percentage(
                        new_name, column, calculation,
                        self.value_edit.text().strip()
                    )
                else:
                    second_column = self.get_second_selected_column()
                    if second_column not in self.current_df.columns:
                        raise TransformationError(
                            "Please select a valid second column."
                        )
                    result = engine.create_column_from_columns(
                        new_name, column, calculation, second_column
                    )

            elif operation == "Calculate Experience":
                new_name = self.new_column_edit.text().strip()
                if not new_name:
                    raise TransformationError(
                        "Enter a name for the new Experience column."
                    )
                result = engine.calculate_experience(
                    new_name,
                    column,
                    self.experience_format_combo.currentText(),
                    self.experience_end_date_edit.text().strip() or None,
                )

            elif operation == "Split Column":
                result = self.apply_split_column()

            elif operation == "Merge Columns":
                selected = [
                    item.data(Qt.ItemDataRole.UserRole)
                    for item in self.columns_list.selectedItems()
                ]
                if len(selected) < 2:
                    raise TransformationError(
                        "Select at least two columns to merge."
                    )

                new_name = self.new_column_edit.text().strip()
                if not new_name:
                    raise TransformationError(
                        "Enter a name for the merged column."
                    )

                result = engine.merge_columns(
                    selected, new_name, self.separator_edit.text()
                )

            elif operation == "Replace Values":
                old_value = self.value_edit.text().strip()
                new_value = self.replacement_edit.text().strip()
                if not old_value:
                    raise TransformationError("Please enter a value to replace.")

                result = self.current_df.copy(deep=True)
                series = result[column]

                if pd.api.types.is_numeric_dtype(series):
                    old_value = pd.to_numeric(old_value, errors="coerce")
                    new_value = pd.to_numeric(new_value, errors="coerce")
                    if pd.isna(old_value) or pd.isna(new_value):
                        raise TransformationError(
                            "Please enter valid numeric values."
                        )
                    if not series.eq(old_value).any():
                        raise TransformationError(
                            "The entered numeric value was not found in this column."
                        )
                    result[column] = series.replace(old_value, new_value)

                elif pd.api.types.is_datetime64_any_dtype(series):
                    old_value = pd.to_datetime(old_value, errors="coerce")
                    new_value = pd.to_datetime(new_value, errors="coerce")
                    if pd.isna(old_value) or pd.isna(new_value):
                        raise TransformationError("Please enter valid dates.")
                    result[column] = series.replace(old_value, new_value)

                else:
                    if not series.astype(str).eq(old_value).any():
                        raise TransformationError(
                            "The entered text value was not found in this column."
                        )
                    result[column] = series.replace(old_value, new_value)

            elif operation == "Sort Data":
                result = engine.sort_data(
                    column, self.sort_combo.currentText()
                )

            elif operation == "Filter Rows":
                result = engine.filter_rows(
                    column,
                    self.filter_combo.currentText(),
                    self.value_edit.text()
                )

            elif operation == "Conditional Percentage Column":
                new_name = self.new_column_edit.text().strip()
                if not new_name:
                    raise TransformationError("Enter a name for the new column.")

                result = engine.conditional_percentage_column(
                    new_name,
                    column,
                    self.condition_combo.currentText(),
                    self.conditional_threshold_edit.text().strip(),
                    self.conditional_true_percent_edit.text().strip(),
                    self.conditional_false_percent_edit.text().strip()
                )

            elif operation == "Conditional Column":
                new_name = self.new_column_edit.text().strip()
                if not new_name:
                    raise TransformationError("Enter a name for the new column.")

                result = engine.conditional_column(
                    new_name,
                    column,
                    self.condition_combo.currentText(),
                    self.value_edit.text(),
                    self.true_value_edit.text(),
                    self.false_value_edit.text()
                )

            else:
                return

            if not isinstance(result, pd.DataFrame):
                raise TransformationError(
                    "Transformation did not return a valid DataFrame."
                )

            self.undo_stack.append(self.current_df.copy(deep=True))
            self.current_df = result.copy(deep=True)
            self.refresh_columns()
            self.refresh_preview()
            self.update_buttons()
            self.status_label.setText(f"Applied successfully: {operation}")
            self.data_changed.emit(self.current_df.copy(deep=True))

        except Exception as error:
            QMessageBox.warning(self, "Transformation Error", str(error))
            self.status_label.setText(
                "Transformation could not be completed."
            )

    def undo(self):
        if not self.undo_stack:
            self.status_label.setText("Nothing to undo.")
            return

        self.current_df = self.undo_stack.pop()
        self.refresh_columns()
        self.refresh_preview()
        self.update_buttons()
        self.data_changed.emit(self.current_df.copy(deep=True))
        self.status_label.setText("Last transformation undone.")

    def reset_data(self):
        if self.original_df is None:
            return

        self.current_df = self.original_df.copy(deep=True)
        self.undo_stack.clear()
        self.refresh_columns()
        self.refresh_preview()
        self.update_buttons()
        self.data_changed.emit(self.current_df.copy(deep=True))
        self.status_label.setText("Original dataset restored.")

    def update_buttons(self):
        has_data = (
            self.current_df is not None
            and not self.current_df.empty
        )
        self.apply_button.setEnabled(has_data)
        self.undo_button.setEnabled(bool(self.undo_stack))
        self.reset_button.setEnabled(
            self.original_df is not None
            and self.current_df is not None
            and not self.current_df.equals(self.original_df)
        )

    def refresh_preview(self):
        if self.current_df is None:
            return

        preview = self.current_df.head(100)
        self.info_label.setText(
            f"Rows: {len(self.current_df):,}   |   "
            f"Columns: {len(self.current_df.columns):,}"
        )

        self.table.clear()
        self.table.setUpdatesEnabled(False)
        self.table.setRowCount(len(preview))
        self.table.setColumnCount(len(preview.columns))
        self.table.setHorizontalHeaderLabels(
            [str(column) for column in preview.columns]
        )

        for row_index, row in enumerate(
            preview.itertuples(index=False, name=None)
        ):
            for column_index, value in enumerate(row):
                missing = pd.isna(value)
                display_value = "" if missing else str(value)
                item = QTableWidgetItem(display_value)
                item.setFlags(
                    Qt.ItemFlag.ItemIsEnabled |
                    Qt.ItemFlag.ItemIsSelectable
                )
                self.table.setItem(row_index, column_index, item)

        self.table.setUpdatesEnabled(True)
        self.table.resizeRowsToContents()
        self.update_buttons()