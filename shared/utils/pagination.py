"""Pagination utilities — reference implementation."""
import math
from dataclasses import dataclass


@dataclass
class PaginationParams:
    page: int = 1
    page_size: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

def calculate_pages(total: int, page_size: int) -> int:
    return math.ceil(total / page_size) if total > 0 else 0
