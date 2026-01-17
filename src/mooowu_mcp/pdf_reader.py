from dataclasses import dataclass
from pathlib import Path
import re
import pymupdf

from .parallel import PageRange, process_pages_parallel


@dataclass
class TextSpan:
    text: str
    bbox: tuple[float, float, float, float]
    font: str
    size: float
    page_num: int


@dataclass
class TextBlock:
    spans: list[TextSpan]
    bbox: tuple[float, float, float, float]
    page_num: int

    @property
    def text(self) -> str:
        return " ".join(span.text for span in self.spans)


def _extract_blocks_from_page_range(page_range: PageRange) -> list[TextBlock]:
    doc = pymupdf.open(page_range.pdf_path)
    blocks: list[TextBlock] = []

    for page_num in range(page_range.start, page_range.end):
        if page_num >= len(doc):
            break

        page = doc[page_num]
        page_dict = page.get_text("dict")

        for block in page_dict["blocks"]:
            if block.get("type") != 0:
                continue

            block_spans: list[TextSpan] = []
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    if not span.get("text", "").strip():
                        continue

                    text_span = TextSpan(
                        text=span["text"],
                        bbox=tuple(span["bbox"]),
                        font=span.get("font", ""),
                        size=span.get("size", 0.0),
                        page_num=page_num,
                    )
                    block_spans.append(text_span)

            if block_spans:
                text_block = TextBlock(
                    spans=block_spans,
                    bbox=tuple(block["bbox"]),
                    page_num=page_num,
                )
                blocks.append(text_block)

    doc.close()
    return blocks


def extract_text_blocks(pdf_path: str | Path) -> list[TextBlock]:
    doc = pymupdf.open(str(pdf_path))
    total_pages = len(doc)
    doc.close()

    return process_pages_parallel(
        pdf_path,
        total_pages,
        _extract_blocks_from_page_range,
    )


def extract_all_spans(pdf_path: str | Path) -> list[TextSpan]:
    blocks = extract_text_blocks(pdf_path)
    spans: list[TextSpan] = []
    for block in blocks:
        spans.extend(block.spans)
    return spans


@dataclass
class Sentence:
    text: str
    spans: list[TextSpan]
    page_num: int

    @property
    def bbox(self) -> tuple[float, float, float, float]:
        if not self.spans:
            return (0, 0, 0, 0)
        x0 = min(s.bbox[0] for s in self.spans)
        y0 = min(s.bbox[1] for s in self.spans)
        x1 = max(s.bbox[2] for s in self.spans)
        y1 = max(s.bbox[3] for s in self.spans)
        return (x0, y0, x1, y1)


SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")


def extract_sentences(pdf_path: str | Path) -> list[Sentence]:
    blocks = extract_text_blocks(pdf_path)
    sentences: list[Sentence] = []

    for block in blocks:
        if not block.spans:
            continue

        block_text = " ".join(span.text for span in block.spans)
        sentence_texts = SENTENCE_BOUNDARY.split(block_text)

        for sent_text in sentence_texts:
            sent_text = sent_text.strip()
            if not sent_text:
                continue

            sent_spans: list[TextSpan] = []
            for span in block.spans:
                if sent_text in span.text or span.text in sent_text:
                    sent_spans.append(span)

            if not sent_spans:
                sent_spans = list(block.spans)

            sentence = Sentence(
                text=sent_text,
                spans=sent_spans,
                page_num=block.page_num,
            )
            sentences.append(sentence)

    return sentences
