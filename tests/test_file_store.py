from conftest import require_attr


def test_write_read_text(tmp_path):
    """Methods under test: storage.file_store.write_text, storage.file_store.read_text"""
    write_text = require_attr("storage.file_store", "write_text")
    read_text = require_attr("storage.file_store", "read_text")
    path = tmp_path / "x.txt"
    write_text(path, "hello")
    result = read_text(path)
    assert result == "hello"

