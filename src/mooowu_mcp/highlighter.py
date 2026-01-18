from concurrent.futures import ProcessPoolExecutor
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import os
import tempfile
import pymupdf

from .pdf_reader import TextSpan, Sentence
from .parallel import PageRange, get_page_ranges, MAX_WORKERS, DEFAULT_CHUNK_SIZE


@dataclass
class HighlightTask:
    pdf_path: str
    page_start: int
    page_end: int
    spans: list[TextSpan]
    color: tuple[float, float, float]
    temp_path: str


def _highlight_page_range_worker(task: HighlightTask) -> str:
    doc = pymupdf.open(task.pdf_path)
    total_pages = len(doc)

    pages_to_keep = list(range(task.page_start, min(task.page_end, total_pages)))
    if not pages_to_keep:
        doc.close()
        empty_doc = pymupdf.open()
        empty_doc.save(task.temp_path)
        empty_doc.close()
        return task.temp_path

    doc.select(pages_to_keep)

    for span in task.spans:
        relative_page = span.page_num - task.page_start
        if 0 <= relative_page < len(doc):
            page = doc[relative_page]
            rect = pymupdf.Rect(span.bbox)
            annot = page.add_highlight_annot(rect)
            annot.set_colors(stroke=task.color)
            annot.update()

    doc.save(task.temp_path, garbage=4, deflate=True)
    doc.close()
    return task.temp_path


def highlight_spans_parallel(
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
    total_pages = len(doc)
    doc.close()

    if total_pages <= DEFAULT_CHUNK_SIZE or len(spans) < 10:
        return highlight_spans(pdf_path, spans, output_path, color)

    spans_by_page: dict[int, list[TextSpan]] = defaultdict(list)
    for span in spans:
        spans_by_page[span.page_num].append(span)

    page_ranges = get_page_ranges(pdf_path, total_pages)

    temp_dir = tempfile.mkdtemp(prefix="highlight_")
    tasks: list[HighlightTask] = []

    for i, page_range in enumerate(page_ranges):
        range_spans: list[TextSpan] = []
        for page_num in range(page_range.start, page_range.end):
            range_spans.extend(spans_by_page.get(page_num, []))

        temp_path = os.path.join(temp_dir, f"part_{i:04d}.pdf")
        task = HighlightTask(
            pdf_path=str(pdf_path),
            page_start=page_range.start,
            page_end=page_range.end,
            spans=range_spans,
            color=color,
            temp_path=temp_path,
        )
        tasks.append(task)

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        temp_paths = list(executor.map(_highlight_page_range_worker, tasks))

    final_doc = pymupdf.open()
    for temp_path in temp_paths:
        if os.path.exists(temp_path):
            with pymupdf.open(temp_path) as part_doc:
                final_doc.insert_pdf(part_doc)
            os.remove(temp_path)

    final_doc.save(str(output_path), garbage=4, deflate=True)
    final_doc.close()

    try:
        os.rmdir(temp_dir)
    except OSError:
        pass

    return output_path


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

    return highlight_spans_parallel(pdf_path, all_spans, output_path, color)
