"""
Batch Generator Module - Generate multiple agents in sequence.

This module allows:
- Sequential generation of multiple agents
- Progress tracking with visual feedback
- Error handling per agent (continue if one fails)
- Summary report at the end
"""

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Any

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from generators.agent_builder import AgentRecommendation, GeneratedAgent, AgentBuilder
from analyzers.doc_analyzer import ProjectProfile
from dialogue.needs_assessor import NeedsAssessment


@dataclass
class AgentGenerationStatus:
    """Status of a single agent generation."""
    agent_type: str
    agent_name: str
    status: str  # "pending", "in_progress", "success", "error"
    generated_agent: GeneratedAgent | None = None
    error_message: str | None = None
    duration_seconds: float = 0.0


@dataclass
class GenerationResult:
    """Result of batch generation."""
    statuses: list[AgentGenerationStatus] = field(default_factory=list)
    total_duration_seconds: float = 0.0

    @property
    def success_count(self) -> int:
        return sum(1 for s in self.statuses if s.status == "success")

    @property
    def error_count(self) -> int:
        return sum(1 for s in self.statuses if s.status == "error")

    @property
    def total_count(self) -> int:
        return len(self.statuses)

    def get_successful_agents(self) -> list[GeneratedAgent]:
        return [s.generated_agent for s in self.statuses if s.generated_agent]

    def is_fully_successful(self) -> bool:
        return self.error_count == 0


