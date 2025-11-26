"""
Demo V2 Library - Modules for enhanced demo experience.

Modules:
- feedback: User feedback collection on recommendations
- selector: Multi-selection of agents
- batch_generator: Batch agent generation
"""

from .feedback import FeedbackCollector, UserFeedback
from .selector import AgentSelector, SelectionResult
from .batch_generator import BatchGenerator, GenerationResult

__all__ = [
    "FeedbackCollector",
    "UserFeedback",
    "AgentSelector",
    "SelectionResult",
    "BatchGenerator",
    "GenerationResult",
]
