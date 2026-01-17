from pathlib import Path
import tempfile
import pytest
import pymupdf


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_pdf_with_text(temp_dir: Path) -> Path:
    pdf_path = temp_dir / "sample_text.pdf"
    doc = pymupdf.open()
    page = doc.new_page()

    page.insert_text(
        (72, 72),
        "This is the first sentence. This is the second sentence.",
        fontsize=12,
        fontname="helv",
    )
    page.insert_text(
        (72, 100),
        "Another paragraph with important text.",
        fontsize=12,
        fontname="helv",
    )

    doc.save(pdf_path)
    doc.close()
    return pdf_path


@pytest.fixture
def sample_pdf_with_code(temp_dir: Path) -> Path:
    pdf_path = temp_dir / "sample_code.pdf"
    doc = pymupdf.open()
    page = doc.new_page()

    page.insert_text(
        (72, 72),
        "Regular text before code block.",
        fontsize=12,
        fontname="helv",
    )
    page.insert_text(
        (72, 100),
        "def hello_world():",
        fontsize=10,
        fontname="cour",
    )
    page.insert_text(
        (72, 115),
        "    print('Hello, World!')",
        fontsize=10,
        fontname="cour",
    )
    page.insert_text(
        (72, 145),
        "Regular text after code block.",
        fontsize=12,
        fontname="helv",
    )

    doc.save(pdf_path)
    doc.close()
    return pdf_path


@pytest.fixture
def sample_pdf_with_image(temp_dir: Path) -> Path:
    pdf_path = temp_dir / "sample_image.pdf"
    doc = pymupdf.open()
    page = doc.new_page()

    page.insert_text(
        (72, 72),
        "Text before the image.",
        fontsize=12,
        fontname="helv",
    )

    img_rect = pymupdf.Rect(72, 100, 200, 200)
    pixmap = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 128, 100), 1)
    pixmap.set_rect(pixmap.irect, (200, 200, 200))
    page.insert_image(img_rect, pixmap=pixmap)

    page.insert_text(
        (72, 220),
        "Text after the image.",
        fontsize=12,
        fontname="helv",
    )

    doc.save(pdf_path)
    doc.close()
    return pdf_path


@pytest.fixture
def sample_pdf_multipage(temp_dir: Path) -> Path:
    pdf_path = temp_dir / "sample_multipage.pdf"
    doc = pymupdf.open()

    for i in range(3):
        page = doc.new_page()
        page.insert_text(
            (72, 72),
            f"This is page {i + 1}. It contains sample text.",
            fontsize=12,
            fontname="helv",
        )

    doc.save(pdf_path)
    doc.close()
    return pdf_path


@pytest.fixture
def sample_pdf_mixed(temp_dir: Path) -> Path:
    pdf_path = temp_dir / "sample_mixed.pdf"
    doc = pymupdf.open()
    page = doc.new_page()

    page.insert_text(
        (72, 72),
        "Introduction paragraph with regular text.",
        fontsize=12,
        fontname="helv",
    )

    page.insert_text(
        (72, 100),
        "console.log('hello');",
        fontsize=10,
        fontname="cour",
    )

    img_rect = pymupdf.Rect(72, 130, 200, 230)
    pixmap = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 128, 100), 1)
    pixmap.set_rect(pixmap.irect, (150, 150, 150))
    page.insert_image(img_rect, pixmap=pixmap)

    page.insert_text(
        (72, 250),
        "Conclusion paragraph that should be highlightable.",
        fontsize=12,
        fontname="helv",
    )

    doc.save(pdf_path)
    doc.close()
    return pdf_path
