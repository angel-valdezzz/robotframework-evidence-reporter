"""Robot Framework Evidence Reporter public API."""

from ._version import __version__ as __version__

from .builder import build_reports
from .library import EvidenceReporter
from .recorder import EvidenceRecorder
from .merge import merge_results

__all__ = ["EvidenceReporter", "EvidenceRecorder", "build_reports", "merge_results"]
