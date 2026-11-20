
"""DashEasy - Data Preview Module."""

import math

import pandas as pd

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)


class DataPreviewPage(QWidget):
    """Display and inspect imported datasets."""

    def __init__(self):
        super().__init__()

        self.dataframe = None
        self.filtered_dataframe = None

        self.current_page = 1
        self.page_size = 25

        self.sort_column = None
        self.sort_ascending = True

        self.setup_ui()

    def setup_ui(self):
        """Build the Data Preview interface."""

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(18)

        # Page heading
        title = QLabel("Data Preview")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "Explore, search and inspect your imported dataset."
        )
        subtitle.setObjectName("pageSubtitle")

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        # Dataset summary cards
        summary_layout = QGridLayout()
        summary_layout.setSpacing(12)

        self.total_rows_label = QLabel("0")
        self.total_columns_label = QLabel("0")
        self.missing_label = QLabel("0")
        self.duplicates_label = QLabel("0")

        summary_items = [
            ("Total Rows", self.total_rows_label),
            ("Total Columns", self.total_columns_label),
            ("Missing Values", self.missing_label),
            ("Duplicate Rows", self.duplicates_label),
        ]

        for index, (heading, value_label) in enumerate(summary_items):

            card = QFrame()
            card.setObjectName("welcomeCard")

            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(16, 14, 16, 14)
            card_layout.setSpacing(8)

            heading_label = QLabel(heading)
            heading_label.setObjectName("pageSubtitle")

            value_label.setObjectName("welcomeTitle")

            card_layout.addWidget(heading_label)
            card_layout.addWidget(value_label)

            summary_layout.addWidget(
                card,
                0,
                index
            )

        main_layout.addLayout(summary_layout)

        # Column information
        self.profile_label = QLabel(
            "Import a dataset to view column information."
        )
        self.profile_label.setObjectName("pageSubtitle")
        self.profile_label.setWordWrap(True)

        main_layout.addWidget(self.profile_label)

        # Search and pagination controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search across all columns..."
        )
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(
            self.search_data
        )

        self.search_input.setMinimumHeight(38)

        controls_layout.addWidget(self.search_input, 1)

        page_size_label = QLabel("Rows per page:")

        controls_layout.addWidget(page_size_label)

        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(
            ["25", "50", "100", "250"]
        )
        self.page_size_combo.setCurrentText("25")

        self.page_size_combo.currentTextChanged.connect(
            self.change_page_size
        )

        controls_layout.addWidget(self.page_size_combo)

        main_layout.addLayout(controls_layout)

        # Dataset table
        self.table = QTableWidget()

        self.table.setObjectName("dataPreviewTable")
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.table.setSortingEnabled(False)

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Interactive
        )

        self.table.horizontalHeader().setStretchLastSection(True)

        self.table.horizontalHeader().sectionClicked.connect(
            self.sort_data
        )

        self.table.verticalHeader().setDefaultSectionSize(32)

        main_layout.addWidget(self.table, 1)

        # Pagination controls
        pagination_layout = QHBoxLayout()

        self.records_label = QLabel("No dataset loaded")
        self.records_label.setObjectName("pageSubtitle")

        pagination_layout.addWidget(self.records_label)

        pagination_layout.addStretch()

        self.previous_button = QPushButton("Previous")
        self.previous_button.clicked.connect(
            self.previous_page
        )

        self.page_label = QLabel("Page 0 of 0")

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(
            self.next_page
        )

        pagination_layout.addWidget(self.previous_button)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.next_button)

        main_layout.addLayout(pagination_layout)

        # Initial state
        self.previous_button.setEnabled(False)
        self.next_button.setEnabled(False)

    def set_dataframe(self, dataframe):
        """Receive the imported dataset from MainWindow."""

        if dataframe is None or not isinstance(
            dataframe, pd.DataFrame
        ):
            self.clear_data()
            return

        self.dataframe = dataframe.copy()

        self.search_input.clear()

        self.sort_column = None
        self.sort_ascending = True

        self.current_page = 1

        self.update_profile()
        self.apply_filters()

    def clear_data(self):
        """Clear the preview when no dataset is available."""

        self.dataframe = None
        self.filtered_dataframe = None

        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)

        self.total_rows_label.setText("0")
        self.total_columns_label.setText("0")
        self.missing_label.setText("0")
        self.duplicates_label.setText("0")

        self.profile_label.setText(
            "Import a dataset to view column information."
        )

        self.records_label.setText("No dataset loaded")
        self.page_label.setText("Page 0 of 0")

        self.previous_button.setEnabled(False)
        self.next_button.setEnabled(False)

    def update_profile(self):
        """Calculate dataset summary and column information."""

        if self.dataframe is None:
            return

        df = self.dataframe

        total_rows, total_columns = df.shape

        missing_values = int(df.isna().sum().sum())

        duplicate_rows = int(df.duplicated().sum())

        self.total_rows_label.setText(
            f"{total_rows:,}"
        )

        self.total_columns_label.setText(
            f"{total_columns:,}"
        )

        self.missing_label.setText(
            f"{missing_values:,}"
        )

        self.duplicates_label.setText(
            f"{duplicate_rows:,}"
        )

        # Automatic data type detection
        numeric_count = 0
        date_count = 0
        other_count = 0

        for column in df.columns:

            dtype = df[column].dtype

            if pd.api.types.is_numeric_dtype(dtype):
                numeric_count += 1

            elif pd.api.types.is_datetime64_any_dtype(dtype):
                date_count += 1

            else:
                other_count += 1

        self.profile_label.setText(
            f"Column Types:  Numeric: {numeric_count}  |  "
            f"Date/Time: {date_count}  |  "
            f"Text/Other: {other_count}  |  "
            f"Missing Cells: {missing_values:,}"
        )

    def search_data(self, search_text):
        """Search across all columns."""

        self.current_page = 1
        self.apply_filters(search_text)

    def apply_filters(self, search_text=""):
        """Apply search and sorting to the dataset."""

        if self.dataframe is None:
            return

        df = self.dataframe.copy()

        search_text = search_text.strip()

        if search_text:

            search_mask = df.astype("string").apply(
                lambda column: column.str.contains(
                    search_text,
                    case=False,
                    na=False,
                    regex=False
                )
            ).any(axis=1)

            df = df[search_mask]

        # Apply column sorting
        if (
            self.sort_column is not None
            and self.sort_column in df.columns
        ):
            df = df.sort_values(
                by=self.sort_column,
                ascending=self.sort_ascending,
                na_position="last"
            )

        self.filtered_dataframe = df

        self.update_table()

    def sort_data(self, column_index):
        """Sort the dataset when a column header is clicked."""

        if self.filtered_dataframe is None:
            return

        columns = list(self.filtered_dataframe.columns)

        if column_index >= len(columns):
            return

        column_name = columns[column_index]

        if self.sort_column == column_name:
            self.sort_ascending = not self.sort_ascending

        else:
            self.sort_column = column_name
            self.sort_ascending = True

        self.current_page = 1

        self.apply_filters(
            self.search_input.text()
        )

    def update_table(self):
        """Display the current page of filtered records."""

        if self.filtered_dataframe is None:
            return

        df = self.filtered_dataframe

        total_records = len(df)

        total_pages = (
            math.ceil(total_records / self.page_size)
            if total_records > 0 else 0
        )

        self.current_page = min(
            max(self.current_page, 1),
            max(total_pages, 1)
        )

        start_index = (
            (self.current_page - 1) * self.page_size
        )

        end_index = min(
            start_index + self.page_size,
            total_records
        )

        page_data = df.iloc[start_index:end_index]

        # Prevent unnecessary table sorting
        self.table.setSortingEnabled(False)

        self.table.clear()

        self.table.setRowCount(len(page_data))
        self.table.setColumnCount(len(page_data.columns))

        self.table.setHorizontalHeaderLabels(
            [str(column) for column in page_data.columns]
        )

        # Populate table
        for row_index, row in enumerate(
            page_data.itertuples(index=False, name=None)
        ):

            for column_index, value in enumerate(row):

                if pd.isna(value):
                    display_value = ""
                else:
                    display_value = str(value)

                item = QTableWidgetItem(display_value)

                self.table.setItem(
                    row_index,
                    column_index,
                    item
                )

        self.table.resizeColumnsToContents()

        # Update pagination information
        if total_records > 0:

            self.records_label.setText(
                f"Showing {start_index + 1:,}–"
                f"{end_index:,} of {total_records:,} records"
            )

        else:
            self.records_label.setText(
                "No matching records found."
            )

        self.page_label.setText(
            f"Page {self.current_page} of {total_pages}"
        )

        self.previous_button.setEnabled(
            self.current_page > 1
        )

        self.next_button.setEnabled(
            self.current_page < total_pages
        )

    def change_page_size(self, value):
        """Change the number of records displayed per page."""

        self.page_size = int(value)
        self.current_page = 1

        self.update_table()

    def previous_page(self):
        """Navigate to the previous page."""

        if self.current_page > 1:

            self.current_page -= 1

            self.update_table()

    def next_page(self):
        """Navigate to the next page."""

        if self.filtered_dataframe is None:
            return

        total_pages = math.ceil(
            len(self.filtered_dataframe) / self.page_size
        )

        if self.current_page < total_pages:

            self.current_page += 1

            self.update_table()
