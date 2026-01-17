from pathlib import Path

from mooowu_mcp.pdf_reader import TextSpan


def test_detect_courier_as_code():
    from mooowu_mcp.content_filter import is_code_span

    span = TextSpan(
        text="def foo():",
        bbox=(0, 0, 100, 20),
        font="Courier",
        size=10,
        page_num=0,
    )
    assert is_code_span(span) is True


def test_detect_cour_as_code():
    from mooowu_mcp.content_filter import is_code_span

    span = TextSpan(
        text="def foo():",
        bbox=(0, 0, 100, 20),
        font="cour",
        size=10,
        page_num=0,
    )
    assert is_code_span(span) is True


def test_detect_monospace_variants():
    from mooowu_mcp.content_filter import is_code_span

    fonts = ["Consolas", "Monaco", "Menlo", "Source Code Pro", "FiraCode-Regular"]
    for font in fonts:
        span = TextSpan(
            text="code",
            bbox=(0, 0, 50, 10),
            font=font,
            size=10,
            page_num=0,
        )
        assert is_code_span(span) is True, f"Failed for font: {font}"


def test_preserve_regular_fonts():
    from mooowu_mcp.content_filter import is_code_span

    fonts = ["Helvetica", "Arial", "Times-Roman", "Georgia"]
    for font in fonts:
        span = TextSpan(
            text="regular text",
            bbox=(0, 0, 100, 20),
            font=font,
            size=12,
            page_num=0,
        )
        assert is_code_span(span) is False, f"Failed for font: {font}"


def test_filter_removes_code_spans():
    from mooowu_mcp.content_filter import filter_code_spans

    spans = [
        TextSpan("regular", (0, 0, 50, 10), "Helvetica", 12, 0),
        TextSpan("code", (50, 0, 100, 10), "Courier", 10, 0),
        TextSpan("more text", (100, 0, 150, 10), "Arial", 12, 0),
    ]

    filtered = filter_code_spans(spans)

    assert len(filtered) == 2
    assert all("Courier" not in s.font for s in filtered)


def test_get_image_regions_detects_images(sample_pdf_with_image: Path):
    from mooowu_mcp.content_filter import get_image_regions

    regions = get_image_regions(sample_pdf_with_image)

    assert len(regions) >= 1
    for region in regions:
        x0, y0, x1, y1 = region.bbox
        assert x1 > x0
        assert y1 > y0


def test_no_images_returns_empty_list(sample_pdf_with_text: Path):
    from mooowu_mcp.content_filter import get_image_regions

    regions = get_image_regions(sample_pdf_with_text)
    assert len(regions) == 0


def test_overlap_detection_inside():
    from mooowu_mcp.content_filter import is_span_overlapping_image, ImageRegion

    span = TextSpan("text", (100, 120, 150, 140), "Helvetica", 12, 0)
    images = [ImageRegion((72, 100, 200, 200), 0)]

    assert is_span_overlapping_image(span, images) is True


def test_overlap_detection_partial():
    from mooowu_mcp.content_filter import is_span_overlapping_image, ImageRegion

    span = TextSpan("text", (180, 180, 220, 200), "Helvetica", 12, 0)
    images = [ImageRegion((72, 100, 200, 200), 0)]

    assert is_span_overlapping_image(span, images) is True


def test_no_overlap_detection():
    from mooowu_mcp.content_filter import is_span_overlapping_image, ImageRegion

    span = TextSpan("text", (250, 250, 300, 270), "Helvetica", 12, 0)
    images = [ImageRegion((72, 100, 200, 200), 0)]

    assert is_span_overlapping_image(span, images) is False


def test_filter_removes_overlapping_spans():
    from mooowu_mcp.content_filter import filter_image_overlapping_spans, ImageRegion

    spans = [
        TextSpan("before", (10, 10, 50, 30), "Helvetica", 12, 0),
        TextSpan("inside", (100, 120, 150, 140), "Helvetica", 12, 0),
        TextSpan("after", (10, 250, 50, 270), "Helvetica", 12, 0),
    ]
    images = [ImageRegion((72, 100, 200, 200), 0)]

    filtered = filter_image_overlapping_spans(spans, images)

    assert len(filtered) == 2
    assert "inside" not in [s.text for s in filtered]


def test_filter_sentences_removes_code(sample_pdf_with_code: Path):
    from mooowu_mcp.pdf_reader import extract_sentences
    from mooowu_mcp.content_filter import filter_sentences

    sentences = extract_sentences(sample_pdf_with_code)
    filtered = filter_sentences(sentences, sample_pdf_with_code)

    for sentence in filtered:
        for span in sentence.spans:
            assert "cour" not in span.font.lower()


def test_filter_sentences_keeps_regular_text(sample_pdf_with_text: Path):
    from mooowu_mcp.pdf_reader import extract_sentences
    from mooowu_mcp.content_filter import filter_sentences

    sentences = extract_sentences(sample_pdf_with_text)
    filtered = filter_sentences(sentences, sample_pdf_with_text)

    assert len(filtered) == len(sentences)
