from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from .pdf_reader import TextSpan, Sentence
from .parallel import PageRange, process_pages_parallel
import pymupdf


def _make_bbox(bbox_list: Any) -> tuple[float, float, float, float]:
    return (
        float(bbox_list[0]),
        float(bbox_list[1]),
        float(bbox_list[2]),
        float(bbox_list[3]),
    )


MONOSPACE_FONTS = frozenset(
    [
        "courier",
        "mono",
        "consolas",
        "menlo",
        "monaco",
        "source code",
        "fira",
        "jetbrains",
        "inconsolata",
        "lucida console",
        "dejavu sans mono",
        "liberation mono",
        "cour",
    ]
)


def is_code_span(span: TextSpan) -> bool:
    font_lower = span.font.lower()
    return any(mono in font_lower for mono in MONOSPACE_FONTS)


def filter_code_spans(spans: list[TextSpan]) -> list[TextSpan]:
    return [span for span in spans if not is_code_span(span)]


@dataclass
class ImageRegion:
    bbox: tuple[float, float, float, float]
    page_num: int


def _extract_images_from_page_range(page_range: PageRange) -> list[ImageRegion]:
    doc = pymupdf.open(page_range.pdf_path)
    regions: list[ImageRegion] = []

    for page_num in range(page_range.start, page_range.end):
        if page_num >= len(doc):
            break

        page = doc[page_num]
        page_dict: Any = page.get_text("dict")

        for block in page_dict["blocks"]:
            if block.get("type") == 1:
                region = ImageRegion(
                    bbox=_make_bbox(block["bbox"]),
                    page_num=page_num,
                )
                regions.append(region)

    doc.close()
    return regions


def get_image_regions(pdf_path: str | Path) -> list[ImageRegion]:
    doc = pymupdf.open(str(pdf_path))
    total_pages = len(doc)
    doc.close()

    return process_pages_parallel(
        pdf_path,
        total_pages,
        _extract_images_from_page_range,
    )


def _is_span_overlapping_page_images(
    span: TextSpan,
    page_images: list[ImageRegion],
) -> bool:
    sx0, sy0, sx1, sy1 = span.bbox

    for img in page_images:
        ix0, iy0, ix1, iy1 = img.bbox
        if sx0 < ix1 and sx1 > ix0 and sy0 < iy1 and sy1 > iy0:
            return True

    return False


def is_span_overlapping_image(span: TextSpan, images: list[ImageRegion]) -> bool:
    sx0, sy0, sx1, sy1 = span.bbox

    for img in images:
        if img.page_num != span.page_num:
            continue

        ix0, iy0, ix1, iy1 = img.bbox

        if sx0 < ix1 and sx1 > ix0 and sy0 < iy1 and sy1 > iy0:
            return True

    return False


def filter_image_overlapping_spans(
    spans: list[TextSpan],
    images: list[ImageRegion],
) -> list[TextSpan]:
    return [span for span in spans if not is_span_overlapping_image(span, images)]


def filter_sentences(
    sentences: list[Sentence],
    pdf_path: str | Path,
    images: list[ImageRegion] | None = None,
) -> list[Sentence]:
    if images is None:
        images = get_image_regions(pdf_path)

    images_by_page: dict[int, list[ImageRegion]] = defaultdict(list)
    for img in images:
        images_by_page[img.page_num].append(img)

    filtered: list[Sentence] = []

    for sentence in sentences:
        valid_spans = filter_code_spans(sentence.spans)

        page_images = images_by_page.get(sentence.page_num, [])
        valid_spans = [
            span
            for span in valid_spans
            if not _is_span_overlapping_page_images(span, page_images)
        ]

        if valid_spans:
            filtered_sentence = Sentence(
                text=sentence.text,
                spans=valid_spans,
                page_num=sentence.page_num,
            )
            filtered.append(filtered_sentence)

    return filtered
