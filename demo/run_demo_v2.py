#!/usr/bin/env python3
"""
Assistant Architect - Demo V2 "Man in the Loop"

Enhanced demonstration with:
- Dynamic catalog (Technical Experts + Transversal Assistants)
- User feedback on recommendations
- Multi-selection of agents
- Batch generation

Usage:
    python demo/run_demo_v2.py [--non-interactive] [--provider claude|gemini|ollama]
    python demo/run_demo_v2.py --max-agents 10
    python demo/run_demo_v2.py --export-feedback feedback.json
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.orchestrator import create_orchestrator
from core.llm_abstraction import get_provider
from dialogue.needs_assessor import NeedsAssessment
from generators.agent_builder import AgentBuilder
from generators.catalog_v2 import CatalogV2, get_catalog_v2

# Import V2 modules
from lib.feedback import FeedbackCollector, create_auto_feedback
from lib.selector import AgentSelector, auto_select
from lib.batch_generator import BatchGenerator, deploy_batch, print_deployment_instructions


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

## Tech Stack

- **Backend**: Python, FastAPI
- **Frontend**: React, TypeScript
- **Database**: PostgreSQL
- **Infrastructure**: Docker, GitHub Actions

## Development Workflow

1. **Project Principles** - `/speckit.constitution` establishes governance
2. **Specifications** - `/speckit.specify` defines requirements
3. **Clarification** - `/speckit.clarify` refines requirements
4. **Technical Planning** - `/speckit.plan` documents architecture
5. **Task Breakdown** - `/speckit.tasks` creates implementation sequences
6. **Analysis** - `/speckit.analyze` validates consistency
7. **Implementation** - `/speckit.implement` executes the build

## Known Pain Points

- Complex debugging when specs and implementation diverge
- Onboarding new developers to the spec-driven workflow
- Maintaining consistency across multiple spec files
- Performance optimization needed for large spec files
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
║                                  VERSION 2                                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)


def run_demo_v2(
    non_interactive: bool = False,
    provider: str = "claude",
    max_agents: int | None = None,
    export_feedback: str | None = None
):
    """Run the V2 demonstration."""

    print_banner()
    print(f"\n🚀 Démarrage de la démonstration V2 (provider: {provider})")
    print("=" * 70)

    # Initialize components
    rules_path = Path(__file__).parent.parent / "knowledge" / "rules" / "bpce-group-rules.yaml"
    output_dir = Path(__file__).parent.parent / "generated-agents"

    # Initialize orchestrator for analysis and dialogue
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

    # Initialize V2 catalog
    catalog = get_catalog_v2()

    # Get expert icons for display
    expert_icons = {k: v.icon for k, v in catalog.get_all_agents().items()}
    technical_types = list(catalog.get_all_experts().keys())

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
    print(f"   🛠️  Stack: {', '.join(profile.stack[:5]) or 'Python, React, PostgreSQL'}")
    print(f"   📐 Patterns: {', '.join(profile.patterns[:3]) or 'specification-driven'}")
    print(f"   📈 Complexité: {profile.complexity}")

    if not non_interactive:
        input("\n   [Appuyez sur Entrée pour continuer...]")

    # =========================================================================
    # Phase 2: Dialogue
    # =========================================================================
    print("\n" + "=" * 70)
    print("💬 PHASE 2: ÉVALUATION DES BESOINS")
    print("=" * 70)

    if non_interactive:
        assessment = NeedsAssessment(
            team_size="4-8 (moyenne)",
            experience_level="Mixte",
            main_pain_points=["Debugging/résolution d'incidents", "Performance", "Tests"],
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
            assessment = _run_manual_dialogue()

    if not non_interactive:
        input("\n   [Appuyez sur Entrée pour continuer...]")

    # =========================================================================
    # Phase 3: Recommendations (V2 - Dynamic)
    # =========================================================================
    print("\n" + "=" * 70)
    print("🎯 PHASE 3: RECOMMANDATIONS D'AGENTS (Catalogue V2)")
    print("=" * 70)

    # Use V2 catalog for dynamic recommendations
    recommendations = catalog.get_recommendations(profile, assessment, min_score=0.2)

    # Limit if max_agents specified
    if max_agents and len(recommendations) > max_agents:
        recommendations = recommendations[:max_agents]

    print(catalog.format_recommendations(recommendations, show_capabilities=True))

    if not non_interactive:
        input("\n   [Appuyez sur Entrée pour continuer...]")

    # =========================================================================
    # Phase 4: Feedback (V2 - New)
    # =========================================================================
    print("\n" + "=" * 70)
    print("💭 PHASE 4: FEEDBACK UTILISATEUR")
    print("=" * 70)

    if non_interactive:
        print("\n   [Mode non-interactif - Feedback automatique basé sur les scores]")
        feedback_session = create_auto_feedback(recommendations)
        useful_agents = [f.agent_type for f in feedback_session.feedbacks if f.rating == "useful"]
    else:
        feedback_collector = FeedbackCollector()
        feedback_session = feedback_collector.collect_all_feedback(recommendations, expert_icons)
        feedback_collector.print_summary()

        # Export feedback if requested
        if export_feedback:
            feedback_session.export_json(Path(export_feedback))
            print(f"\n   📁 Feedback exporté vers: {export_feedback}")

        useful_agents = feedback_collector.get_useful_agents()

        # Ask for refinement
        if feedback_collector.ask_refinement():
            recommendations = feedback_collector.filter_recommendations(
                recommendations, exclude_not_relevant=True
            )
            print("\n   ✅ Recommandations raffinées selon vos retours")

    if not non_interactive:
        input("\n   [Appuyez sur Entrée pour continuer...]")

    # =========================================================================
    # Phase 5: Selection (V2 - Multi-select)
    # =========================================================================
    print("\n" + "=" * 70)
    print("✅ PHASE 5: SÉLECTION DES AGENTS")
    print("=" * 70)

    if non_interactive:
        print("\n   [Mode non-interactif - Sélection automatique des agents HIGH priority]")
        selection = auto_select(recommendations, max_agents=5, min_priority="high")
        print(f"   ✅ {selection.count} agent(s) sélectionné(s)")
    else:
        selector = AgentSelector()
        selection = selector.run_selection(
            recommendations,
            expert_icons=expert_icons,
            technical_types=technical_types,
            useful_agents=useful_agents
        )

    if selection.is_empty():
        print("\n   ⚠️  Aucun agent sélectionné. Fin de la démonstration.")
        return

    if not non_interactive:
        input("\n   [Appuyez sur Entrée pour continuer...]")

    # =========================================================================
    # Phase 6: Generation (V2 - Batch)
    # =========================================================================
    print("\n" + "=" * 70)
    print("⚙️  PHASE 6: GÉNÉRATION DES AGENTS (Batch)")
    print("=" * 70)

    # Initialize builder
    try:
        llm = get_provider(provider)
    except Exception:
        llm = None

    builder = AgentBuilder(llm)

    # Load enterprise rules
    enterprise_rules = None
    if rules_path.exists():
        import yaml
        with open(rules_path) as f:
            enterprise_rules = yaml.safe_load(f)

    # Batch generation
    batch_gen = BatchGenerator(builder)
    gen_result = batch_gen.generate_batch(
        selection.selected_recommendations,
        profile,
        assessment,
        enterprise_rules,
        expert_icons
    )

    batch_gen.print_summary(gen_result)

    if gen_result.error_count == gen_result.total_count:
        print("\n   ❌ Tous les agents ont échoué. Fin de la démonstration.")
        return

    if not non_interactive:
        input("\n   [Appuyez sur Entrée pour continuer...]")

    # =========================================================================
    # Phase 7: Validation
    # =========================================================================
    print("\n" + "=" * 70)
    print("✅ PHASE 7: VALIDATION ARCHITECTE")
    print("=" * 70)

    successful_agents = gen_result.get_successful_agents()

    print(f"\n   {len(successful_agents)} agent(s) générés avec succès:")
    for agent in successful_agents:
        print(f"   • {agent.name}")

    if non_interactive:
        approved = True
        print("\n   [Mode non-interactif - Approbation automatique]")
    else:
        response = input("\n   Approuver tous les agents? (O/n): ").strip().lower()
        approved = response != 'n'

    if approved:
        print("\n   ✅ Agents APPROUVÉS par l'architecte")
    else:
        print("\n   ❌ Agents REJETÉS - Fin de la démonstration")
        return

    if not non_interactive:
        input("\n   [Appuyez sur Entrée pour continuer...]")

    # =========================================================================
    # Phase 8: Deployment
    # =========================================================================
    print("\n" + "=" * 70)
    print("🚀 PHASE 8: DÉPLOIEMENT")
    print("=" * 70)

    deploy_result = deploy_batch(successful_agents, output_dir)
    print_deployment_instructions(deploy_result)

    # =========================================================================
    # End
    # =========================================================================
    print("\n" + "=" * 70)
    print("✨ DÉMONSTRATION V2 TERMINÉE")
    print("=" * 70)
    print(f"""
   Ce que nous avons démontré dans la V2:

   1. ✅ Analyse automatique de documentation
   2. ✅ Dialogue intelligent pour comprendre les besoins
   3. ✅ Recommandations DYNAMIQUES (Experts + Assistants)
   4. ✅ Feedback utilisateur sur les propositions (Man in the Loop)
   5. ✅ Multi-sélection d'agents
   6. ✅ Génération BATCH de {gen_result.success_count} agents
   7. ✅ Application des règles BPCE
   8. ✅ Workflow de validation architecte
   9. ✅ Déploiement batch

   Agents générés: {', '.join(a.name for a in successful_agents)}
