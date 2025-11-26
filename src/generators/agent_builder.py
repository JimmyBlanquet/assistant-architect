"""
Agent Builder - Generates specialized AI agents based on project profile and needs.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    from ..analyzers.doc_analyzer import ProjectProfile
    from ..dialogue.needs_assessor import NeedsAssessment
    from ..core.llm_abstraction import LLMProvider
except ImportError:
    from analyzers.doc_analyzer import ProjectProfile
    from dialogue.needs_assessor import NeedsAssessment
    from core.llm_abstraction import LLMProvider


@dataclass
class AgentCapability:
    """A capability/skill for an agent."""
    name: str
    description: str
    trigger: str  # When this capability is relevant
    priority: int = 5  # 1-10, higher = more important


@dataclass
class AgentRecommendation:
    """A recommended agent type with justification."""
    agent_type: str
    name: str
    description: str
    priority: str  # "high", "medium", "low"
    justification: str
    capabilities: list[AgentCapability] = field(default_factory=list)
    match_score: float = 0.0


@dataclass
class GeneratedAgent:
    """A fully generated agent ready for deployment."""
    name: str
    type: str
    system_prompt: str
    config: dict[str, Any]
    commands: dict[str, str]  # command_name -> prompt
    knowledge: dict[str, str]  # filename -> content
    rules: dict[str, Any]
    hooks: dict[str, str]  # hook_name -> script content

    def to_files(self, output_dir: Path) -> dict[str, Path]:
        """Export agent to file structure."""
        agent_dir = output_dir / f"agent-{self.name.lower().replace(' ', '-')}"
        agent_dir.mkdir(parents=True, exist_ok=True)

        created_files = {}

        # AGENT.md - System prompt
        agent_md = agent_dir / "AGENT.md"
        agent_md.write_text(self.system_prompt)
        created_files["system_prompt"] = agent_md

        # config.json
        config_file = agent_dir / "config.json"
        config_file.write_text(json.dumps(self.config, indent=2))
        created_files["config"] = config_file

        # Commands
        if self.commands:
            commands_dir = agent_dir / "commands"
            commands_dir.mkdir(exist_ok=True)
            for cmd_name, cmd_content in self.commands.items():
                cmd_file = commands_dir / f"{cmd_name}.md"
                cmd_file.write_text(cmd_content)
                created_files[f"command_{cmd_name}"] = cmd_file

        # Knowledge
        if self.knowledge:
            knowledge_dir = agent_dir / "knowledge"
            knowledge_dir.mkdir(exist_ok=True)
            for filename, content in self.knowledge.items():
                knowledge_file = knowledge_dir / filename
                knowledge_file.write_text(content)
                created_files[f"knowledge_{filename}"] = knowledge_file

        # Rules
        if self.rules:
            rules_dir = agent_dir / "rules"
            rules_dir.mkdir(exist_ok=True)
            for rule_name, rule_content in self.rules.items():
                if isinstance(rule_content, dict):
                    rule_file = rules_dir / f"{rule_name}.yaml"
                    import yaml
                    rule_file.write_text(yaml.dump(rule_content, default_flow_style=False, allow_unicode=True))
                else:
                    rule_file = rules_dir / f"{rule_name}.md"
                    rule_file.write_text(str(rule_content))
                created_files[f"rule_{rule_name}"] = rule_file

        # Hooks
        if self.hooks:
            hooks_dir = agent_dir / "hooks"
            hooks_dir.mkdir(exist_ok=True)
            for hook_name, hook_content in self.hooks.items():
                hook_file = hooks_dir / f"{hook_name}.sh"
                hook_file.write_text(hook_content)
                hook_file.chmod(0o755)
                created_files[f"hook_{hook_name}"] = hook_file

        return created_files


class AgentCatalog:
    """Catalog of available agent types and their capabilities."""

    AGENT_TYPES = {
        "debug-helper": {
            "name": "Debug Helper",
            "description": "Aide au debugging et à la résolution d'incidents",
            "triggers": ["debugging", "incidents", "logs", "errors", "stack complexe"],
            "capabilities": [
                AgentCapability("log-analysis", "Analyse des logs d'erreur", "error logs", 9),
                AgentCapability("stack-trace", "Interprétation des stack traces", "exception", 9),
                AgentCapability("root-cause", "Identification de la cause racine", "bug", 8),
                AgentCapability("fix-suggestion", "Suggestion de correctifs", "fix needed", 7),
            ]
        },
        "code-reviewer": {
            "name": "Code Reviewer",
            "description": "Review de code et amélioration de la qualité",
            "triggers": ["code review", "qualité", "standards", "équipe junior"],
            "capabilities": [
                AgentCapability("style-check", "Vérification du style de code", "code style", 8),
                AgentCapability("best-practices", "Suggestions de bonnes pratiques", "improvement", 8),
                AgentCapability("security-scan", "Détection de problèmes de sécurité", "security", 9),
                AgentCapability("performance", "Suggestions d'optimisation", "slow", 7),
            ]
        },
        "test-generator": {
            "name": "Test Generator",
            "description": "Génération et amélioration des tests",
            "triggers": ["tests", "coverage", "TDD", "qualité"],
            "capabilities": [
                AgentCapability("unit-tests", "Génération de tests unitaires", "unit test", 9),
                AgentCapability("integration-tests", "Tests d'intégration", "integration", 8),
                AgentCapability("edge-cases", "Identification des cas limites", "edge case", 8),
                AgentCapability("mocking", "Génération de mocks", "mock", 7),
            ]
        },
        "onboarding-guide": {
            "name": "Onboarding Guide",
            "description": "Aide à la montée en compétence sur le projet",
            "triggers": ["legacy", "onboarding", "nouveau", "compréhension"],
            "capabilities": [
                AgentCapability("architecture-explain", "Explication de l'architecture", "architecture", 9),
                AgentCapability("code-walkthrough", "Parcours du code", "understand", 8),
                AgentCapability("conventions", "Explication des conventions", "convention", 7),
                AgentCapability("history", "Contexte historique du projet", "why", 6),
            ]
        },
        "security-checker": {
            "name": "Security Checker",
            "description": "Vérification de la sécurité du code",
            "triggers": ["sécurité", "données sensibles", "compliance", "RGPD", "PCI"],
            "capabilities": [
                AgentCapability("vulnerability-scan", "Détection de vulnérabilités", "security", 10),
                AgentCapability("secrets-detection", "Détection de secrets exposés", "secret", 10),
                AgentCapability("compliance-check", "Vérification de conformité", "compliance", 9),
                AgentCapability("data-flow", "Analyse des flux de données", "data", 8),
            ]
        },
    }

    @classmethod
    def get_all_types(cls) -> list[str]:
        return list(cls.AGENT_TYPES.keys())

    @classmethod
    def get_agent_info(cls, agent_type: str) -> dict | None:
        return cls.AGENT_TYPES.get(agent_type)


class AgentRecommender:
    """Recommends appropriate agents based on project profile and needs."""

    def __init__(self, llm: LLMProvider | None = None):
        self.llm = llm
        self.catalog = AgentCatalog()

    def recommend(
        self,
        profile: ProjectProfile,
        assessment: NeedsAssessment,
        max_recommendations: int = 3
    ) -> list[AgentRecommendation]:
        """Generate agent recommendations."""
        recommendations = []

        for agent_type, info in AgentCatalog.AGENT_TYPES.items():
            score = self._calculate_match_score(agent_type, info, profile, assessment)

            if score > 0:
                priority = "high" if score > 0.7 else "medium" if score > 0.4 else "low"
                justification = self._generate_justification(agent_type, info, profile, assessment, score)

                recommendations.append(AgentRecommendation(
                    agent_type=agent_type,
                    name=info["name"],
                    description=info["description"],
                    priority=priority,
                    justification=justification,
                    capabilities=[AgentCapability(**cap.__dict__) for cap in info["capabilities"]],
                    match_score=score
                ))

        # Sort by score and return top N
        recommendations.sort(key=lambda x: x.match_score, reverse=True)
        return recommendations[:max_recommendations]

    def _calculate_match_score(
        self,
        agent_type: str,
        info: dict,
        profile: ProjectProfile,
        assessment: NeedsAssessment
    ) -> float:
        """Calculate how well an agent type matches the context."""
        score = 0.0
        triggers = info["triggers"]

        # Check profile matches
        profile_text = " ".join([
            " ".join(profile.stack),
            " ".join(profile.patterns),
            " ".join(profile.pain_points),
            profile.complexity,
            " ".join(profile.features)
        ]).lower()

        for trigger in triggers:
            if trigger.lower() in profile_text:
                score += 0.2

        # Check assessment matches
        assessment_text = " ".join([
            " ".join(assessment.main_pain_points),
            " ".join(assessment.priorities),
            assessment.additional_context
        ]).lower()

        for trigger in triggers:
            if trigger.lower() in assessment_text:
                score += 0.3

        # Specific adjustments
        if agent_type == "debug-helper" and profile.complexity == "high":
            score += 0.2

        if agent_type == "security-checker" and assessment.sensitive_data:
            score += 0.4

        if agent_type == "onboarding-guide" and "mixte" in assessment.experience_level.lower():
            score += 0.2

        if agent_type == "test-generator" and "test" in assessment_text:
            score += 0.3

        return min(score, 1.0)

    def _generate_justification(
        self,
        agent_type: str,
        info: dict,
        profile: ProjectProfile,
        assessment: NeedsAssessment,
        score: float
    ) -> str:
        """Generate human-readable justification for recommendation."""
        reasons = []

        if agent_type == "debug-helper":
            if profile.complexity == "high":
                reasons.append("complexité élevée du projet")
            if "debugging" in " ".join(assessment.main_pain_points).lower():
                reasons.append("debugging identifié comme difficulté principale")

        elif agent_type == "code-reviewer":
            if "junior" in assessment.experience_level.lower() or "mixte" in assessment.experience_level.lower():
                reasons.append("équipe avec profils mixtes")
            if "qualité" in " ".join(assessment.priorities).lower():
                reasons.append("qualité du code prioritaire")

        elif agent_type == "test-generator":
            if "test" in " ".join(assessment.main_pain_points).lower():
                reasons.append("tests identifiés comme point de friction")

        elif agent_type == "onboarding-guide":
            if profile.complexity in ["high", "medium"]:
                reasons.append("projet complexe nécessitant une montée en compétence")

        elif agent_type == "security-checker":
            if assessment.sensitive_data:
                reasons.append("données sensibles à protéger")
            if assessment.compliance_requirements:
                reasons.append(f"compliance requise: {', '.join(assessment.compliance_requirements)}")

        if not reasons:
            reasons.append(f"score de correspondance: {score:.0%}")

        return f"Recommandé car: {'; '.join(reasons)}"

    def format_recommendations(self, recommendations: list[AgentRecommendation]) -> str:
        """Format recommendations for display."""
        output = """
