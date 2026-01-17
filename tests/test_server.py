from pathlib import Path


def test_server_imports():
    from mooowu_mcp.server import mcp, main

    assert mcp is not None
    assert callable(main)


def test_read_pdf_returns_text(sample_pdf_with_text: Path):
    from mooowu_mcp.server import read_pdf

    result = read_pdf(str(sample_pdf_with_text))

    assert "first sentence" in result
    assert "second sentence" in result


def test_read_pdf_excludes_code(sample_pdf_with_code: Path):
    from mooowu_mcp.server import read_pdf

    result = read_pdf(str(sample_pdf_with_code))

    assert "def hello_world" not in result
    assert "print" not in result
    assert "Regular text" in result


def test_read_pdf_invalid_path():
    from mooowu_mcp.server import read_pdf
    import pytest

    with pytest.raises(FileNotFoundError):
        read_pdf("/nonexistent/path.pdf")


def test_highlight_pdf_creates_output(sample_pdf_with_text: Path, temp_dir: Path):
    from mooowu_mcp.server import highlight_pdf

    output = temp_dir / "output.pdf"
    result = highlight_pdf(
        str(sample_pdf_with_text),
        ["This is the first sentence."],
        str(output),
    )

    assert result["highlighted_count"] == 1
    assert Path(result["output_path"]).exists()


def test_highlight_pdf_skips_code(sample_pdf_with_code: Path, temp_dir: Path):
    from mooowu_mcp.server import highlight_pdf

    output = temp_dir / "output.pdf"
    result = highlight_pdf(
        str(sample_pdf_with_code),
        ["def hello_world():"],
        str(output),
    )

    assert result["highlighted_count"] == 0
    assert "warnings" in result


def test_highlight_pdf_returns_warnings(sample_pdf_with_text: Path, temp_dir: Path):
    from mooowu_mcp.server import highlight_pdf

    output = temp_dir / "output.pdf"
    result = highlight_pdf(
        str(sample_pdf_with_text),
        ["Nonexistent sentence."],
        str(output),
    )

    assert result["highlighted_count"] == 0
    assert "warnings" in result
    assert len(result["warnings"]) == 1


def test_highlight_pdf_with_color(sample_pdf_with_text: Path, temp_dir: Path):
    from mooowu_mcp.server import highlight_pdf

    output = temp_dir / "output.pdf"
    result = highlight_pdf(
        str(sample_pdf_with_text),
        ["This is the first sentence."],
        str(output),
        color=[0, 1, 0],
    )

    assert result["highlighted_count"] == 1


def test_analyze_pdf_page_count(sample_pdf_multipage: Path):
    from mooowu_mcp.server import analyze_pdf

    result = analyze_pdf(str(sample_pdf_multipage))

    assert result["page_count"] == 3


def test_analyze_pdf_counts_sentences(sample_pdf_with_text: Path):
    from mooowu_mcp.server import analyze_pdf

    result = analyze_pdf(str(sample_pdf_with_text))

    assert result["sentence_count"] >= 2
    assert result["highlightable_sentence_count"] >= 2


def test_analyze_pdf_detects_code(sample_pdf_with_code: Path):
    from mooowu_mcp.server import analyze_pdf

    result = analyze_pdf(str(sample_pdf_with_code))

    assert result["code_block_sentence_count"] >= 1


def test_analyze_pdf_detects_images(sample_pdf_with_image: Path):
    from mooowu_mcp.server import analyze_pdf

    result = analyze_pdf(str(sample_pdf_with_image))

    assert result["image_count"] >= 1
