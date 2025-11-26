"""
Needs Assessor - Dialogue system to clarify user requirements.
Conducts structured conversation to understand team needs and constraints.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable

try:
    from ..analyzers.doc_analyzer import ProjectProfile
    from ..core.llm_abstraction import LLMProvider, Message
except ImportError:
    from analyzers.doc_analyzer import ProjectProfile
    from core.llm_abstraction import LLMProvider, Message


class DialoguePhase(Enum):
    CONTEXT = "context"
    PAIN_POINTS = "pain_points"
    PRIORITIES = "priorities"
    CONSTRAINTS = "constraints"
    VALIDATION = "validation"
    COMPLETE = "complete"


@dataclass
class Question:
    """A question to ask the user."""
    id: str
    phase: DialoguePhase
    text: str
    options: list[str] | None = None  # If None, free-form answer
    required: bool = True
    follow_up: str | None = None  # Conditional follow-up question


@dataclass
class NeedsAssessment:
    """Results of the needs assessment dialogue."""
    team_size: str = ""
    experience_level: str = ""
    main_pain_points: list[str] = field(default_factory=list)
    priorities: list[str] = field(default_factory=list)
    constraints: dict[str, str] = field(default_factory=dict)
    sensitive_data: bool = False
    compliance_requirements: list[str] = field(default_factory=list)
    preferred_workflow: str = ""
    additional_context: str = ""
    raw_answers: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "team_size": self.team_size,
            "experience_level": self.experience_level,
            "main_pain_points": self.main_pain_points,
            "priorities": self.priorities,
            "constraints": self.constraints,
            "sensitive_data": self.sensitive_data,
            "compliance_requirements": self.compliance_requirements,
            "preferred_workflow": self.preferred_workflow,
            "additional_context": self.additional_context
        }


class NeedsAssessor:
    """Conducts structured dialogue to assess team needs."""

    def __init__(self, llm: LLMProvider | None = None):
        self.llm = llm
        self.questions = self._build_questions()
        self.current_phase = DialoguePhase.CONTEXT
        self.assessment = NeedsAssessment()
        self.conversation_history: list[Message] = []

    def _build_questions(self) -> list[Question]:
        """Build the standard question set."""
        return [
            # Context Phase
            Question(
                id="team_size",
                phase=DialoguePhase.CONTEXT,
                text="Quelle est la taille de votre équipe de développement ?",
                options=["1-3 (petite)", "4-8 (moyenne)", "9-20 (grande)", "20+ (très grande)"]
            ),
            Question(
                id="experience_level",
                phase=DialoguePhase.CONTEXT,
                text="Quel est le niveau d'expérience moyen de l'équipe sur ce projet ?",
                options=["Junior (< 2 ans)", "Intermédiaire (2-5 ans)", "Senior (5+ ans)", "Mixte"]
            ),

            # Pain Points Phase
            Question(
                id="main_difficulty",
                phase=DialoguePhase.PAIN_POINTS,
                text="Qu'est-ce qui ralentit le plus votre équipe actuellement ?",
                options=[
                    "Debugging/résolution d'incidents",
                    "Code reviews et qualité",
                    "Écriture des tests",
                    "Compréhension du code existant",
                    "Documentation",
                    "Autre"
                ]
            ),
            Question(
                id="secondary_difficulties",
                phase=DialoguePhase.PAIN_POINTS,
                text="Y a-t-il d'autres difficultés importantes ?",
                options=None  # Free-form
            ),

            # Priorities Phase
            Question(
                id="priority",
                phase=DialoguePhase.PRIORITIES,
                text="Quelle est votre priorité principale ?",
                options=[
                    "Rapidité de développement",
                    "Qualité du code",
                    "Réduction des bugs",
                    "Montée en compétence de l'équipe",
                    "Maintenance du legacy"
                ]
            ),

            # Constraints Phase
            Question(
                id="sensitive_data",
                phase=DialoguePhase.CONSTRAINTS,
                text="Le projet traite-t-il des données sensibles ?",
                options=["Oui - données bancaires/financières", "Oui - données personnelles (RGPD)", "Oui - autres données sensibles", "Non"]
            ),
            Question(
                id="compliance",
                phase=DialoguePhase.CONSTRAINTS,
                text="Y a-t-il des exigences de compliance spécifiques ?",
                options=["RGPD", "PCI-DSS", "SOC2", "Normes internes", "Aucune", "Autre"]
            ),

            # Validation Phase
            Question(
                id="workflow_preference",
                phase=DialoguePhase.VALIDATION,
                text="Comment préférez-vous interagir avec l'assistant IA ?",
                options=["CLI (ligne de commande)", "VS Code / IDE", "Les deux"]
            ),
            Question(
                id="confirmation",
                phase=DialoguePhase.VALIDATION,
                text="Ces informations sont-elles correctes ? Voulez-vous ajouter quelque chose ?",
                options=None  # Free-form
            ),
        ]

    def get_current_question(self) -> Question | None:
        """Get the next unanswered question."""
        answered_ids = set(self.assessment.raw_answers.keys())

        for question in self.questions:
            if question.id not in answered_ids:
                self.current_phase = question.phase
                return question

        self.current_phase = DialoguePhase.COMPLETE
        return None

    def process_answer(self, question_id: str, answer: str) -> None:
        """Process and store an answer."""
        self.assessment.raw_answers[question_id] = answer

        # Map answers to assessment fields
        if question_id == "team_size":
            self.assessment.team_size = answer
        elif question_id == "experience_level":
            self.assessment.experience_level = answer
        elif question_id == "main_difficulty":
            self.assessment.main_pain_points.append(answer)
        elif question_id == "secondary_difficulties":
            if answer.strip():
                self.assessment.additional_context = answer
        elif question_id == "priority":
            self.assessment.priorities.append(answer)
        elif question_id == "sensitive_data":
            self.assessment.sensitive_data = "oui" in answer.lower()
            if self.assessment.sensitive_data:
                self.assessment.constraints["data_sensitivity"] = answer
        elif question_id == "compliance":
            if answer.lower() not in ["aucune", "non"]:
                self.assessment.compliance_requirements.append(answer)
        elif question_id == "workflow_preference":
            self.assessment.preferred_workflow = answer
        elif question_id == "confirmation":
            if answer.strip():
                self.assessment.additional_context += f"\n{answer}"

    def format_question_for_display(self, question: Question) -> str:
        """Format a question for CLI display."""
        output = f"\n{'='*60}\n"
        output += f"[{question.phase.value.upper()}] {question.text}\n"
        output += f"{'='*60}\n"

        if question.options:
            for i, option in enumerate(question.options, 1):
                output += f"  {i}. {option}\n"
            output += "\nEntrez le numéro de votre choix (ou texte libre) : "
        else:
            output += "Votre réponse : "

        return output

    def parse_option_answer(self, question: Question, answer: str) -> str:
        """Parse answer and convert option number to text if needed."""
        if question.options and answer.isdigit():
            idx = int(answer) - 1
            if 0 <= idx < len(question.options):
                return question.options[idx]
        return answer

    def generate_summary(self) -> str:
        """Generate a summary of the assessment."""
        summary = """
