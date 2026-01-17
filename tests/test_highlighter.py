from pathlib import Path
import pymupdf


def test_highlight_single_occurrence(sample_pdf_with_text: Path, temp_dir: Path):
    from mooowu_mcp.highlighter import highlight_text_in_pdf

    output_path = temp_dir / "highlighted.pdf"
    result = highlight_text_in_pdf(sample_pdf_with_text, "first sentence", output_path)

    assert result.exists()
    doc = pymupdf.open(str(result))
    annots = list(doc[0].annots())
    assert len(annots) >= 1
    doc.close()


def test_highlight_multiple_occurrences(sample_pdf_multipage: Path, temp_dir: Path):
    from mooowu_mcp.highlighter import highlight_text_in_pdf

    output_path = temp_dir / "highlighted.pdf"
    result = highlight_text_in_pdf(sample_pdf_multipage, "page", output_path)

    assert result.exists()
    doc = pymupdf.open(str(result))
    total_annots = sum(len(list(page.annots())) for page in doc)
    assert total_annots >= 3
    doc.close()


def test_highlight_no_match(sample_pdf_with_text: Path, temp_dir: Path):
    from mooowu_mcp.highlighter import highlight_text_in_pdf

    output_path = temp_dir / "highlighted.pdf"
    result = highlight_text_in_pdf(
        sample_pdf_with_text, "nonexistent text xyz", output_path
    )

    assert result.exists()
    doc = pymupdf.open(str(result))
    annots = list(doc[0].annots())
    assert len(annots) == 0
    doc.close()


def test_highlight_creates_output_file(sample_pdf_with_text: Path, temp_dir: Path):
    from mooowu_mcp.highlighter import highlight_text_in_pdf

    output_path = temp_dir / "my_highlighted.pdf"
    assert not output_path.exists()

    result = highlight_text_in_pdf(sample_pdf_with_text, "first", output_path)

    assert result == output_path
    assert output_path.exists()


def test_highlight_preserves_original(sample_pdf_with_text: Path, temp_dir: Path):
    from mooowu_mcp.highlighter import highlight_text_in_pdf

    original_doc = pymupdf.open(str(sample_pdf_with_text))
    original_annots = len(list(original_doc[0].annots()))
    original_doc.close()

    output_path = temp_dir / "highlighted.pdf"
    highlight_text_in_pdf(sample_pdf_with_text, "first", output_path)

    original_doc = pymupdf.open(str(sample_pdf_with_text))
    after_annots = len(list(original_doc[0].annots()))
    original_doc.close()

    assert original_annots == after_annots


def test_highlight_spans_by_coordinates(sample_pdf_with_text: Path, temp_dir: Path):
    from mooowu_mcp.highlighter import highlight_spans
    from mooowu_mcp.pdf_reader import extract_all_spans

    spans = extract_all_spans(sample_pdf_with_text)
    output_path = temp_dir / "highlighted.pdf"

    result = highlight_spans(sample_pdf_with_text, spans[:1], output_path)

    assert result.exists()
    doc = pymupdf.open(str(result))
    annots = list(doc[0].annots())
    assert len(annots) >= 1
    doc.close()


def test_highlight_sentences_all_spans(sample_pdf_with_text: Path, temp_dir: Path):
    from mooowu_mcp.highlighter import highlight_sentences
    from mooowu_mcp.pdf_reader import extract_sentences

    sentences = extract_sentences(sample_pdf_with_text)
    output_path = temp_dir / "highlighted.pdf"

    result = highlight_sentences(sample_pdf_with_text, sentences[:1], output_path)

    assert result.exists()
    doc = pymupdf.open(str(result))
    annots = list(doc[0].annots())
    assert len(annots) >= 1
    doc.close()


def test_highlight_with_custom_color(sample_pdf_with_text: Path, temp_dir: Path):
    from mooowu_mcp.highlighter import highlight_text_in_pdf

    output_path = temp_dir / "highlighted.pdf"
    result = highlight_text_in_pdf(
        sample_pdf_with_text,
        "first",
        output_path,
        color=(0, 1, 0),
    )

    assert result.exists()
