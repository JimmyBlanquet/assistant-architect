#!/usr/bin/env python3
"""
Assistant Architect - Demo Script

Demonstrates the full workflow:
1. Analyze project documentation (using spec-kit as example)
2. Conduct needs assessment dialogue
3. Recommend appropriate agents
4. Generate selected agent
5. Validate and deploy

Usage:
    python demo/run_demo.py [--non-interactive] [--provider claude|gemini|ollama]
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.orchestrator import create_orchestrator
from dialogue.needs_assessor import NeedsAssessment


# Sample documentation content (from spec-kit project)
SAMPLE_DOC = """
# Spec Kit

Spec Kit is an open-source toolkit designed to accelerate software development
by prioritizing specifications as executable artifacts.

## Overview

The framework implements "Spec-Driven Development," which flips conventional practice:
specifications become executable, directly generating working implementations
rather than just guiding them.

## Supported AI Agents

- Claude Code (Anthropic)
- GitHub Copilot
- Gemini CLI
- Cursor, Windsurf, Qwen Code

## Requirements

- Python 3.11+
- Git version control
- UV package manager

## Development Workflow

1. **Project Principles** - `/speckit.constitution` establishes governance
2. **Specifications** - `/speckit.specify` defines requirements
3. **Clarification** - `/speckit.clarify` refines requirements
4. **Technical Planning** - `/speckit.plan` documents architecture
5. **Task Breakdown** - `/speckit.tasks` creates implementation sequences
6. **Analysis** - `/speckit.analyze` validates consistency
7. **Implementation** - `/speckit.implement` executes the build

## Project Structure

```
.specify/
├── memory/constitution.md
├── scripts/
├── specs/
└── templates/
```

## Architecture

The system follows a specification-driven architecture where:
- Specs define the "what"
- Plans define the "how"
- Tasks break down the work
- Implementation is guided by all above

## Complexity

This is a medium-high complexity project with:
- Multiple AI agent integrations
- CLI tooling
- Template system
- Workflow orchestration

## Known Pain Points

- Complex debugging when specs and implementation diverge
- Onboarding new developers to the spec-driven workflow
- Maintaining consistency across multiple spec files
"""


def print_banner():
    """Print the demo banner."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     █████╗ ███████╗███████╗██╗███████╗████████╗ █████╗ ███╗   ██╗████████╗   ║
║    ██╔══██╗██╔════╝██╔════╝██║██╔════╝╚══██╔══╝██╔══██╗████╗  ██║╚══██╔══╝   ║
║    ███████║███████╗███████╗██║███████╗   ██║   ███████║██╔██╗ ██║   ██║      ║
║    ██╔══██║╚════██║╚════██║██║╚════██║   ██║   ██╔══██║██║╚██╗██║   ██║      ║
║    ██║  ██║███████║███████║██║███████║   ██║   ██║  ██║██║ ╚████║   ██║      ║
║    ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝      ║
║                                                                              ║
║                    █████╗ ██████╗  ██████╗██╗  ██╗██╗████████╗███████╗       ║
║                   ██╔══██╗██╔══██╗██╔════╝██║  ██║██║╚══██╔══╝██╔════╝       ║
║                   ███████║██████╔╝██║     ███████║██║   ██║   █████╗         ║
║                   ██╔══██║██╔══██╗██║     ██╔══██║██║   ██║   ██╔══╝         ║
║                   ██║  ██║██║  ██║╚██████╗██║  ██║██║   ██║   ███████╗       ║
║                   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝   ╚═╝   ╚══════╝       ║
║                                                                              ║
║                     Générateur d'Agents IA pour Développeurs                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)


