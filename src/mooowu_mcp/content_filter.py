from pathlib import Path
from dataclasses import dataclass

from .pdf_reader import TextSpan, Sentence
import pymupdf

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


def get_image_regions(pdf_path: str | Path) -> list[ImageRegion]:
    doc = pymupdf.open(str(pdf_path))
    regions: list[ImageRegion] = []

    for page_num, page in enumerate(doc):
        page_dict = page.get_text("dict")

        for block in page_dict["blocks"]:
            if block.get("type") == 1:
                region = ImageRegion(
                    bbox=tuple(block["bbox"]),
                    page_num=page_num,
                )
                regions.append(region)

    doc.close()
    return regions


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
) -> list[Sentence]:
    images = get_image_regions(pdf_path)
    filtered: list[Sentence] = []

    for sentence in sentences:
        valid_spans = filter_code_spans(sentence.spans)
        valid_spans = filter_image_overlapping_spans(valid_spans, images)

        if valid_spans:
            filtered_sentence = Sentence(
                text=sentence.text,
                spans=valid_spans,
                page_num=sentence.page_num,
            )
            filtered.append(filtered_sentence)

    return filtered
