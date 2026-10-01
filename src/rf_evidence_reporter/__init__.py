"""Robot Framework Evidence Reporter public API."""

from .builder import build_reports
from .library import EvidenceReporter
from .recorder import EvidenceRecorder

__version__ = "0.1.0"
__all__ = ["EvidenceReporter", "EvidenceRecorder", "build_reports"]
