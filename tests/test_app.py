import pytest
import os
from keyword_cluster_app.clustering import load_keywords_from_file

def test_load_keywords_from_file_with_volume(tmp_path):
    # Create a temporary CSV file with keyword and volume
    csv_content = """Keyword,Volume
keyword1,100
keyword2,200
keyword3,300
"""
    file_path = tmp_path / "test_with_volume.csv"
    file_path.write_text(csv_content)

    keywords = load_keywords_from_file(str(file_path))

    assert len(keywords) == 3
    assert keywords[0]["text"] == "keyword1"
    assert keywords[0]["volume"] == 100
    assert keywords[1]["text"] == "keyword2"
    assert keywords[1]["volume"] == 200
    assert keywords[2]["text"] == "keyword3"
    assert keywords[2]["volume"] == 300

def test_load_keywords_from_file_without_volume(tmp_path):
    # Create a temporary CSV file with only keyword
    csv_content = """Keyword
keywordA
keywordB
keywordC
"""
    file_path = tmp_path / "test_without_volume.csv"
    file_path.write_text(csv_content)

    keywords = load_keywords_from_file(str(file_path))

    assert len(keywords) == 3
    assert keywords[0]["text"] == "keywordA"
    assert keywords[0]["volume"] == 0 # Should default to 0
    assert keywords[1]["text"] == "keywordB"
    assert keywords[1]["volume"] == 0
    assert keywords[2]["text"] == "keywordC"
    assert keywords[2]["volume"] == 0

def test_load_keywords_from_file_empty_lines(tmp_path):
    csv_content = """Keyword,Volume

keyword1,100

keyword2,200

"""
    file_path = tmp_path / "test_empty_lines.csv"
    file_path.write_text(csv_content)

    keywords = load_keywords_from_file(str(file_path))
    assert len(keywords) == 2
    assert keywords[0]["text"] == "keyword1"
    assert keywords[1]["text"] == "keyword2"

def test_load_keywords_from_file_different_separator(tmp_path):
    csv_content = """Keyword;Volume
keyword1;100
keyword2;200
"""
    file_path = tmp_path / "test_semicolon.csv"
    file_path.write_text(csv_content)

    keywords = load_keywords_from_file(str(file_path))
    assert len(keywords) == 2
    assert keywords[0]["text"] == "keyword1"
    assert keywords[0]["volume"] == 100

def test_load_keywords_from_file_alias_columns(tmp_path):
    csv_content = """Search Term,Average Monthly Searches
kw_alias1,500
kw_alias2,600
"""
    file_path = tmp_path / "test_alias.csv"
    file_path.write_text(csv_content)

    keywords = load_keywords_from_file(str(file_path))
    assert len(keywords) == 2
    assert keywords[0]["text"] == "kw_alias1"
    assert keywords[0]["volume"] == 500

def test_load_keywords_from_file_non_existent(tmp_path):
    file_path = tmp_path / "non_existent.csv"
    with pytest.raises(FileNotFoundError):
        load_keywords_from_file(str(file_path))

def test_load_keywords_from_file_no_keyword_column(tmp_path):
    csv_content = """Volume,Other
100,data
200,more_data
"""
    file_path = tmp_path / "test_no_keyword.csv"
    file_path.write_text(csv_content)

    with pytest.raises(ValueError, match="Không tìm thấy cột keyword"):
        load_keywords_from_file(str(file_path))
