
"""DashEasy native project save/load engine."""

import json
import sqlite3
import tempfile
import zipfile

from pathlib import Path

import pandas as pd


PROJECT_FORMAT_VERSION = 1
PROJECT_EXTENSION = ".dash"


class ProjectManagerError(Exception):
    """Raised when a DashEasy project operation fails."""


class ProjectManager:
    """Save and load DashEasy projects using SQLite and JSON."""

    # ==================================================
    # SAVE PROJECT
    # ==================================================

    @staticmethod
    def save_project(
        file_path,
        tables,
        relationships=None,
        source_files=None,
        project_name=None,
        kpis=None,
        dashboards=None,
    ):
        """
        Save tables, relationships, KPIs and dashboards.

        Package contains:
        - manifest.json
        - data.sqlite
        """

        file_path = Path(file_path)

        if file_path.suffix.lower() != PROJECT_EXTENSION:
            file_path = file_path.with_suffix(PROJECT_EXTENSION)

        if not tables:
            raise ProjectManagerError(
                "Cannot save a project without tables."
            )

        relationships = relationships or []
        source_files = source_files or {}
        kpis = kpis or []
        dashboards = dashboards or []

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        try:
            with tempfile.TemporaryDirectory() as temp_dir:

                temp_dir = Path(temp_dir)

                database_path = temp_dir / "data.sqlite"
                manifest_path = temp_dir / "manifest.json"

                table_metadata = []

                connection = sqlite3.connect(database_path)

                try:
                    for index, (table_name, dataframe) in enumerate(
                        tables.items()
                    ):

                        if not isinstance(dataframe, pd.DataFrame):
                            raise ProjectManagerError(
                                f"Invalid table data: {table_name}"
                            )

                        if not all(
                            isinstance(column, str)
                            for column in dataframe.columns
                        ):
                            raise ProjectManagerError(
                                f"Table '{table_name}' has non-text "
                                "column names."
                            )

                        if not dataframe.columns.is_unique:
                            raise ProjectManagerError(
                                f"Table '{table_name}' has duplicate "
                                "column names."
                            )

                        database_table_name = f"dataset_{index}"

                        dataframe.to_sql(
                            database_table_name,
                            connection,
                            if_exists="replace",
                            index=False,
                        )

                        table_metadata.append({
                            "name": str(table_name),
                            "database_table": database_table_name,
                            "rows": int(len(dataframe)),
                            "columns": [
                                str(column)
                                for column in dataframe.columns
                            ],
                            "source_file": source_files.get(table_name),
                        })

                    connection.commit()

                except Exception:
                    connection.rollback()
                    raise

                finally:
                    connection.close()

                # Validate KPI definitions
                safe_kpis = []

                for kpi in kpis:
                    if not isinstance(kpi, dict):
                        raise ProjectManagerError(
                            "Invalid KPI definition."
                        )

                    if not {"name", "aggregation"}.issubset(kpi):
                        raise ProjectManagerError(
                            "A KPI is missing its name or aggregation."
                        )

                    safe_kpi = {
                        "name": str(kpi["name"]),
                        "aggregation": str(kpi["aggregation"]),
                        "column": (
                            str(kpi["column"])
                            if kpi.get("column") is not None
                            else None
                        ),
                    }

                    if kpi.get("formula") is not None:
                        safe_kpi["formula"] = str(kpi["formula"])

                    safe_kpis.append(safe_kpi)

                # Validate dashboard configurations
                if not isinstance(dashboards, list):
                    raise ProjectManagerError(
                        "Dashboards must be provided as a list."
                    )

                for dashboard in dashboards:
                    if not isinstance(dashboard, dict):
                        raise ProjectManagerError(
                            "Invalid dashboard configuration."
                        )

                # Build manifest
                manifest = {
                    "application": "DashEasy",
                    "format_version": PROJECT_FORMAT_VERSION,
                    "project_name": (
                        project_name or file_path.stem
                    ),
                    "tables": table_metadata,
                    "relationships": relationships,
                    "kpis": safe_kpis,
                    "dashboards": dashboards,
                }

                # Ensure all metadata can be serialized
                try:
                    manifest_json = json.dumps(
                        manifest,
                        indent=4,
                        ensure_ascii=False,
                        default=str,
                    )
                except (TypeError, ValueError) as error:
                    raise ProjectManagerError(
                        f"Could not serialize project metadata: {error}"
                    ) from error

                manifest_path.write_text(
                    manifest_json,
                    encoding="utf-8",
                )

                # Create project archive
                with zipfile.ZipFile(
                    file_path,
                    mode="w",
                    compression=zipfile.ZIP_DEFLATED,
                ) as project_archive:

                    project_archive.write(
                        manifest_path,
                        arcname="manifest.json",
                    )

                    project_archive.write(
                        database_path,
                        arcname="data.sqlite",
                    )

            return str(file_path)

        except ProjectManagerError:
            raise

        except Exception as error:
            raise ProjectManagerError(
                f"Could not save project: {error}"
            ) from error

    # ==================================================
    # LOAD PROJECT
    # ==================================================

    @staticmethod
    def load_project(file_path):
        """Load a DashEasy project."""

        file_path = Path(file_path)

        if not file_path.exists():
            raise ProjectManagerError(
                f"Project file does not exist: {file_path}"
            )

        if not zipfile.is_zipfile(file_path):
            raise ProjectManagerError(
                "This is not a valid DashEasy project file."
            )

        try:
            with tempfile.TemporaryDirectory() as temp_dir:

                temp_dir = Path(temp_dir)

                with zipfile.ZipFile(file_path, "r") as archive:

                    required_files = {
                        "manifest.json",
                        "data.sqlite",
                    }

                    available_files = set(archive.namelist())

                    if not required_files.issubset(available_files):
                        raise ProjectManagerError(
                            "Project package is missing required files."
                        )

                    for member in required_files:
                        archive.extract(member, temp_dir)

                manifest_path = temp_dir / "manifest.json"
                database_path = temp_dir / "data.sqlite"

                manifest = json.loads(
                    manifest_path.read_text(encoding="utf-8")
                )

                if manifest.get("application") != "DashEasy":
                    raise ProjectManagerError(
                        "This file is not a DashEasy project."
                    )

                version = manifest.get("format_version")

                if version != PROJECT_FORMAT_VERSION:
                    raise ProjectManagerError(
                        f"Unsupported project format version: {version}"
                    )

                tables = {}
                source_files = {}

                connection = sqlite3.connect(database_path)

                try:
                    for table_info in manifest.get("tables", []):

                        table_name = table_info["name"]
                        database_table = table_info["database_table"]

                        if not database_table.replace("_", "").isalnum():
                            raise ProjectManagerError(
                                "Invalid database table identifier."
                            )

                        dataframe = pd.read_sql_query(
                            f'SELECT * FROM "{database_table}"',
                            connection,
                        )

                        tables[table_name] = dataframe

                        source_files[table_name] = (
                            table_info.get("source_file")
                        )

                finally:
                    connection.close()

                return {
                    "project_name": manifest.get(
                        "project_name",
                        file_path.stem,
                    ),
                    "tables": tables,
                    "relationships": manifest.get(
                        "relationships",
                        [],
                    ),
                    "source_files": source_files,
                    "kpis": manifest.get("kpis", []),
                    "dashboards": manifest.get("dashboards", []),
                    "format_version": version,
                }

        except ProjectManagerError:
            raise

        except Exception as error:
            raise ProjectManagerError(
                f"Could not load project: {error}"
            ) from error