""")


def _create_mock_profile():
    """Create a mock profile for demo without LLM."""
    from analyzers.doc_analyzer import ProjectProfile
    return ProjectProfile(
        name="Spec-Kit",
        description="Toolkit for spec-driven development",
        stack=["Python", "FastAPI", "React", "TypeScript", "PostgreSQL", "Docker"],
        patterns=["specification-driven", "CLI", "API"],
        complexity="medium",
        pain_points=["debugging when specs diverge", "onboarding new developers", "performance"],
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

    print("\n   📋 Question 3/5: Principales difficultés? (plusieurs choix: 1,2,3)")
    print("      1. Debugging")
    print("      2. Code reviews")
    print("      3. Tests")
    print("      4. Performance")
    print("      5. Documentation")
    diff = input("      Choix: ").strip() or "1,3"
    diff_map = {
        "1": "Debugging",
        "2": "Code reviews",
        "3": "Tests",
        "4": "Performance",
        "5": "Documentation"
    }
    difficulties = [diff_map.get(d.strip(), "Debugging") for d in diff.split(",")]

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
        main_pain_points=difficulties,
        priorities=["Qualité du code"],
        sensitive_data=sensitive,
        compliance_requirements=["RGPD"] if sensitive else [],
        preferred_workflow=workflow
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assistant Architect Demo V2")
    parser.add_argument("--non-interactive", action="store_true", help="Run without user input")
    parser.add_argument("--provider", default="claude", choices=["claude", "gemini", "ollama"])
    parser.add_argument("--max-agents", type=int, help="Maximum number of agents to recommend")
    parser.add_argument("--export-feedback", type=str, help="Export feedback to JSON file")

    args = parser.parse_args()

    run_demo_v2(
        non_interactive=args.non_interactive,
        provider=args.provider,
        max_agents=args.max_agents,
        export_feedback=args.export_feedback
    )
