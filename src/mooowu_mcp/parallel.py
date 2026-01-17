from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, TypeVar
import os

T = TypeVar("T")

DEFAULT_CHUNK_SIZE = 10
MAX_WORKERS = min(8, os.cpu_count() or 4)


@dataclass
class PageRange:
    start: int
    end: int
    pdf_path: str


def get_page_ranges(pdf_path: str | Path, total_pages: int) -> list[PageRange]:
    pdf_path_str = str(pdf_path)
    chunk_size = max(1, total_pages // MAX_WORKERS)
    chunk_size = min(chunk_size, DEFAULT_CHUNK_SIZE)

    ranges: list[PageRange] = []
    for start in range(0, total_pages, chunk_size):
        end = min(start + chunk_size, total_pages)
        ranges.append(PageRange(start=start, end=end, pdf_path=pdf_path_str))

    return ranges


def process_pages_parallel(
    pdf_path: str | Path,
    total_pages: int,
    worker_func: Callable[[PageRange], list[T]],
) -> list[T]:
    if total_pages <= DEFAULT_CHUNK_SIZE:
        return worker_func(PageRange(0, total_pages, str(pdf_path)))

    ranges = get_page_ranges(pdf_path, total_pages)

    results: list[T] = []
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for chunk_results in executor.map(worker_func, ranges):
            results.extend(chunk_results)

    return results
