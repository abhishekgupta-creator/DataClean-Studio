import pandas as pd

from core.project_manager import ProjectManager


def test_save_and_load_project(tmp_path):

    departments = pd.DataFrame({
        "DeptID": [1, 2, 3],
        "Department": ["IT", "HR", "Sales"],
    })

    employees = pd.DataFrame({
        "EmpID": [101, 102, 103],
        "EmpName": ["Amit", "Neha", "Rohit"],
        "DeptID": [1, 2, 1],
    })

    tables = {
        "Departments": departments,
        "Employees": employees,
    }

    relationships = [
        {
            "table1": "Departments",
            "column1": "DeptID",
            "table2": "Employees",
            "column2": "DeptID",
            "relationship_type": "one-to-many",
        }
    ]

    project_path = tmp_path / "HR_Analytics.dash"

    ProjectManager.save_project(
        project_path,
        tables,
        relationships,
    )

    loaded = ProjectManager.load_project(project_path)

    assert loaded["project_name"] == "HR_Analytics"
    assert len(loaded["tables"]) == 2
    assert loaded["relationships"] == relationships

    pd.testing.assert_frame_equal(
        loaded["tables"]["Departments"],
        departments,
    )

    pd.testing.assert_frame_equal(
        loaded["tables"]["Employees"],
        employees,
    )