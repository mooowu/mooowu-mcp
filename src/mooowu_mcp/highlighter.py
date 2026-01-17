from pathlib import Path
import pymupdf

from .pdf_reader import TextSpan, Sentence


def highlight_text_in_pdf(
    pdf_path: str | Path,
    search_text: str,
    output_path: str | Path | None = None,
    color: tuple[float, float, float] = (1, 1, 0),
) -> Path:
    pdf_path = Path(pdf_path)
    if output_path is None:
        output_path = pdf_path.with_stem(f"{pdf_path.stem}_highlighted")
    output_path = Path(output_path)

    doc = pymupdf.open(str(pdf_path))

    for page in doc:
        quads = page.search_for(search_text, quads=True)
        for quad in quads:
            annot = page.add_highlight_annot(quad)
            annot.set_colors(stroke=color)
            annot.update()

    doc.save(str(output_path))
    doc.close()

    return output_path


def highlight_spans(
    pdf_path: str | Path,
    spans: list[TextSpan],
    output_path: str | Path | None = None,
    color: tuple[float, float, float] = (1, 1, 0),
) -> Path:
    pdf_path = Path(pdf_path)
    if output_path is None:
        output_path = pdf_path.with_stem(f"{pdf_path.stem}_highlighted")
    output_path = Path(output_path)

    doc = pymupdf.open(str(pdf_path))

    for span in spans:
        if span.page_num >= len(doc):
            continue

        page = doc[span.page_num]
        rect = pymupdf.Rect(span.bbox)
        annot = page.add_highlight_annot(rect)
        annot.set_colors(stroke=color)
        annot.update()

    doc.save(str(output_path))
    doc.close()

    return output_path


def highlight_sentences(
    pdf_path: str | Path,
    sentences: list[Sentence],
    output_path: str | Path | None = None,
    color: tuple[float, float, float] = (1, 1, 0),
) -> Path:
    all_spans: list[TextSpan] = []
    for sentence in sentences:
        all_spans.extend(sentence.spans)

    return highlight_spans(pdf_path, all_spans, output_path, color)
