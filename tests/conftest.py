import pytest
from backend.review_store import ReviewStore

@pytest.fixture(autouse=True)
def isolated_review_journal(tmp_path,monkeypatch):
    from backend import main
    monkeypatch.setattr(main,'review_store',ReviewStore(tmp_path/'reviews.sqlite3'))
