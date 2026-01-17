from pathlib import Path


def test_extract_text_from_single_page(sample_pdf_with_text: Path):
    from mooowu_mcp.pdf_reader import extract_text_blocks

    blocks = extract_text_blocks(sample_pdf_with_text)

    assert len(blocks) >= 1
    all_text = " ".join(block.text for block in blocks)
    assert "first sentence" in all_text
    assert "second sentence" in all_text


def test_extract_text_preserves_coordinates(sample_pdf_with_text: Path):
    from mooowu_mcp.pdf_reader import extract_text_blocks

    blocks = extract_text_blocks(sample_pdf_with_text)

    for block in blocks:
        x0, y0, x1, y1 = block.bbox
        assert x0 >= 0
        assert y0 >= 0
        assert x1 > x0
        assert y1 > y0

        for span in block.spans:
            sx0, sy0, sx1, sy1 = span.bbox
            assert sx0 >= 0
            assert sy0 >= 0
            assert sx1 > sx0
            assert sy1 > sy0


def test_extract_text_includes_font_info(sample_pdf_with_text: Path):
    from mooowu_mcp.pdf_reader import extract_text_blocks

    blocks = extract_text_blocks(sample_pdf_with_text)

    for block in blocks:
        for span in block.spans:
            assert span.font != ""
            assert span.size > 0


def test_extract_text_multipage(sample_pdf_multipage: Path):
    from mooowu_mcp.pdf_reader import extract_text_blocks

    blocks = extract_text_blocks(sample_pdf_multipage)

    page_nums = {block.page_num for block in blocks}
    assert 0 in page_nums
    assert 1 in page_nums
    assert 2 in page_nums


def test_extract_all_spans(sample_pdf_with_text: Path):
    from mooowu_mcp.pdf_reader import extract_all_spans

    spans = extract_all_spans(sample_pdf_with_text)

    assert len(spans) >= 1
    all_text = " ".join(span.text for span in spans)
    assert "first sentence" in all_text


def test_extract_sentences_simple(sample_pdf_with_text: Path):
    from mooowu_mcp.pdf_reader import extract_sentences

    sentences = extract_sentences(sample_pdf_with_text)

    assert len(sentences) >= 2
    sentence_texts = [s.text for s in sentences]
    assert any("first sentence" in t for t in sentence_texts)
    assert any("second sentence" in t for t in sentence_texts)


def test_extract_sentences_preserves_span_mapping(sample_pdf_with_text: Path):
    from mooowu_mcp.pdf_reader import extract_sentences

    sentences = extract_sentences(sample_pdf_with_text)

    for sentence in sentences:
        assert len(sentence.spans) >= 1
        assert sentence.page_num >= 0


def test_extract_sentences_multipage(sample_pdf_multipage: Path):
    from mooowu_mcp.pdf_reader import extract_sentences

    sentences = extract_sentences(sample_pdf_multipage)

    page_nums = {s.page_num for s in sentences}
    assert 0 in page_nums
    assert 1 in page_nums
    assert 2 in page_nums
