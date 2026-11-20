
"""DataClean Studio main window."""

from pathlib import Path

import pandas as pd

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QStackedWidget,
    QFrame,
    QFileDialog,
    QMessageBox,
    QPushButton,
)

from config.settings import (
    APP_NAME,
    APP_VERSION,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    MIN_WINDOW_HEIGHT,
)

from app.navigation import NavigationSidebar
from ui.pages.home_page import HomePage
from ui.pages.import_page import ImportPage
from ui.pages.data_preview_page import DataPreviewPage
from ui.pages.data_cleaning_page import CleaningPage
from ui.pages.transformation_page import TransformationPage


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()

        self.current_dataframe = None
        self.original_dataframe = None
        self.current_file_path = None
        self.current_sheet_name = None
        self.last_workspace_page = "Home"

        self.setWindowTitle(
            f"{APP_NAME} - Excel & CSV Data Cleaner"
        )

        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setMinimumSize(
            MIN_WINDOW_WIDTH,
            MIN_WINDOW_HEIGHT
        )

        self.setup_ui()
        self.load_theme()
        self.update_window_title()

    # --------------------------------------------------
    # MAIN UI
    # --------------------------------------------------

    def setup_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)

        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Sidebar
        self.sidebar = NavigationSidebar()
        root_layout.addWidget(self.sidebar)

        # Main workspace
        workspace = QWidget()
        workspace.setObjectName("workspace")

        workspace_layout = QVBoxLayout(workspace)
        workspace_layout.setContentsMargins(0, 0, 0, 0)
        workspace_layout.setSpacing(0)

        self.create_topbar(workspace_layout)

        # Page stack
        self.page_stack = QStackedWidget()
        self.page_stack.setObjectName("pageStack")

        # Home page
        self.home_page = HomePage()

        if hasattr(self.home_page, "import_requested"):
            self.home_page.import_requested.connect(
                lambda: self.sidebar.select_page("Import Data")
            )

        self.page_stack.addWidget(self.home_page)

        # Import page
        self.import_page = ImportPage()
        self.import_page.data_loaded.connect(
            self.handle_data_loaded
        )
        self.page_stack.addWidget(self.import_page)

        # Data preview page
        self.data_preview_page = DataPreviewPage()
        self.page_stack.addWidget(self.data_preview_page)

        # Cleaning page
        self.cleaning_page = CleaningPage()
        self.cleaning_page.data_applied.connect(
            self.handle_cleaned_data
        )
        self.page_stack.addWidget(self.cleaning_page)

        # Transformation page
        self.transformation_page = TransformationPage()
        self.transformation_page.data_changed.connect(
            self.handle_transformed_data
        )
        self.page_stack.addWidget(self.transformation_page)

        # Export page
        self.export_page = self.create_export_page()
        self.page_stack.addWidget(self.export_page)

        workspace_layout.addWidget(self.page_stack)
        root_layout.addWidget(workspace, 1)

        # Navigation connection
        self.sidebar.page_changed.connect(self.change_page)
        self.sidebar.select_page("Home")

    # --------------------------------------------------
    # TOP BAR
    # --------------------------------------------------

    def create_topbar(self, parent_layout):
        topbar = QFrame()
        topbar.setObjectName("topbar")
        topbar.setFixedHeight(68)

        layout = QHBoxLayout(topbar)
        layout.setContentsMargins(28, 10, 28, 10)

        self.page_title = QLabel("Home")
        self.page_title.setObjectName("topbarTitle")
        layout.addWidget(self.page_title)

        layout.addStretch()

        app_version = QLabel(
            f"DataClean Studio v{APP_VERSION}"
        )
        app_version.setObjectName("versionLabel")
        layout.addWidget(app_version)

        parent_layout.addWidget(topbar)

    # --------------------------------------------------
    # EXPORT PAGE
    # --------------------------------------------------

    def create_export_page(self):
        page = QWidget()
        page.setObjectName("exportPage")

        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 26, 28, 28)
        layout.setSpacing(16)

        title = QLabel("Export Cleaned Data")
        title.setObjectName("pageTitle")

        description = QLabel(
            "Save your cleaned and transformed dataset "
            "as an Excel or CSV file."
        )
        description.setObjectName("placeholderDescription")
        description.setWordWrap(True)

        self.export_status_label = QLabel(
            "Import a file and apply your cleaning or "
            "transformation steps first."
        )
        self.export_status_label.setWordWrap(True)
        self.export_status_label.setObjectName(
            "placeholderDescription"
        )

        buttons_row = QHBoxLayout()

        self.export_excel_button = QPushButton(
            "Export as Excel (.xlsx)"
        )
        self.export_csv_button = QPushButton(
            "Export as CSV (.csv)"
        )

        self.export_excel_button.setMinimumHeight(44)
        self.export_csv_button.setMinimumHeight(44)

        self.export_excel_button.clicked.connect(
            self.export_excel
        )
        self.export_csv_button.clicked.connect(
            self.export_csv
        )

        buttons_row.addWidget(self.export_excel_button)
        buttons_row.addWidget(self.export_csv_button)
        buttons_row.addStretch()

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(self.export_status_label)
        layout.addLayout(buttons_row)
        layout.addStretch()

        self.update_export_page_state()

        return page

    # --------------------------------------------------
    # PAGE NAVIGATION
    # --------------------------------------------------

    def change_page(self, page_name):
        self.page_title.setText(page_name)

        page_map = {
            "Home": self.home_page,
            "Import Data": self.import_page,
            "Data Preview": self.data_preview_page,
            "Data Cleaning": self.cleaning_page,
            "Data Transformation": self.transformation_page,
            "Export Data": self.export_page,
        }

        page = page_map.get(page_name)

        if page is None:
            return

        self.page_stack.setCurrentWidget(page)

        if page_name in {
            "Data Preview",
            "Data Cleaning",
            "Data Transformation",
        }:
            self.last_workspace_page = page_name

        if (
            page_name == "Data Preview"
            and self.current_dataframe is None
        ):
            self.data_preview_page.clear_data()

        elif (
            page_name == "Data Cleaning"
            and self.current_dataframe is None
        ):
            self.cleaning_page.set_dataframe(None)

        elif (
            page_name == "Data Transformation"
            and self.current_dataframe is None
        ):
            self.transformation_page.clear_data()

        elif page_name == "Export Data":
            self.update_export_page_state()

    # --------------------------------------------------
    # DATA IMPORT / SYNCHRONIZATION
    # --------------------------------------------------

    def handle_data_loaded(
        self,
        dataframe,
        file_path,
        sheet_name=None
    ):
        """Receive imported data and update workflow pages."""

        if (
            dataframe is None
            or not isinstance(dataframe, pd.DataFrame)
        ):
            QMessageBox.warning(
                self,
                "Import Failed",
                "The imported data is invalid."
            )
            return

        self.original_dataframe = dataframe.copy(deep=True)
        self.current_dataframe = dataframe.copy(deep=True)

        self.current_file_path = (
            str(file_path) if file_path else None
        )
        self.current_sheet_name = sheet_name

        self.sync_dataframe_to_pages()
        self.update_export_page_state()
        self.update_window_title()

        self.sidebar.select_page("Data Preview")

    def sync_dataframe_to_pages(self):
        """Synchronize the current dataframe across pages."""

        if self.current_dataframe is None:
            self.data_preview_page.clear_data()
            self.cleaning_page.set_dataframe(None)
            self.transformation_page.clear_data()
            return

        data = self.current_dataframe.copy(deep=True)

        self.data_preview_page.set_dataframe(
            data.copy(deep=True)
        )

        self.cleaning_page.set_dataframe(
            data.copy(deep=True)
        )

        self.transformation_page.set_dataframe(
            data.copy(deep=True)
        )

    def handle_cleaned_data(self, dataframe):
        """Receive cleaned data from the Cleaning page."""

        if (
            dataframe is None
            or not isinstance(dataframe, pd.DataFrame)
        ):
            return

        self.current_dataframe = dataframe.copy(deep=True)

        self.data_preview_page.set_dataframe(
            self.current_dataframe.copy(deep=True)
        )

        self.transformation_page.set_dataframe(
            self.current_dataframe.copy(deep=True)
        )

        self.update_export_page_state()
        self.update_window_title()

    def handle_transformed_data(self, dataframe):
        """Receive transformed data from the Transformation page."""

        if (
            dataframe is None
            or not isinstance(dataframe, pd.DataFrame)
        ):
            return

        self.current_dataframe = dataframe.copy(deep=True)

        self.data_preview_page.set_dataframe(
            self.current_dataframe.copy(deep=True)
        )

        self.cleaning_page.set_dataframe(
            self.current_dataframe.copy(deep=True)
        )

        self.update_export_page_state()
        self.update_window_title()

    # --------------------------------------------------
    # EXPORT
    # --------------------------------------------------

    def update_export_page_state(self):
        has_data = (
            isinstance(self.current_dataframe, pd.DataFrame)
            and not self.current_dataframe.empty
        )

        if not hasattr(self, "export_excel_button"):
            return

        self.export_excel_button.setEnabled(has_data)
        self.export_csv_button.setEnabled(has_data)

        if has_data:
            self.export_status_label.setText(
                f"Ready to export "
                f"{len(self.current_dataframe):,} rows and "
                f"{len(self.current_dataframe.columns):,} columns."
            )
        else:
            self.export_status_label.setText(
                "No data available. Import an Excel or CSV file first."
            )

    def export_excel(self):
        """Export current data to Excel."""

        if self.current_dataframe is None:
            QMessageBox.warning(
                self,
                "No Data",
                "Import data before exporting."
            )
            return

        default_name = self.get_export_default_name(
            "_cleaned.xlsx"
        )

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Cleaned Data as Excel",
            default_name,
            "Excel Workbook (*.xlsx)",
        )

        if not file_path:
            return

        if not file_path.lower().endswith(".xlsx"):
            file_path += ".xlsx"

        try:
            self.current_dataframe.to_excel(
                file_path,
                index=False,
                engine="openpyxl"
            )

            QMessageBox.information(
                self,
                "Export Successful",
                f"Excel file saved successfully:\n\n{file_path}"
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                "Excel Export Failed",
                str(exc)
            )

    def export_csv(self):
        """Export current data to CSV."""

        if self.current_dataframe is None:
            QMessageBox.warning(
                self,
                "No Data",
                "Import data before exporting."
            )
            return

        default_name = self.get_export_default_name(
            "_cleaned.csv"
        )

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Cleaned Data as CSV",
            default_name,
            "CSV Files (*.csv)",
        )

        if not file_path:
            return

        if not file_path.lower().endswith(".csv"):
            file_path += ".csv"

        try:
            self.current_dataframe.to_csv(
                file_path,
                index=False,
                encoding="utf-8-sig"
            )

            QMessageBox.information(
                self,
                "Export Successful",
                f"CSV file saved successfully:\n\n{file_path}"
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                "CSV Export Failed",
                str(exc)
            )

    def get_export_default_name(self, suffix):
        if self.current_file_path:
            source_path = Path(self.current_file_path)

            return str(
                source_path.with_name(
                    f"{source_path.stem}{suffix}"
                )
            )

        return f"cleaned_data{suffix}"

    # --------------------------------------------------
    # WINDOW TITLE / LIGHT THEME
    # --------------------------------------------------

    def update_window_title(self):
        if self.current_file_path:
            file_name = Path(self.current_file_path).name

            self.setWindowTitle(
                f"{file_name} - {APP_NAME} - Data Cleaner"
            )
        else:
            self.setWindowTitle(
                f"{APP_NAME} - Excel & CSV Data Cleaner"
            )

    def load_theme(self):
        """Load the only available theme: Light Mode."""

        theme_path = (
            Path(__file__).resolve().parent.parent
            / "ui"
            / "themes"
            / "light.qss"
        )

        if theme_path.exists():
            stylesheet = theme_path.read_text(
                encoding="utf-8"
            )
            self.setStyleSheet(stylesheet)
        else:
            QMessageBox.warning(
                self,
                "Theme Not Found",
                f"Light theme file not found:\n{theme_path}"
            )

    def closeEvent(self, event):
        event.accept()
