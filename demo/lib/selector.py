"""
Selector Module - Multi-selection of agents to generate.

This module allows users to:
- View all recommendations grouped by category
- Select multiple agents using comma-separated numbers
- Use shortcuts (A for all, H for high priority only)
"""

from dataclasses import dataclass, field
from typing import Callable

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from generators.agent_builder import AgentRecommendation


@dataclass
class SelectionResult:
    """Result of agent selection."""
    selected_indices: list[int]
    selected_recommendations: list[AgentRecommendation]
    total_available: int

    @property
    def count(self) -> int:
        return len(self.selected_recommendations)

    def is_empty(self) -> bool:
        return self.count == 0


class AgentSelector:
    """
    Interactive agent selector for multi-selection.

    Allows users to select multiple agents from recommendations
    using various input methods.
    """

    def __init__(
        self,
        input_func: Callable[[], str] = input,
        print_func: Callable[[str], None] = print
    ):
        self.input_func = input_func
        self.print_func = print_func

    def print_header(self) -> None:
        """Print selection section header."""
        self.print_func("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    SÉLECTION DES AGENTS À GÉNÉRER                            ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Cochez les agents que vous souhaitez générer.                              ║
║  Entrez les numéros séparés par des virgules (ex: 1,2,4)                    ║
║                                                                              ║
║  Raccourcis:                                                                 ║
║  [A] Sélectionner tous les agents                                           ║
║  [H] Sélectionner uniquement les HIGH priority                              ║
║  [U] Sélectionner les agents marqués "Très utile" (si feedback fait)        ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

    def display_recommendations(
        self,
        recommendations: list[AgentRecommendation],
        expert_icons: dict[str, str] | None = None,
        technical_types: list[str] | None = None
    ) -> None:
        """
        Display recommendations grouped by category.

        Args:
            recommendations: List of recommendations to display
            expert_icons: Optional dict mapping agent_type to icon
            technical_types: List of agent_types that are technical experts
        """
        expert_icons = expert_icons or {}
        technical_types = technical_types or []

        # Separate by category
        technical = []
        transversal = []

        for i, rec in enumerate(recommendations):
            if rec.agent_type in technical_types:
                technical.append((i + 1, rec))
            else:
                transversal.append((i + 1, rec))

        # Display technical experts
        if technical:
            self.print_func("\n📦 EXPERTS TECHNIQUES")
            self.print_func("─" * 70)
            for idx, rec in technical:
                self._display_single(idx, rec, expert_icons)

        # Display transversal assistants
        if transversal:
            self.print_func("\n🔧 ASSISTANTS TRANSVERSAUX")
            self.print_func("─" * 70)
            for idx, rec in transversal:
                self._display_single(idx, rec, expert_icons)

        self.print_func("")

    def _display_single(
        self,
        index: int,
        rec: AgentRecommendation,
        expert_icons: dict[str, str]
    ) -> None:
        """Display a single recommendation."""
        icon = expert_icons.get(rec.agent_type, "🤖")
        priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}[rec.priority]

        self.print_func(
            f"  [{index:2d}] {icon} {rec.name:<40} {priority_icon} {rec.priority.upper()}"
        )

    def get_selection(
        self,
        recommendations: list[AgentRecommendation],
        useful_agents: list[str] | None = None
    ) -> SelectionResult:
        """
        Get user selection of agents.

        Args:
            recommendations: Available recommendations
            useful_agents: List of agent_types marked as useful (from feedback)

        Returns:
            SelectionResult with selected recommendations
        """
        useful_agents = useful_agents or []
        total = len(recommendations)

        while True:
            self.print_func(f"\n   Sélection (1-{total}, A=tous, H=high, U=utiles): ")
            choice = self.input_func("   > ").strip().upper()

            # Handle shortcuts
            if choice == "A":
                indices = list(range(total))
                self.print_func(f"   ✓ Tous les {total} agents sélectionnés")
                break

            elif choice == "H":
                indices = [
                    i for i, rec in enumerate(recommendations)
                    if rec.priority == "high"
                ]
                if indices:
                    self.print_func(f"   ✓ {len(indices)} agent(s) HIGH priority sélectionné(s)")
                    break
                else:
                    self.print_func("   ⚠️  Aucun agent HIGH priority disponible")
                    continue

            elif choice == "U":
                if not useful_agents:
                    self.print_func("   ⚠️  Aucun feedback disponible, utilisez A ou H")
                    continue
                indices = [
                    i for i, rec in enumerate(recommendations)
                    if rec.agent_type in useful_agents
                ]
                if indices:
                    self.print_func(f"   ✓ {len(indices)} agent(s) 'Très utile' sélectionné(s)")
                    break
                else:
                    self.print_func("   ⚠️  Aucun agent marqué comme 'Très utile'")
                    continue

            elif choice == "":
                # Default: select all HIGH priority
                indices = [
                    i for i, rec in enumerate(recommendations)
                    if rec.priority == "high"
                ]
                if not indices:
                    indices = [0]  # At least select the first one
                self.print_func(f"   ✓ Sélection par défaut: {len(indices)} agent(s)")
                break

            else:
                # Parse comma-separated numbers
                try:
                    parts = [p.strip() for p in choice.split(",")]
                    indices = []
                    for part in parts:
                        if "-" in part:
                            # Handle ranges like "1-3"
                            start, end = part.split("-")
                            for n in range(int(start), int(end) + 1):
                                if 1 <= n <= total:
                                    indices.append(n - 1)
                        else:
                            n = int(part)
                            if 1 <= n <= total:
                                indices.append(n - 1)

                    if indices:
                        indices = list(set(indices))  # Remove duplicates
                        indices.sort()
                        self.print_func(f"   ✓ {len(indices)} agent(s) sélectionné(s)")
                        break
                    else:
                        self.print_func(f"   ⚠️  Numéros invalides. Entrez des valeurs entre 1 et {total}")

                except ValueError:
                    self.print_func("   ⚠️  Format invalide. Exemples: 1,2,4 ou 1-3 ou A")

        selected = [recommendations[i] for i in indices]

        return SelectionResult(
            selected_indices=indices,
            selected_recommendations=selected,
            total_available=total
        )

    def confirm_selection(self, result: SelectionResult) -> bool:
        """
        Confirm the selection with user.

        Returns:
            True if confirmed, False to re-select
        """
        self.print_func(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    CONFIRMATION DE SÉLECTION                                 ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║   {result.count} agent(s) sélectionné(s) sur {result.total_available} disponible(s):                               ║
║                                                                              ║""")

        for rec in result.selected_recommendations:
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}[rec.priority]
            name = rec.name[:50]
            self.print_func(f"║   • {name:<50} {priority_icon}   ║")

        self.print_func("""║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

        choice = self.input_func("   Confirmer? (O/n): ").strip().lower()
        return choice != "n"

    def run_selection(
        self,
        recommendations: list[AgentRecommendation],
        expert_icons: dict[str, str] | None = None,
        technical_types: list[str] | None = None,
        useful_agents: list[str] | None = None
    ) -> SelectionResult:
        """
        Run the full selection process.

        Args:
            recommendations: Available recommendations
            expert_icons: Optional dict mapping agent_type to icon
            technical_types: List of agent_types that are technical experts
            useful_agents: List of agent_types marked as useful

        Returns:
            Final SelectionResult after confirmation
        """
        self.print_header()
        self.display_recommendations(recommendations, expert_icons, technical_types)

        while True:
            result = self.get_selection(recommendations, useful_agents)

            if result.is_empty():
                self.print_func("   ⚠️  Aucun agent sélectionné. Veuillez en choisir au moins un.")
                continue

            if self.confirm_selection(result):
                return result


def create_selector(
    input_func: Callable[[], str] = input,
    print_func: Callable[[str], None] = print
) -> AgentSelector:
    """Factory function to create an AgentSelector."""
    return AgentSelector(input_func, print_func)


# =============================================================================
# NON-INTERACTIVE MODE
# =============================================================================

def auto_select(
    recommendations: list[AgentRecommendation],
    max_agents: int = 5,
    min_priority: str = "medium"
) -> SelectionResult:
    """
    Automatically select agents based on priority.

    Used in non-interactive mode.

    Args:
        recommendations: Available recommendations
        max_agents: Maximum number of agents to select
        min_priority: Minimum priority level ("high", "medium", "low")

    Returns:
        SelectionResult with auto-selected agents
    """
    priority_order = {"high": 0, "medium": 1, "low": 2}
    min_priority_value = priority_order.get(min_priority, 1)

    # Filter by priority
    eligible = [
        (i, rec) for i, rec in enumerate(recommendations)
        if priority_order.get(rec.priority, 2) <= min_priority_value
    ]

    # Sort by score and take top N
    eligible.sort(key=lambda x: x[1].match_score, reverse=True)
    selected = eligible[:max_agents]

    return SelectionResult(
        selected_indices=[i for i, _ in selected],
        selected_recommendations=[rec for _, rec in selected],
        total_available=len(recommendations)
    )
