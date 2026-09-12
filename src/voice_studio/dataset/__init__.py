"""
Phrases dataset parsing, filtering, and multi-selection utilities.
"""

from .prompts import PromptsDataset, parse_multi_selection, parse_phrase_indices

__all__ = ["PromptsDataset", "parse_multi_selection", "parse_phrase_indices"]