def run_demo(non_interactive: bool = False, provider: str = "claude"):
    """Run the full demonstration."""

    print_banner()
    print(f"\n🚀 Démarrage de la démonstration (provider: {provider})")
    print("=" * 70)

    # Initialize orchestrator
    rules_path = Path(__file__).parent.parent / "knowledge" / "rules" / "bpce-group-rules.yaml"
    output_dir = Path(__file__).parent.parent / "generated-agents"

    try:
        orchestrator = create_orchestrator(
            provider=provider,
            enterprise_rules_path=rules_path,
            output_dir=output_dir
        )
    except Exception as e:
        print(f"\n⚠️  Impossible d'initialiser le provider '{provider}': {e}")
        print("   Continuation en mode simulation...\n")
        orchestrator = None

    # =========================================================================
    # Phase 1: Analysis
    # =========================================================================
    print("\n" + "=" * 70)
    print("📊 PHASE 1: ANALYSE DE LA DOCUMENTATION")
    print("=" * 70)
    print("\n📁 Source: Projet Spec-Kit (GitHub)")
    print("   Documentation Markdown analysée...\n")

    if orchestrator:
        try:
            profile = orchestrator.analyze_documentation(SAMPLE_DOC)
        except Exception as e:
            print(f"   ⚠️  Analyse LLM échouée, utilisation de l'analyse basique: {e}")
            profile = _create_mock_profile()
    else:
        profile = _create_mock_profile()

    print("✅ Analyse terminée!\n")
    print(f"   📋 Projet: {profile.name or 'Spec-Kit'}")
    print(f"   🛠️  Stack: {', '.join(profile.stack[:5]) or 'Python, Git, CLI'}")
    print(f"   📐 Patterns: {', '.join(profile.patterns[:3]) or 'specification-driven'}")
    print(f"   📈 Complexité: {profile.complexity}")

    if profile.pain_points:
        print(f"   ⚠️  Points de friction détectés: {len(profile.pain_points)}")

    input("\n   [Appuyez sur Entrée pour continuer...]") if not non_interactive else None

    # =========================================================================
    # Phase 2: Dialogue
    # =========================================================================
    print("\n" + "=" * 70)
    print("💬 PHASE 2: ÉVALUATION DES BESOINS")
    print("=" * 70)

    if non_interactive:
        # Use predefined answers
        assessment = NeedsAssessment(
            team_size="4-8 (moyenne)",
            experience_level="Mixte",
            main_pain_points=["Debugging/résolution d'incidents", "Compréhension du code existant"],
            priorities=["Qualité du code"],
            sensitive_data=True,
            compliance_requirements=["RGPD", "Normes internes"],
            preferred_workflow="Les deux"
        )
        print("\n   [Mode non-interactif - Réponses prédéfinies utilisées]")
        print(f"\n   📊 Équipe: {assessment.team_size}")
        print(f"   👥 Niveau: {assessment.experience_level}")
        print(f"   🎯 Priorité: {', '.join(assessment.priorities)}")
        print(f"   🔒 Données sensibles: {'Oui' if assessment.sensitive_data else 'Non'}")
    else:
        print("\n   Je vais vous poser quelques questions pour comprendre vos besoins.\n")

        if orchestrator:
            assessment = orchestrator.conduct_dialogue()
        else:
            # Manual dialogue simulation
            assessment = _run_manual_dialogue()

    if orchestrator:
        orchestrator.set_assessment(assessment)

    input("\n   [Appuyez sur Entrée pour continuer...]") if not non_interactive else None

    # =========================================================================
    # Phase 3: Recommendations
    # =========================================================================
    print("\n" + "=" * 70)
    print("🎯 PHASE 3: RECOMMANDATIONS D'AGENTS")
    print("=" * 70)

    if orchestrator:
        recommendations = orchestrator.get_recommendations(max_recommendations=3)
        print(orchestrator.format_recommendations())
    else:
        recommendations = _create_mock_recommendations()
        _print_mock_recommendations(recommendations)

    # Select first recommendation
    print("\n   Sélection automatique du premier agent recommandé...")

    if orchestrator:
        selected = orchestrator.select_agent(0)
    else:
        selected = recommendations[0]

    print(f"   ✅ Agent sélectionné: {selected['name'] if isinstance(selected, dict) else selected.name}")

    input("\n   [Appuyez sur Entrée pour continuer...]") if not non_interactive else None

    # =========================================================================
    # Phase 4: Generation
    # =========================================================================
    print("\n" + "=" * 70)
    print("⚙️  PHASE 4: GÉNÉRATION DE L'AGENT")
    print("=" * 70)

    print("\n   Génération en cours...")
    print("   - Création du system prompt...")
    print("   - Configuration des capacités...")
    print("   - Génération des commandes...")
    print("   - Application des règles BPCE...")
    print("   - Préparation des hooks métriques...")

    if orchestrator:
        try:
            agent = orchestrator.generate_agent()
            print("\n   ✅ Agent généré avec succès!")
        except Exception as e:
            print(f"\n   ⚠️  Erreur de génération: {e}")
            agent = None
    else:
        agent = None
        print("\n   ✅ Agent généré avec succès! (simulation)")

    input("\n   [Appuyez sur Entrée pour continuer...]") if not non_interactive else None

    # =========================================================================
    # Phase 5: Validation
    # =========================================================================
    print("\n" + "=" * 70)
    print("✅ PHASE 5: VALIDATION ARCHITECTE")
    print("=" * 70)

    if orchestrator and agent:
        print(orchestrator.get_validation_summary())
    else:
        _print_mock_validation_summary()

    if non_interactive:
        approved = True
        print("\n   [Mode non-interactif - Approbation automatique]")
    else:
        response = input("\n   Approuver cet agent? (O/n): ").strip().lower()
        approved = response != 'n'

    if approved:
        print("\n   ✅ Agent APPROUVÉ par l'architecte")
        if orchestrator:
            orchestrator.validate(True, "demo_architect")
    else:
        print("\n   ❌ Agent REJETÉ - Fin de la démonstration")
        return

    input("\n   [Appuyez sur Entrée pour continuer...]") if not non_interactive else None

    # =========================================================================
    # Phase 6: Deployment
    # =========================================================================
    print("\n" + "=" * 70)
    print("🚀 PHASE 6: DÉPLOIEMENT")
    print("=" * 70)

    if orchestrator and agent:
        try:
            deploy_path = orchestrator.deploy()
            print(orchestrator.get_deployment_instructions())
        except Exception as e:
            print(f"\n   ⚠️  Erreur de déploiement: {e}")
            _print_mock_deployment()
    else:
        _print_mock_deployment()

    # =========================================================================
    # End
    # =========================================================================
    print("\n" + "=" * 70)
    print("✨ DÉMONSTRATION TERMINÉE")
    print("=" * 70)
    print("""
   Ce que nous avons démontré:

   1. ✅ Analyse automatique de documentation (Markdown/HTML)
   2. ✅ Dialogue intelligent pour comprendre les besoins
   3. ✅ Recommandation d'agents basée sur le contexte
   4. ✅ Génération d'agent avec skills, commands, hooks
   5. ✅ Application des règles BPCE (sécurité, RGPD, audit)
   6. ✅ Workflow de validation architecte
   7. ✅ Déploiement vers environnement cible

   Prochaines étapes:
   - Intégration avec d'autres repos
   - Enrichissement du catalogue d'agents
   - Implémentation complète des métriques
   - UI web pour le workflow de validation
""")


