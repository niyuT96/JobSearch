from conftest import require_attr


def test_google_drive_store_interface():
    """Method under test: storage.google_drive_store.GoogleDriveStore (construction)"""
    GoogleDriveStore = require_attr("storage.google_drive_store", "GoogleDriveStore")
    store = GoogleDriveStore()
    assert store is not None

