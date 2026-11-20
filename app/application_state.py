
"""DashEasy central application state and dataset manager."""

from PySide6.QtCore import QObject, Signal


class ApplicationState(QObject):
    """
    Stores the currently active dataset.

    All application modules can access the same active dataset
    through the MainWindow's ApplicationState instance.
    """

    dataset_changed = Signal(object, str, str, bool)

    def __init__(self):
        super().__init__()

        self.current_dataframe = None
        self.current_file_path = ""
        self.current_sheet_name = ""

    @property
    def has_dataset(self):
        """Check whether a dataset is currently loaded."""

        return self.current_dataframe is not None

    @property
    def row_count(self):
        """Return the number of dataset rows."""

        if not self.has_dataset:
            return 0

        return len(self.current_dataframe)

    @property
    def column_count(self):
        """Return the number of dataset columns."""

        if not self.has_dataset:
            return 0

        return len(self.current_dataframe.columns)

    @property
    def file_name(self):
        """Return the active dataset filename."""

        if not self.current_file_path:
            return ""

        from pathlib import Path

        return Path(self.current_file_path).name

    def set_dataset(self, dataframe, file_path, sheet_name=""):
        """Set the active dataset after successful import."""

        if dataframe is None:
            raise ValueError("Dataset cannot be None.")

        if dataframe.empty:
            raise ValueError("Dataset contains no data rows.")

        self.current_dataframe = dataframe
        self.current_file_path = str(file_path)
        self.current_sheet_name = str(sheet_name or "")

        self.dataset_changed.emit(
            self.current_dataframe,
            self.current_file_path,
            self.current_sheet_name,
            True
        )

    def clear_dataset(self):
        """Clear the active dataset."""

        self.current_dataframe = None
        self.current_file_path = ""
        self.current_sheet_name = ""

        self.dataset_changed.emit(
            None,
            "",
            "",
            False
        )