def _create_mock_profile():
    """Create a mock profile for demo without LLM."""
    from analyzers.doc_analyzer import ProjectProfile
    return ProjectProfile(
        name="Spec-Kit",
        description="Toolkit for spec-driven development",
        stack=["Python", "Git", "CLI", "Claude", "GitHub Copilot"],
        patterns=["specification-driven", "CLI"],
        complexity="medium",
        pain_points=["debugging when specs diverge", "onboarding new developers"],
        features=["spec validation", "multi-agent support", "template system"]
    )


def _run_manual_dialogue():
    """Run manual dialogue without LLM."""
    print("\n   📋 Question 1/5: Taille de l'équipe?")
    print("      1. 1-3 (petite)")
    print("      2. 4-8 (moyenne)")
    print("      3. 9-20 (grande)")
    team = input("      Choix: ").strip() or "2"
    team_map = {"1": "1-3 (petite)", "2": "4-8 (moyenne)", "3": "9-20 (grande)"}
    team_size = team_map.get(team, "4-8 (moyenne)")

    print("\n   📋 Question 2/5: Niveau d'expérience?")
    print("      1. Junior")
    print("      2. Intermédiaire")
    print("      3. Senior")
    print("      4. Mixte")
    exp = input("      Choix: ").strip() or "4"
    exp_map = {"1": "Junior", "2": "Intermédiaire", "3": "Senior", "4": "Mixte"}
    experience = exp_map.get(exp, "Mixte")

    print("\n   📋 Question 3/5: Principale difficulté?")
    print("      1. Debugging")
    print("      2. Code reviews")
    print("      3. Tests")
    print("      4. Compréhension du code")
    diff = input("      Choix: ").strip() or "1"
    diff_map = {"1": "Debugging", "2": "Code reviews", "3": "Tests", "4": "Compréhension du code"}
    difficulty = diff_map.get(diff, "Debugging")

    print("\n   📋 Question 4/5: Données sensibles?")
    sensitive = input("      (O/n): ").strip().lower() != "n"

    print("\n   📋 Question 5/5: Interface préférée?")
    print("      1. CLI")
    print("      2. VS Code")
    print("      3. Les deux")
    wf = input("      Choix: ").strip() or "3"
    wf_map = {"1": "CLI", "2": "VS Code", "3": "Les deux"}
    workflow = wf_map.get(wf, "Les deux")

    return NeedsAssessment(
        team_size=team_size,
        experience_level=experience,
        main_pain_points=[difficulty],
        priorities=["Qualité du code"],
        sensitive_data=sensitive,
        compliance_requirements=["RGPD"] if sensitive else [],
        preferred_workflow=workflow
    )


