from pathlib import Path
from typing import cast
from mcp.server.fastmcp import FastMCP

from .pdf_reader import extract_sentences
from .content_filter import filter_sentences, get_image_regions
from .highlighter import highlight_sentences

mcp = FastMCP("mooowu-mcp")


@mcp.tool()
def read_pdf(pdf_path: str) -> str:
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    sentences = extract_sentences(pdf_path)
    filtered = filter_sentences(sentences, pdf_path)

    return "\n".join(s.text for s in filtered)


@mcp.tool()
def highlight_pdf(
    pdf_path: str,
    sentences: list[str],
    output_path: str | None = None,
    color: list[float] | None = None,
) -> dict:
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    highlight_color: tuple[float, float, float] = (1.0, 1.0, 0.0)
    if color and len(color) >= 3:
        highlight_color = (float(color[0]), float(color[1]), float(color[2]))

    all_sentences = extract_sentences(pdf_path)
    filtered = filter_sentences(all_sentences, pdf_path)

    matched: list = []
    not_found: list[str] = []

    for search_text in sentences:
        found = False
        for sent in filtered:
            if sent.text == search_text:
                matched.append(sent)
                found = True
                break
        if not found:
            not_found.append(search_text)

    if matched:
        out_path = Path(output_path) if output_path else None
        result_path = highlight_sentences(pdf_path, matched, out_path, highlight_color)
    else:
        result_path = Path(pdf_path)

    response = {
        "output_path": str(result_path),
        "highlighted_count": len(matched),
        "total_requested": len(sentences),
    }

    if not_found:
        response["warnings"] = [f"Sentence not found: {s}" for s in not_found]

    return response


@mcp.tool()
def analyze_pdf(pdf_path: str) -> dict:
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    import pymupdf

    doc = pymupdf.open(str(path))
    page_count = len(doc)
    doc.close()

    sentences = extract_sentences(pdf_path)
    images = get_image_regions(pdf_path)
    filtered = filter_sentences(sentences, pdf_path, images)

    code_sentence_count = len(sentences) - len(filtered)

    return {
        "page_count": page_count,
        "sentence_count": len(sentences),
        "highlightable_sentence_count": len(filtered),
        "code_block_sentence_count": code_sentence_count,
        "image_count": len(images),
        "highlightable_sentences": [s.text for s in filtered],
    }


def main():
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
