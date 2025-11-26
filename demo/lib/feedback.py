"""
Feedback Module - Collect user feedback on agent recommendations.

This module allows users to:
- Rate each recommendation (Very useful / Maybe / Not relevant)
- Add optional comments
- Refine recommendations based on feedback
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Callable

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from generators.agent_builder import AgentRecommendation


@dataclass
class UserFeedback:
    """User feedback for a single recommendation."""
    agent_type: str
    agent_name: str
    rating: str  # "useful", "maybe", "not_relevant"
    comment: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class FeedbackSession:
    """Complete feedback session for all recommendations."""
    feedbacks: list[UserFeedback] = field(default_factory=list)
    session_start: str = field(default_factory=lambda: datetime.now().isoformat())
    refined: bool = False

    def to_dict(self) -> dict:
        return {
            "session_start": self.session_start,
            "refined": self.refined,
            "feedbacks": [f.to_dict() for f in self.feedbacks]
        }

    def export_json(self, filepath: Path) -> None:
        """Export feedback session to JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)


class FeedbackCollector:
    """
    Collects user feedback on recommendations.

    Provides an interactive interface for users to rate each
    recommendation and optionally add comments.
    """

    RATING_OPTIONS = {
        "1": ("useful", "Très utile"),
        "2": ("maybe", "Peut-être"),
        "3": ("not_relevant", "Pas pertinent"),
    }

    def __init__(
        self,
        input_func: Callable[[], str] = input,
        print_func: Callable[[str], None] = print
    ):
        self.input_func = input_func
        self.print_func = print_func
        self.session = FeedbackSession()

    def print_header(self) -> None:
        """Print feedback section header."""
        self.print_func("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    FEEDBACK SUR LES RECOMMANDATIONS                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Pour chaque agent, indiquez votre intérêt :                                ║
║  [1] Très utile   [2] Peut-être   [3] Pas pertinent                         ║
║                                                                              ║
║  Vous pouvez ajouter un commentaire optionnel après chaque évaluation.      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

    def collect_single_feedback(
        self,
        index: int,
        recommendation: AgentRecommendation,
        expert_icon: str = "🤖"
    ) -> UserFeedback:
        """Collect feedback for a single recommendation."""
        priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}[recommendation.priority]

        self.print_func(f"""
┌──────────────────────────────────────────────────────────────────────────────┐
│  {index}. {expert_icon} {recommendation.name} {priority_icon} [{recommendation.priority.upper()}]
│     {recommendation.description}
│
│     📋 {recommendation.justification}
└──────────────────────────────────────────────────────────────────────────────┘
""")

        # Get rating
        while True:
            self.print_func("   Votre avis: [1] Très utile  [2] Peut-être  [3] Pas pertinent")
            choice = self.input_func("   Choix (1/2/3): ").strip()

            if choice in self.RATING_OPTIONS:
                rating, rating_label = self.RATING_OPTIONS[choice]
                self.print_func(f"   ✓ {rating_label}")
                break
            elif choice == "":
                rating, rating_label = "maybe", "Peut-être"
                self.print_func(f"   ✓ {rating_label} (défaut)")
                break
            else:
                self.print_func("   ⚠️  Choix invalide, veuillez entrer 1, 2 ou 3")

        # Get optional comment
        comment = self.input_func("   Commentaire (Entrée pour passer): ").strip()

        return UserFeedback(
            agent_type=recommendation.agent_type,
            agent_name=recommendation.name,
            rating=rating,
            comment=comment
        )

    def collect_all_feedback(
        self,
        recommendations: list[AgentRecommendation],
        expert_icons: dict[str, str] | None = None
    ) -> FeedbackSession:
        """
        Collect feedback for all recommendations.

        Args:
            recommendations: List of agent recommendations
            expert_icons: Optional dict mapping agent_type to icon

        Returns:
            FeedbackSession with all user feedbacks
        """
        self.print_header()

        expert_icons = expert_icons or {}

        for i, rec in enumerate(recommendations, 1):
            icon = expert_icons.get(rec.agent_type, "🤖")
            feedback = self.collect_single_feedback(i, rec, icon)
            self.session.feedbacks.append(feedback)

        return self.session

    def print_summary(self) -> None:
        """Print summary of collected feedback."""
        useful = sum(1 for f in self.session.feedbacks if f.rating == "useful")
        maybe = sum(1 for f in self.session.feedbacks if f.rating == "maybe")
        not_relevant = sum(1 for f in self.session.feedbacks if f.rating == "not_relevant")

        self.print_func(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         RÉSUMÉ DES FEEDBACKS                                 ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║   ✅ Très utile:    {useful:2d} agent(s)                                          ║
║   🤔 Peut-être:     {maybe:2d} agent(s)                                          ║
║   ❌ Pas pertinent: {not_relevant:2d} agent(s)                                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

    def ask_refinement(self) -> bool:
        """
        Ask user if they want to refine recommendations.

        Returns:
            True if user wants to refine, False to proceed to selection
        """
        self.print_func("""
   Options:
   [R] Raffiner les recommandations avec mes retours
   [S] Passer à la sélection des agents
""")
        choice = self.input_func("   Votre choix (R/S): ").strip().upper()
        return choice == "R"

    def get_useful_agents(self) -> list[str]:
        """Get list of agent_types rated as useful."""
        return [f.agent_type for f in self.session.feedbacks if f.rating == "useful"]

    def get_maybe_agents(self) -> list[str]:
        """Get list of agent_types rated as maybe."""
        return [f.agent_type for f in self.session.feedbacks if f.rating == "maybe"]

    def get_not_relevant_agents(self) -> list[str]:
        """Get list of agent_types rated as not relevant."""
        return [f.agent_type for f in self.session.feedbacks if f.rating == "not_relevant"]

    def filter_recommendations(
        self,
        recommendations: list[AgentRecommendation],
        exclude_not_relevant: bool = True
    ) -> list[AgentRecommendation]:
        """
        Filter recommendations based on feedback.

        Args:
            recommendations: Original recommendations
            exclude_not_relevant: If True, remove agents rated as not relevant

        Returns:
            Filtered list of recommendations, sorted by feedback rating
        """
        if not self.session.feedbacks:
            return recommendations

        # Build rating map
        rating_map = {f.agent_type: f.rating for f in self.session.feedbacks}

        # Filter and sort
        filtered = []
        for rec in recommendations:
            rating = rating_map.get(rec.agent_type, "maybe")
            if exclude_not_relevant and rating == "not_relevant":
                continue
            filtered.append((rec, rating))

        # Sort: useful first, then maybe, then not_relevant
        rating_order = {"useful": 0, "maybe": 1, "not_relevant": 2}
        filtered.sort(key=lambda x: (rating_order[x[1]], -x[0].match_score))

        return [rec for rec, _ in filtered]


def create_feedback_collector(
    input_func: Callable[[], str] = input,
    print_func: Callable[[str], None] = print
) -> FeedbackCollector:
    """Factory function to create a FeedbackCollector."""
    return FeedbackCollector(input_func, print_func)


# =============================================================================
# NON-INTERACTIVE MODE
# =============================================================================

def create_auto_feedback(
    recommendations: list[AgentRecommendation],
    auto_useful_threshold: float = 0.6,
    auto_maybe_threshold: float = 0.3
) -> FeedbackSession:
    """
    Create automatic feedback based on match scores.

    Used in non-interactive mode.

    Args:
        recommendations: List of recommendations
        auto_useful_threshold: Score threshold for "useful" rating
        auto_maybe_threshold: Score threshold for "maybe" rating

    Returns:
        FeedbackSession with auto-generated feedbacks
    """
    session = FeedbackSession()

    for rec in recommendations:
        if rec.match_score >= auto_useful_threshold:
            rating = "useful"
        elif rec.match_score >= auto_maybe_threshold:
            rating = "maybe"
        else:
            rating = "not_relevant"

        session.feedbacks.append(UserFeedback(
            agent_type=rec.agent_type,
            agent_name=rec.name,
            rating=rating,
            comment="Auto-generated based on match score"
        ))

    return session
