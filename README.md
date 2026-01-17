# mooowu-mcp

MCP server for PDF reading and intelligent highlighting. This server provides tools to extract clean text from PDFs (excluding code blocks and images), highlight specific sentences, and analyze PDF content.

## Features

- Clean PDF text extraction: Automatically filters out code blocks and text overlapping with images.
- Intelligent highlighting: Highlight specific sentences in a PDF with custom colors.
- PDF Analysis: Get metadata and a list of highlightable sentences.
- Built with FastMCP for reliable performance.

## Installation

### Using uv (Recommended)

You can run the server directly using `uvx`:

```bash
uvx --from mooowu-mcp mooowu-mcp
```

Or install it in your project:

```bash
uv add mooowu-mcp
```

## Configuration

### Claude Desktop

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mooowu-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mooowu-mcp",
        "run",
        "mooowu-mcp"
      ]
    }
  }
}
```

*Note: Replace `/path/to/mooowu-mcp` with the actual path to the project.*

## Tools

### read_pdf
Extracts clean text from a PDF file.

- `pdf_path` (string): Absolute path to the PDF file.

Returns the extracted text as a string.

### highlight_pdf
Highlights specified sentences in a PDF file.

- `pdf_path` (string): Absolute path to the PDF file.
- `sentences` (list of strings): List of sentences to highlight.
- `output_path` (string, optional): Path to save the highlighted PDF. Defaults to `{original}_highlighted.pdf`.
- `color` (list of floats, optional): RGB color for highlighting (e.g., `[1.0, 1.0, 0.0]` for yellow).

Returns a dictionary containing the output path and counts of highlighted sentences.

### analyze_pdf
Analyzes a PDF file and returns metadata.

- `pdf_path` (string): Absolute path to the PDF file.

Returns a dictionary with:
- `page_count`: Number of pages.
- `sentence_count`: Total number of sentences found.
- `highlightable_sentence_count`: Number of sentences after filtering.
- `code_block_sentence_count`: Number of sentences identified as code.
- `image_count`: Number of images found.
- `highlightable_sentences`: List of all sentences that can be highlighted.

## Development

To install development dependencies and run tests:

```bash
uv sync --extra dev
pytest
```

## License

This project is licensed under the MIT License.