class BatchGenerator:
    """
    Generates multiple agents in batch with progress tracking.

    Provides visual feedback during generation and handles
    errors gracefully.
    """

    def __init__(
        self,
        builder: AgentBuilder,
        print_func: Callable[[str], None] = print
    ):
        self.builder = builder
        self.print_func = print_func

    def print_header(self, total: int) -> None:
        """Print generation header."""
        self.print_func(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    GÉNÉRATION DES AGENTS ({total} agent(s))                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
""")

    def print_progress_bar(self, current: int, total: int, width: int = 40) -> str:
        """Generate a progress bar string."""
        progress = current / total if total > 0 else 0
        filled = int(width * progress)
        bar = "█" * filled + "░" * (width - filled)
        percent = int(progress * 100)
        return f"[{bar}] {percent}%"

    def print_status_line(
        self,
        index: int,
        total: int,
        name: str,
        status: str,
        icon: str = "🤖"
    ) -> None:
        """Print a single agent status line."""
        status_icons = {
            "pending": "⏸️",
            "in_progress": "⏳",
            "success": "✅",
            "error": "❌"
        }
        status_icon = status_icons.get(status, "❓")

        # Truncate name if too long
        name = name[:35] + "..." if len(name) > 38 else name

        status_text = {
            "pending": "En attente",
            "in_progress": "En cours...",
            "success": "Généré",
            "error": "Erreur"
        }.get(status, status)

        self.print_func(f"║  {status_icon} {index}/{total} {icon} {name:<38} {status_text:<12} ║")

    def generate_batch(
        self,
        recommendations: list[AgentRecommendation],
        profile: ProjectProfile,
        assessment: NeedsAssessment,
        enterprise_rules: dict | None = None,
        expert_icons: dict[str, str] | None = None
    ) -> GenerationResult:
        """
        Generate multiple agents in sequence.

        Args:
            recommendations: List of recommendations to generate
            profile: Project profile
            assessment: Needs assessment
            enterprise_rules: Optional enterprise rules
            expert_icons: Optional dict mapping agent_type to icon

        Returns:
            GenerationResult with all statuses
        """
        expert_icons = expert_icons or {}
        total = len(recommendations)
        result = GenerationResult()

        # Initialize statuses
        for rec in recommendations:
            result.statuses.append(AgentGenerationStatus(
                agent_type=rec.agent_type,
                agent_name=rec.name,
                status="pending"
            ))

        self.print_header(total)

        start_time = time.time()

        # Generate each agent
        for i, rec in enumerate(recommendations):
            status = result.statuses[i]
            icon = expert_icons.get(rec.agent_type, "🤖")

            # Update status to in_progress
            status.status = "in_progress"

            # Print current progress
            self._print_current_state(result, i, total, expert_icons)

            # Generate agent
            agent_start = time.time()
            try:
                agent = self.builder.build(
                    rec,
                    profile,
                    assessment,
                    enterprise_rules
                )
                status.generated_agent = agent
                status.status = "success"

            except Exception as e:
                status.status = "error"
                status.error_message = str(e)

            status.duration_seconds = time.time() - agent_start

            # Small delay for visual effect
            time.sleep(0.2)

        result.total_duration_seconds = time.time() - start_time

        # Print final state
        self._print_current_state(result, total, total, expert_icons, final=True)

        return result

    def _print_current_state(
        self,
        result: GenerationResult,
        current: int,
        total: int,
        expert_icons: dict[str, str],
        final: bool = False
    ) -> None:
        """Print the current state of generation."""
        # Clear and reprint (simulated with newlines in terminal)
        progress = self.print_progress_bar(current, total)

        self.print_func(f"║  {progress}                            ║")
        self.print_func("║                                                                              ║")

        for i, status in enumerate(result.statuses):
            icon = expert_icons.get(status.agent_type, "🤖")
            self.print_status_line(i + 1, total, status.agent_name, status.status, icon)

        if not final:
            self.print_func("║                                                                              ║")

    def print_summary(self, result: GenerationResult) -> None:
        """Print generation summary."""
        self.print_func(f"""
╠══════════════════════════════════════════════════════════════════════════════╣
║                         RÉSUMÉ DE GÉNÉRATION                                 ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║   ✅ Générés avec succès: {result.success_count:2d} agent(s)                                    ║
║   ❌ Erreurs:             {result.error_count:2d} agent(s)                                    ║
║   ⏱️  Temps total:         {result.total_duration_seconds:5.1f}s                                       ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

        # Print errors if any
        if result.error_count > 0:
            self.print_func("\n⚠️  Erreurs rencontrées:")
            for status in result.statuses:
                if status.status == "error":
                    self.print_func(f"   • {status.agent_name}: {status.error_message}")


def create_batch_generator(
    builder: AgentBuilder,
    print_func: Callable[[str], None] = print
) -> BatchGenerator:
    """Factory function to create a BatchGenerator."""
    return BatchGenerator(builder, print_func)


# =============================================================================
# DEPLOYMENT UTILITIES
# =============================================================================

@dataclass
class DeploymentStatus:
    """Status of a single agent deployment."""
    agent_name: str
    deployed: bool
    path: Path | None = None
    error: str | None = None


@dataclass
class BatchDeploymentResult:
    """Result of batch deployment."""
    statuses: list[DeploymentStatus] = field(default_factory=list)
    output_dir: Path | None = None

    @property
    def success_count(self) -> int:
        return sum(1 for s in self.statuses if s.deployed)


def deploy_batch(
    agents: list[GeneratedAgent],
    output_dir: Path,
    print_func: Callable[[str], None] = print
) -> BatchDeploymentResult:
    """
    Deploy multiple generated agents.

    Args:
        agents: List of generated agents
        output_dir: Output directory for agents
        print_func: Print function for output

    Returns:
        BatchDeploymentResult with deployment statuses
    """
    result = BatchDeploymentResult(output_dir=output_dir)

    print_func(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    DÉPLOIEMENT DES AGENTS                                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
""")

    output_dir.mkdir(parents=True, exist_ok=True)

    for agent in agents:
        try:
            files = agent.to_files(output_dir)
            agent_dir = output_dir / f"agent-{agent.name.lower().replace(' ', '-')}"

            result.statuses.append(DeploymentStatus(
                agent_name=agent.name,
                deployed=True,
                path=agent_dir
            ))
            print_func(f"║   ✅ {agent.name:<50} Déployé    ║")

        except Exception as e:
            result.statuses.append(DeploymentStatus(
                agent_name=agent.name,
                deployed=False,
                error=str(e)
            ))
            print_func(f"║   ❌ {agent.name:<50} Erreur     ║")

    print_func("""║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

    return result


def print_deployment_instructions(
    result: BatchDeploymentResult,
    print_func: Callable[[str], None] = print
) -> None:
    """Print deployment instructions for all deployed agents."""
    print_func("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    INSTRUCTIONS DE DÉPLOIEMENT                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  🚀 UTILISATION AVEC CLAUDE CODE:                                           ║
║                                                                              ║
║     Copiez les agents dans votre projet:                                    ║""")

    for status in result.statuses:
        if status.deployed and status.path:
            print_func(f"║     cp -r \"{status.path}\" /votre/projet/.claude/                ║")

    print_func("""║                                                                              ║
║  📋 AGENTS GÉNÉRÉS:                                                         ║
║                                                                              ║""")

    for status in result.statuses:
        if status.deployed:
            print_func(f"║     • {status.agent_name:<60}   ║")

    print_func("""║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