╔══════════════════════════════════════════════════════════════╗
║               RÉSUMÉ DE L'ÉVALUATION DES BESOINS             ║
╚══════════════════════════════════════════════════════════════╝

📊 CONTEXTE ÉQUIPE
   • Taille : {team_size}
   • Expérience : {experience_level}

🎯 DIFFICULTÉS IDENTIFIÉES
{pain_points}

⚡ PRIORITÉS
{priorities}

🔒 CONTRAINTES
   • Données sensibles : {sensitive}
   • Compliance : {compliance}

💻 PRÉFÉRENCES
   • Workflow : {workflow}

📝 NOTES ADDITIONNELLES
   {notes}
""".format(
            team_size=self.assessment.team_size or "Non spécifié",
            experience_level=self.assessment.experience_level or "Non spécifié",
            pain_points="\n".join(f"   • {p}" for p in self.assessment.main_pain_points) or "   • Aucune spécifiée",
            priorities="\n".join(f"   • {p}" for p in self.assessment.priorities) or "   • Aucune spécifiée",
            sensitive="Oui" if self.assessment.sensitive_data else "Non",
            compliance=", ".join(self.assessment.compliance_requirements) or "Aucune",
            workflow=self.assessment.preferred_workflow or "Non spécifié",
            notes=self.assessment.additional_context.strip() or "Aucune"
        )
        return summary

    def run_interactive(self, input_func: Callable[[], str] = input, print_func: Callable[[str], None] = print) -> NeedsAssessment:
        """Run interactive assessment in CLI mode."""
        print_func("\n🤖 Assistant Architect - Évaluation des Besoins\n")
        print_func("Je vais vous poser quelques questions pour comprendre vos besoins.\n")

        while True:
            question = self.get_current_question()
            if question is None:
                break

            prompt = self.format_question_for_display(question)
            print_func(prompt)

            answer = input_func().strip()
            if not answer and question.required:
                print_func("⚠️  Cette question requiert une réponse.\n")
                continue

            parsed_answer = self.parse_option_answer(question, answer)
            self.process_answer(question.id, parsed_answer)

        print_func(self.generate_summary())
        return self.assessment


class AdaptiveNeedsAssessor(NeedsAssessor):
    """Enhanced assessor that adapts questions based on project profile."""

    def __init__(self, llm: LLMProvider, project_profile: ProjectProfile):
        super().__init__(llm)
        self.project_profile = project_profile
        self._adapt_questions()

    def _adapt_questions(self) -> None:
        """Adapt questions based on project analysis."""
        # Add technology-specific questions
        if "Kafka" in self.project_profile.stack or "event-driven" in self.project_profile.patterns:
            self.questions.insert(3, Question(
                id="messaging_difficulty",
                phase=DialoguePhase.PAIN_POINTS,
                text="Rencontrez-vous des difficultés avec le messaging/events ?",
                options=["Oui - debugging complexe", "Oui - performance", "Oui - compréhension des flux", "Non"]
            ))

        if self.project_profile.complexity == "high":
            self.questions.insert(4, Question(
                id="onboarding_issue",
                phase=DialoguePhase.PAIN_POINTS,
                text="La montée en compétence des nouveaux développeurs est-elle un problème ?",
                options=["Oui - très longue", "Oui - documentation insuffisante", "Non - processus OK"]
            ))

        # Add compliance question if banking/financial detected
        if any(term in str(self.project_profile.stack).lower() for term in ["bank", "financ", "payment"]):
            idx = next((i for i, q in enumerate(self.questions) if q.id == "compliance"), len(self.questions))
            self.questions.insert(idx + 1, Question(
                id="pci_compliance",
                phase=DialoguePhase.CONSTRAINTS,
                text="Le projet doit-il être conforme PCI-DSS pour les paiements ?",
                options=["Oui", "Non", "En cours de certification"]
            ))
