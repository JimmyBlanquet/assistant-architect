"""
Orchestrator - Central coordinator for the Assistant Architect workflow.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

try:
    from .llm_abstraction import LLMProvider, get_provider
    from ..analyzers.doc_analyzer import DocumentationAnalyzer, ProjectProfile
    from ..dialogue.needs_assessor import NeedsAssessor, AdaptiveNeedsAssessor, NeedsAssessment
    from ..generators.agent_builder import AgentRecommender, AgentBuilder, AgentRecommendation, GeneratedAgent
except ImportError:
    from core.llm_abstraction import LLMProvider, get_provider
    from analyzers.doc_analyzer import DocumentationAnalyzer, ProjectProfile
    from dialogue.needs_assessor import NeedsAssessor, AdaptiveNeedsAssessor, NeedsAssessment
    from generators.agent_builder import AgentRecommender, AgentBuilder, AgentRecommendation, GeneratedAgent


@dataclass
class WorkflowState:
    """Current state of the workflow."""
    phase: str = "init"  # init, analyzing, dialogue, recommending, generating, validating, deploying, complete
    project_profile: ProjectProfile | None = None
    needs_assessment: NeedsAssessment | None = None
    recommendations: list[AgentRecommendation] | None = None
    selected_agent: AgentRecommendation | None = None
    generated_agent: GeneratedAgent | None = None
    validation_status: str | None = None
    deployment_path: Path | None = None
    error: str | None = None


class Orchestrator:
    """
    Central orchestrator that coordinates the full workflow:
    1. Analyze documentation
    2. Conduct needs dialogue
    3. Recommend agents
    4. Generate selected agent
    5. Validate (approval workflow)
    6. Deploy to target environment
    """

    def __init__(
        self,
        llm: LLMProvider | None = None,
        enterprise_rules_path: Path | None = None,
        output_dir: Path | None = None
    ):
        self.llm = llm or get_provider("claude")
        self.enterprise_rules_path = enterprise_rules_path
        self.output_dir = output_dir or Path("./generated-agents")
        self.state = WorkflowState()

        # Initialize components
        self.analyzer = DocumentationAnalyzer(self.llm)
        self.recommender = AgentRecommender(self.llm)
        self.builder = AgentBuilder(self.llm)

        # Load enterprise rules if provided
        self.enterprise_rules = self._load_enterprise_rules()

    def _load_enterprise_rules(self) -> dict | None:
        """Load enterprise rules from file."""
        if not self.enterprise_rules_path or not self.enterprise_rules_path.exists():
            return None

        import yaml
        with open(self.enterprise_rules_path) as f:
            return yaml.safe_load(f)

    # =========================================================================
    # Phase 1: Analysis
    # =========================================================================

    def analyze_documentation(self, doc_source: Path | str) -> ProjectProfile:
        """Analyze project documentation."""
        self.state.phase = "analyzing"

        try:
            if isinstance(doc_source, Path):
                if doc_source.is_dir():
                    profile = self.analyzer.analyze_directory(doc_source)
                else:
                    content = doc_source.read_text()
                    source_type = "html" if doc_source.suffix == ".html" else "markdown"
                    profile = self.analyzer.analyze_content(content, source_type)
            else:
                # Assume string content is markdown
                profile = self.analyzer.analyze_content(doc_source, "markdown")

            self.state.project_profile = profile
            return profile

        except Exception as e:
            self.state.error = f"Analysis failed: {e}"
            raise

    # =========================================================================
    # Phase 2: Dialogue
    # =========================================================================

    def conduct_dialogue(
        self,
        input_func: Callable[[], str] = input,
        print_func: Callable[[str], None] = print,
        adaptive: bool = True
    ) -> NeedsAssessment:
        """Conduct needs assessment dialogue."""
        self.state.phase = "dialogue"

        if adaptive and self.state.project_profile:
            assessor = AdaptiveNeedsAssessor(self.llm, self.state.project_profile)
        else:
            assessor = NeedsAssessor(self.llm)

        assessment = assessor.run_interactive(input_func, print_func)
        self.state.needs_assessment = assessment
        return assessment

    def set_assessment(self, assessment: NeedsAssessment) -> None:
        """Set assessment directly (for non-interactive mode)."""
        self.state.needs_assessment = assessment

    # =========================================================================
    # Phase 3: Recommendation
    # =========================================================================

    def get_recommendations(self, max_recommendations: int = 3) -> list[AgentRecommendation]:
        """Generate agent recommendations."""
        self.state.phase = "recommending"

        if not self.state.project_profile:
            raise ValueError("No project profile available. Run analyze_documentation first.")
        if not self.state.needs_assessment:
            raise ValueError("No needs assessment available. Run conduct_dialogue first.")

        recommendations = self.recommender.recommend(
            self.state.project_profile,
            self.state.needs_assessment,
            max_recommendations
        )

        self.state.recommendations = recommendations
        return recommendations

    def format_recommendations(self) -> str:
        """Format recommendations for display."""
        if not self.state.recommendations:
            return "No recommendations available."
        return self.recommender.format_recommendations(self.state.recommendations)

    def select_agent(self, index: int) -> AgentRecommendation:
        """Select an agent from recommendations."""
        if not self.state.recommendations:
            raise ValueError("No recommendations available.")
        if index < 0 or index >= len(self.state.recommendations):
            raise ValueError(f"Invalid index. Must be 0-{len(self.state.recommendations)-1}")

        self.state.selected_agent = self.state.recommendations[index]
        return self.state.selected_agent

    # =========================================================================
    # Phase 4: Generation
    # =========================================================================

    def generate_agent(self) -> GeneratedAgent:
        """Generate the selected agent."""
        self.state.phase = "generating"

        if not self.state.selected_agent:
            raise ValueError("No agent selected. Run select_agent first.")
        if not self.state.project_profile or not self.state.needs_assessment:
            raise ValueError("Missing profile or assessment.")

        agent = self.builder.build(
            self.state.selected_agent,
            self.state.project_profile,
            self.state.needs_assessment,
            self.enterprise_rules
        )

        self.state.generated_agent = agent
        return agent

    # =========================================================================
    # Phase 5: Validation
    # =========================================================================

    def get_validation_summary(self) -> str:
        """Generate summary for validation/approval."""
        if not self.state.generated_agent:
            return "No agent generated."

        agent = self.state.generated_agent
        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║           VALIDATION - AGENT GÉNÉRÉ                          ║
╚══════════════════════════════════════════════════════════════╝

📋 INFORMATIONS GÉNÉRALES
   • Nom: {agent.name}
   • Type: {agent.type}
   • Version: {agent.config.get('version', '1.0.0')}

🤖 CONFIGURATION LLM
   • Provider: {agent.config.get('llm', {}).get('provider', 'N/A')}
   • Model: {agent.config.get('llm', {}).get('model', 'N/A')}
   • Temperature: {agent.config.get('llm', {}).get('temperature', 'N/A')}

📝 COMMANDES DISPONIBLES
{chr(10).join(f'   • /{cmd}' for cmd in agent.commands.keys()) or '   Aucune'}

📚 BASE DE CONNAISSANCES
{chr(10).join(f'   • {f}' for f in agent.knowledge.keys()) or '   Aucune'}

🔒 RÈGLES APPLIQUÉES
{chr(10).join(f'   • {r}' for r in agent.rules.keys()) or '   Aucune'}

🔗 HOOKS MÉTRIQUES
{chr(10).join(f'   • {h}' for h in agent.hooks.keys()) or '   Aucun'}

══════════════════════════════════════════════════════════════
"""
        return summary

    def validate(self, approved: bool, validator: str = "architect") -> bool:
        """Record validation decision."""
        self.state.phase = "validating"
        self.state.validation_status = "approved" if approved else "rejected"

        if approved:
            # Log approval (placeholder for audit)
            print(f"[AUDIT] Agent approved by {validator} at {__import__('datetime').datetime.now()}")

        return approved

    # =========================================================================
    # Phase 6: Deployment
    # =========================================================================

    def deploy(self, target_path: Path | None = None) -> Path:
        """Deploy the generated agent."""
        self.state.phase = "deploying"

        if not self.state.generated_agent:
            raise ValueError("No agent generated.")
        if self.state.validation_status != "approved":
            raise ValueError("Agent must be approved before deployment.")

        output_path = target_path or self.output_dir
        output_path.mkdir(parents=True, exist_ok=True)

        files = self.state.generated_agent.to_files(output_path)

        self.state.deployment_path = output_path
        self.state.phase = "complete"

        return output_path

    def get_deployment_instructions(self) -> str:
        """Get instructions for using the deployed agent."""
        if not self.state.deployment_path or not self.state.generated_agent:
            return "No deployment available."

        agent_dir = self.state.deployment_path / f"agent-{self.state.generated_agent.name.lower().replace(' ', '-')}"

        return f"""
╔══════════════════════════════════════════════════════════════╗
║           INSTRUCTIONS DE DÉPLOIEMENT                        ║
╚══════════════════════════════════════════════════════════════╝

✅ Agent généré avec succès!

📁 Emplacement: {agent_dir}

🚀 UTILISATION AVEC CLAUDE CODE:

   1. Copiez le dossier dans votre projet:
      cp -r "{agent_dir}" /votre/projet/.claude/

   2. Ou créez un lien symbolique:
      ln -s "{agent_dir}" /votre/projet/.claude/

🖥️  UTILISATION AVEC VS CODE:

   1. Ouvrez les paramètres VS Code
   2. Recherchez "Claude" ou "AI Assistant"
   3. Pointez vers: {agent_dir}/config.json

📋 COMMANDES DISPONIBLES:
{chr(10).join(f'   /{cmd}' for cmd in self.state.generated_agent.commands.keys())}

══════════════════════════════════════════════════════════════
"""

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def get_status(self) -> str:
        """Get current workflow status."""
        status_icons = {
            "init": "⏳",
            "analyzing": "🔍",
            "dialogue": "💬",
            "recommending": "🎯",
            "generating": "⚙️",
            "validating": "✅",
            "deploying": "🚀",
            "complete": "✨"
        }

        return f"{status_icons.get(self.state.phase, '❓')} Phase: {self.state.phase}"

    def reset(self) -> None:
        """Reset the workflow state."""
        self.state = WorkflowState()


def create_orchestrator(
    provider: str = "claude",
    enterprise_rules_path: Path | None = None,
    output_dir: Path | None = None,
    **provider_kwargs
) -> Orchestrator:
    """Factory function to create an orchestrator."""
    llm = get_provider(provider, **provider_kwargs)
    return Orchestrator(llm, enterprise_rules_path, output_dir)