def _create_mock_recommendations():
    """Create mock recommendations."""
    return [
        {
            "name": "Debug Helper",
            "priority": "high",
            "description": "Aide au debugging et résolution d'incidents",
            "justification": "Complexité moyenne du projet + debugging identifié"
        },
        {
            "name": "Onboarding Guide",
            "priority": "medium",
            "description": "Aide à la montée en compétence",
            "justification": "Équipe mixte + projet spec-driven"
        },
        {
            "name": "Security Checker",
            "priority": "medium",
            "description": "Vérification sécurité du code",
            "justification": "Données sensibles à protéger"
        }
    ]


def _print_mock_recommendations(recs):
    """Print mock recommendations."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║              AGENTS IA RECOMMANDÉS                           ║
╚══════════════════════════════════════════════════════════════╝
""")
    for i, rec in enumerate(recs, 1):
        icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}[rec["priority"]]
        print(f"""
{i}. {rec['name']} {icon} [{rec['priority'].upper()}]
   {rec['description']}

   📋 Justification: {rec['justification']}
""")


def _print_mock_validation_summary():
    """Print mock validation summary."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║           VALIDATION - AGENT GÉNÉRÉ                          ║
╚══════════════════════════════════════════════════════════════╝

📋 INFORMATIONS GÉNÉRALES
   • Nom: Debug Helper - Spec-Kit
   • Type: debug-helper
   • Version: 1.0.0

🤖 CONFIGURATION LLM
   • Provider: claude
   • Model: claude-sonnet-4-20250514
   • Temperature: 0.7

📝 COMMANDES DISPONIBLES
   • /debug
   • /trace

📚 BASE DE CONNAISSANCES
   • architecture.md
   • conventions.md

🔒 RÈGLES APPLIQUÉES
   • bpce-security
   • enterprise

🔗 HOOKS MÉTRIQUES
   • on-conversation-start
   • on-task-complete
   • on-code-generated
""")


def _print_mock_deployment():
    """Print mock deployment instructions."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║           INSTRUCTIONS DE DÉPLOIEMENT                        ║
╚══════════════════════════════════════════════════════════════╝

✅ Agent généré avec succès!

📁 Emplacement: ./generated-agents/agent-debug-helper-spec-kit/

🚀 UTILISATION AVEC CLAUDE CODE:

   1. Copiez le dossier dans votre projet:
      cp -r "./generated-agents/agent-debug-helper-spec-kit" /votre/projet/.claude/

🖥️  UTILISATION AVEC VS CODE:

   1. Ouvrez les paramètres VS Code
   2. Pointez vers: ./generated-agents/agent-debug-helper-spec-kit/config.json

📋 COMMANDES DISPONIBLES:
   /debug
   /trace
""")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assistant Architect Demo")
    parser.add_argument("--non-interactive", action="store_true", help="Run without user input")
    parser.add_argument("--provider", default="claude", choices=["claude", "gemini", "ollama"])
    args = parser.parse_args()

    run_demo(non_interactive=args.non_interactive, provider=args.provider)
