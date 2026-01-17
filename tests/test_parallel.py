from pathlib import Path
import time


def test_parallel_extracts_all_pages(sample_pdf_large: Path):
    from mooowu_mcp.pdf_reader import extract_text_blocks

    blocks = extract_text_blocks(sample_pdf_large)

    page_nums = {block.page_num for block in blocks}
    assert len(page_nums) == 50


def test_parallel_extracts_sentences_from_all_pages(sample_pdf_large: Path):
    from mooowu_mcp.pdf_reader import extract_sentences

    sentences = extract_sentences(sample_pdf_large)

    page_nums = {s.page_num for s in sentences}
    assert len(page_nums) == 50
    assert len(sentences) >= 100


def test_parallel_filters_code_across_pages(sample_pdf_large: Path):
    from mooowu_mcp.pdf_reader import extract_sentences
    from mooowu_mcp.content_filter import filter_sentences

    all_sentences = extract_sentences(sample_pdf_large)
    filtered = filter_sentences(all_sentences, sample_pdf_large)

    for sentence in filtered:
        assert "def process_page" not in sentence.text


def test_parallel_image_detection_all_pages(sample_pdf_large: Path):
    from mooowu_mcp.content_filter import get_image_regions

    regions = get_image_regions(sample_pdf_large)

    assert len(regions) == 0


def test_parallel_processing_completes_in_reasonable_time(sample_pdf_large: Path):
    from mooowu_mcp.pdf_reader import extract_sentences
    from mooowu_mcp.content_filter import filter_sentences

    start = time.time()

    sentences = extract_sentences(sample_pdf_large)
    filtered = filter_sentences(sentences, sample_pdf_large)

    elapsed = time.time() - start

    assert len(filtered) > 0
    assert elapsed < 10.0


def test_read_pdf_tool_with_large_pdf(sample_pdf_large: Path):
    from mooowu_mcp.server import read_pdf

    result = read_pdf(str(sample_pdf_large))

    assert "Page 1:" in result
    assert "Page 50:" in result
    assert "def process_page" not in result


def test_analyze_pdf_tool_with_large_pdf(sample_pdf_large: Path):
    from mooowu_mcp.server import analyze_pdf

    result = analyze_pdf(str(sample_pdf_large))

    assert result["page_count"] == 50
    assert result["sentence_count"] >= 100
    assert result["code_block_sentence_count"] >= 50
