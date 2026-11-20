
"""DashEasy - Import Data Page."""

from pathlib import Path

import pandas as pd

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QFileDialog,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
)


from core.import_engine.file_loader import (
    load_data_file,
    get_excel_sheet_names,
    ImportFileError,
)


class ImportPage(QWidget):
    """Import Excel and CSV files into DashEasy."""

    data_loaded = Signal(object, str, str)

    def __init__(self):
        super().__init__()

        self.selected_file = None
        self.current_dataframe = None

        self.setup_ui()

    def setup_ui(self):
        """Build the Import Data interface."""

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(18)

        # Page title
        title = QLabel("Import Data")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "Upload Excel or CSV files to start analyzing your data."
        )
        subtitle.setObjectName("pageSubtitle")

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        # File selection card
        file_card = QFrame()
        file_card.setObjectName("welcomeCard")

        file_layout = QVBoxLayout(file_card)
        file_layout.setContentsMargins(22, 22, 22, 22)
        file_layout.setSpacing(14)

        file_heading = QLabel("Select Your Dataset")
        file_heading.setObjectName("welcomeTitle")

        self.file_label = QLabel("No file selected")
        self.file_label.setObjectName("welcomeDescription")
        self.file_label.setWordWrap(True)

        self.browse_button = QPushButton("Browse Files")
        self.browse_button.setObjectName("primaryButton")
        self.browse_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.browse_button.clicked.connect(self.browse_file)

        file_layout.addWidget(file_heading)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.browse_button)

        # Excel worksheet selection
        self.sheet_container = QWidget()

        sheet_layout = QHBoxLayout(self.sheet_container)
        sheet_layout.setContentsMargins(0, 0, 0, 0)

        sheet_label = QLabel("Excel Worksheet:")
        sheet_label.setObjectName("stepHeading")

        self.sheet_combo = QComboBox()
        self.sheet_combo.setMinimumWidth(200)
        self.sheet_combo.setEnabled(False)

        sheet_layout.addWidget(sheet_label)
        sheet_layout.addWidget(self.sheet_combo)
        sheet_layout.addStretch()

        file_layout.addWidget(self.sheet_container)

        # Hide worksheet selector initially
        self.sheet_container.hide()

        # Import button
        self.import_button = QPushButton("Import Dataset")
        self.import_button.setObjectName("primaryButton")
        self.import_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.import_button.setEnabled(False)
        self.import_button.clicked.connect(self.import_file)

        file_layout.addWidget(self.import_button)

        main_layout.addWidget(file_card)

        # Dataset information
        self.info_label = QLabel(
            "Dataset information will appear here after import."
        )
        self.info_label.setObjectName("sectionTitle")

        main_layout.addWidget(self.info_label)

        # Data preview heading
        preview_heading = QLabel(
            "Data Preview (First 100 Rows)"
        )
        preview_heading.setObjectName("sectionTitle")

        main_layout.addWidget(preview_heading)

        # Data preview table
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(False)

        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.table.horizontalHeader().setStretchLastSection(True)

        main_layout.addWidget(self.table, 1)

        # Status message
        self.status_label = QLabel("Ready to import data.")
        self.status_label.setObjectName("pageSubtitle")

        main_layout.addWidget(self.status_label)

    def browse_file(self):
        """Open file selection dialog."""

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Dataset",
            "",
            "Supported Files (*.xlsx *.xls *.csv);;"
            "Excel Files (*.xlsx *.xls);;"
            "CSV Files (*.csv)"
        )

        if not file_path:
            return

        self.selected_file = Path(file_path)
        self.current_dataframe = None

        self.file_label.setText(
            f"Selected: {self.selected_file.name}"
        )

        self.info_label.setText(
            "File selected. Ready to import."
        )

        # Clear previous preview
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)

        self.import_button.setEnabled(False)

        self.sheet_combo.clear()
        self.sheet_combo.setEnabled(False)
        self.sheet_container.hide()

        try:
            extension = self.selected_file.suffix.lower()

            # Excel file handling
            if extension in {".xlsx", ".xls"}:

                sheets = get_excel_sheet_names(
                    self.selected_file
                )

                if not sheets:
                    raise ImportFileError(
                        "No worksheets found in this workbook."
                    )

                self.sheet_combo.addItems(sheets)
                self.sheet_combo.setEnabled(True)

                self.sheet_container.show()

            # CSV file handling
            else:
                self.sheet_container.hide()

            self.import_button.setEnabled(True)

            self.status_label.setText(
                "File selected successfully."
            )

        except ImportFileError as error:

            self.selected_file = None

            QMessageBox.critical(
                self,
                "File Selection Error",
                str(error)
            )

            self.status_label.setText(
                "Unable to prepare the selected file."
            )

    def import_file(self):
        """Import the selected Excel or CSV file."""

        if not self.selected_file:
            return

        self.import_button.setEnabled(False)
        self.browse_button.setEnabled(False)

        self.status_label.setText(
            "Importing dataset..."
        )

        try:
            sheet_name = None

            # Get selected Excel worksheet
            if self.selected_file.suffix.lower() in {
                ".xlsx", ".xls"
            }:
                sheet_name = self.sheet_combo.currentText()

            # Load actual dataset
            dataframe = load_data_file(
                self.selected_file,
                sheet_name=sheet_name
            )

            if dataframe.empty:

                self.current_dataframe = None

                QMessageBox.warning(
                    self,
                    "Empty Dataset",
                    "The selected file contains no data rows."
                )

                self.status_label.setText(
                    "No data rows were found."
                )

                return

            self.current_dataframe = dataframe

            # Display imported data
            self.show_dataset_preview(dataframe)

            rows, columns = dataframe.shape

            # Update dataset information
            self.info_label.setText(
                f"Rows: {rows:,}    |    "
                f"Columns: {columns:,}    |    "
                f"File: {self.selected_file.name}"
            )

            self.status_label.setText(
                "Dataset imported successfully."
            )

            # Send dataset to MainWindow
            self.data_loaded.emit(
                dataframe,
                str(self.selected_file),
                sheet_name or ""
            )

        except ImportFileError as error:

            QMessageBox.critical(
                self,
                "Import Error",
                str(error)
            )

            self.status_label.setText(
                "Dataset import failed."
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Unexpected Error",
                str(error)
            )

            self.status_label.setText(
                "An unexpected error occurred."
            )

        finally:

            self.import_button.setEnabled(
                self.selected_file is not None
            )

            self.browse_button.setEnabled(True)

    def show_dataset_preview(self, dataframe):
        """Display the first 100 rows of imported data."""

        preview = dataframe.head(100)

        # Prepare table dimensions
        self.table.clear()
        self.table.setRowCount(len(preview))
        self.table.setColumnCount(len(preview.columns))

        # Set column headers
        self.table.setHorizontalHeaderLabels(
            [str(column) for column in preview.columns]
        )

        # Populate table cells
        for row_index, row in enumerate(
            preview.itertuples(index=False, name=None)
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

        # Adjust column widths
        self.table.resizeColumnsToContents()

        # Reset preview to the first row
        if len(preview) > 0 and len(preview.columns) > 0:

            self.table.setCurrentCell(0, 0)

        self.table.scrollToTop()

        self.table.verticalScrollBar().setValue(0)

        self.table.horizontalScrollBar().setValue(0)
