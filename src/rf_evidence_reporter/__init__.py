"""Robot Framework Evidence Reporter public API."""

from .builder import build_reports
from .library import EvidenceReporter
from .recorder import EvidenceRecorder
from .merge import merge_results

__version__ = "0.2.0"
__all__ = ["EvidenceReporter", "EvidenceRecorder", "build_reports", "merge_results"]
