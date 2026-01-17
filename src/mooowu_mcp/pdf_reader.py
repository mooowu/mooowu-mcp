from dataclasses import dataclass
from pathlib import Path
import pymupdf


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


def extract_text_blocks(pdf_path: str | Path) -> list[TextBlock]:
    doc = pymupdf.open(str(pdf_path))
    blocks: list[TextBlock] = []

    for page_num, page in enumerate(doc):
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


def extract_all_spans(pdf_path: str | Path) -> list[TextSpan]:
    blocks = extract_text_blocks(pdf_path)
    spans: list[TextSpan] = []
    for block in blocks:
        spans.extend(block.spans)
    return spans
