import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from jsonresume_schema import validate


def minimal():
    return {
        "$schema": "x",
        "basics": {"name": "Lea", "email": "lea@example.com"},
        "work": [{"name": "c-sense", "position": "Engineer", "startDate": "2024-08-01"}],
        "meta": {},
    }


def test_valid_document_has_no_errors():
    assert validate(minimal()) == []


def test_bad_date_format_is_reported_with_its_path():
    data = minimal()
    data["work"][0]["startDate"] = "2024-08"
    errors = validate(data)
    assert errors == [("work[0].startDate", "must be YYYY-MM-DD or empty, got '2024-08'")]


def test_empty_date_is_allowed_for_ongoing_entries():
    data = minimal()
    data["work"][0]["endDate"] = ""
    assert validate(data) == []


def test_unknown_key_is_reported():
    data = minimal()
    data["work"][0]["employer"] = "c-sense"
    paths = [p for p, _ in validate(data)]
    assert "work[0].employer" in paths


def test_missing_required_key_is_reported():
    data = minimal()
    del data["work"][0]["position"]
    assert ("work[0].position", "required field is missing") in validate(data)


def test_wrong_type_is_reported():
    data = minimal()
    data["work"][0]["highlights"] = "not a list"
    paths = [p for p, _ in validate(data)]
    assert "work[0].highlights" in paths