╔══════════════════════════════════════════════════════════════╗
║              AGENTS IA RECOMMANDÉS                           ║
╚══════════════════════════════════════════════════════════════╝
"""
        for i, rec in enumerate(recommendations, 1):
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}[rec.priority]
            output += f"""
{i}. {rec.name} {priority_icon} [{rec.priority.upper()}]
   {rec.description}

   📋 Justification: {rec.justification}

   🛠️  Capacités:
"""
            for cap in rec.capabilities[:3]:
                output += f"      • {cap.name}: {cap.description}\n"

        output += "\n" + "="*60
        return output


class AgentBuilder:
    """Builds complete agent configurations."""

    def __init__(self, llm: LLMProvider | None = None, templates_dir: Path | None = None):
        self.llm = llm
        self.templates_dir = templates_dir or Path(__file__).parent.parent.parent / "knowledge" / "templates"

    def build(
        self,
        recommendation: AgentRecommendation,
        profile: ProjectProfile,
        assessment: NeedsAssessment,
        enterprise_rules: dict | None = None
    ) -> GeneratedAgent:
        """Build a complete agent from recommendation."""

        # Generate system prompt
        system_prompt = self._generate_system_prompt(recommendation, profile, assessment)

        # Generate config
        config = self._generate_config(recommendation, profile)

        # Generate commands
        commands = self._generate_commands(recommendation, profile)

        # Generate knowledge base
        knowledge = self._generate_knowledge(profile)

        # Apply enterprise rules
        rules = self._apply_enterprise_rules(enterprise_rules)

        # Generate hooks (prepared for metrics)
        hooks = self._generate_hooks()

        return GeneratedAgent(
            name=f"{recommendation.name} - {profile.name or 'Project'}",
            type=recommendation.agent_type,
            system_prompt=system_prompt,
            config=config,
            commands=commands,
            knowledge=knowledge,
            rules=rules,
            hooks=hooks
        )

    def _generate_system_prompt(
        self,
        recommendation: AgentRecommendation,
        profile: ProjectProfile,
        assessment: NeedsAssessment
    ) -> str:
        """Generate the agent's system prompt."""

        # Base personality
        base_prompt = f"""# {recommendation.name}

## Rôle
Tu es un assistant IA spécialisé : **{recommendation.description}**.
Tu travailles sur le projet "{profile.name or 'ce projet'}" avec une équipe de développeurs.

## Contexte Projet
- **Stack technique**: {', '.join(profile.stack) or 'Non spécifié'}
- **Patterns**: {', '.join(profile.patterns) or 'Non spécifié'}
- **Complexité**: {profile.complexity}

## Contexte Équipe
- **Taille**: {assessment.team_size or 'Non spécifié'}
- **Niveau**: {assessment.experience_level or 'Non spécifié'}
- **Priorités**: {', '.join(assessment.priorities) or 'Non spécifié'}

## Tes Capacités
"""
        for cap in recommendation.capabilities:
            base_prompt += f"- **{cap.name}**: {cap.description}\n"

        base_prompt += """
## Règles de Conduite
1. Sois concis et actionnable dans tes réponses
2. Adapte ton niveau de détail à l'expérience de l'équipe
3. Propose toujours des solutions concrètes
4. Respecte les conventions du projet
5. Signale tout problème de sécurité potentiel
"""

        if assessment.sensitive_data:
            base_prompt += """
## ⚠️ DONNÉES SENSIBLES
Ce projet traite des données sensibles. Tu dois :
- Ne JAMAIS inclure de vraies données dans tes exemples
- Toujours utiliser des données fictives
- Alerter si tu détectes des données sensibles exposées
"""

        if assessment.compliance_requirements:
            base_prompt += f"""
## Compliance
Exigences: {', '.join(assessment.compliance_requirements)}
Assure-toi que tes suggestions respectent ces normes.
"""

        return base_prompt

    def _generate_config(self, recommendation: AgentRecommendation, profile: ProjectProfile) -> dict:
        """Generate agent configuration."""
        return {
            "agent_type": recommendation.agent_type,
            "name": recommendation.name,
            "version": "1.0.0",
            "llm": {
                "provider": "claude",
                "model": "claude-sonnet-4-20250514",
                "temperature": 0.3 if recommendation.agent_type == "security-checker" else 0.7,
                "max_tokens": 4096
            },
            "capabilities": [cap.name for cap in recommendation.capabilities],
            "project": {
                "stack": profile.stack,
                "complexity": profile.complexity
            }
        }

    def _generate_commands(self, recommendation: AgentRecommendation, profile: ProjectProfile) -> dict[str, str]:
        """Generate slash commands for the agent."""
        commands = {}

        if recommendation.agent_type == "debug-helper":
            commands["debug"] = """# /debug - Analyser un problème

Analyse le problème décrit et propose des pistes de résolution.

## Usage
/debug <description du problème>

## Ce que je fais
1. J'analyse les symptômes décrits
2. Je cherche les causes possibles dans le contexte du projet
3. Je propose des étapes de diagnostic
4. Je suggère des solutions

Décris ton problème et je t'aide à le résoudre.
"""
            commands["trace"] = """# /trace - Analyser une stack trace

Analyse une stack trace ou des logs d'erreur.

## Usage
/trace
Puis colle ta stack trace.

## Ce que je fais
1. J'identifie l'erreur principale
2. Je localise la source dans le code
3. J'explique la cause probable
4. Je propose un correctif
"""

        elif recommendation.agent_type == "code-reviewer":
            commands["review"] = """# /review - Review de code

Effectue une review du code fourni.

## Usage
/review
Puis colle le code à reviewer.

## Ce que je vérifie
- Style et conventions
- Bonnes pratiques
- Problèmes de sécurité potentiels
- Opportunités d'amélioration
"""

        elif recommendation.agent_type == "test-generator":
            commands["test"] = """# /test - Générer des tests

Génère des tests pour le code fourni.

## Usage
/test
Puis colle le code à tester.

## Ce que je génère
- Tests unitaires
- Cas limites
- Mocks nécessaires
"""

        elif recommendation.agent_type == "security-checker":
            commands["security"] = """# /security - Audit de sécurité

Effectue un audit de sécurité du code.

## Usage
/security
Puis colle le code à auditer.

## Ce que je vérifie
- Vulnérabilités OWASP Top 10
- Secrets exposés
- Injection possibles
- Problèmes d'authentification/autorisation
"""

        return commands

    def _generate_knowledge(self, profile: ProjectProfile) -> dict[str, str]:
        """Generate knowledge base files."""
        knowledge = {}

        # Architecture summary
        if profile.description or profile.patterns:
            knowledge["architecture.md"] = f"""# Architecture du Projet

## Description
{profile.description or 'Projet de développement'}

## Stack Technique
{chr(10).join(f'- {tech}' for tech in profile.stack) or '- Non spécifié'}

## Patterns Architecturaux
{chr(10).join(f'- {pattern}' for pattern in profile.patterns) or '- Non spécifié'}

## Complexité
{profile.complexity}
"""

        # Conventions (if detected)
        if profile.conventions:
            knowledge["conventions.md"] = f"""# Conventions du Projet

{json.dumps(profile.conventions, indent=2)}
"""

        return knowledge

    def _apply_enterprise_rules(self, enterprise_rules: dict | None) -> dict[str, Any]:
        """Apply enterprise rules to the agent."""
        rules = {}

        if enterprise_rules:
            rules["enterprise"] = enterprise_rules

        # Default BPCE rules (demo)
        rules["bpce-security"] = {
            "id": "BPCE-SEC-001",
            "name": "Protection des données",
            "enabled": True,
            "actions": {
                "pii_detected": "mask_or_reject",
                "financial_data": "reject",
                "credentials": "reject_and_alert"
            }
        }

        return rules

    def _generate_hooks(self) -> dict[str, str]:
        """Generate hook scripts for metrics collection."""
        return {
            "on-conversation-start": """#!/bin/bash
# Hook: on-conversation-start
# Called when a new conversation begins

# Log session start (placeholder for metrics)
echo "[$(date -Iseconds)] SESSION_START user=$USER agent=$AGENT_TYPE" >> /tmp/assistant-architect-metrics.log
""",
            "on-task-complete": """#!/bin/bash
# Hook: on-task-complete
# Called when a task is completed

# Log task completion (placeholder for metrics)
echo "[$(date -Iseconds)] TASK_COMPLETE task=$TASK_NAME duration=$DURATION" >> /tmp/assistant-architect-metrics.log
""",
            "on-code-generated": """#!/bin/bash
# Hook: on-code-generated
# Called when code is generated

# Log code generation (placeholder for metrics)
echo "[$(date -Iseconds)] CODE_GENERATED file=$FILE_PATH lines=$LINE_COUNT language=$LANGUAGE" >> /tmp/assistant-architect-metrics.log
"""
        }
