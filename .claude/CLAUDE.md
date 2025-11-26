# Assistant Architect - Project Memory

**Purpose**: Système de génération d'agents IA pour projets de développement
**Client**: Direction Architecture - Groupe BPCE
**Status**: MVP Démo Fonctionnel

---

## Quick Context

Système intelligent qui :
1. Analyse la documentation de code (Markdown/HTML)
2. Dialogue avec l'utilisateur pour comprendre ses besoins
3. Recommande des agents IA adaptés
4. Génère et déploie ces agents (skills, commands, hooks)

**Philosophie**: LLM-agnostique (Claude, Gemini, modèles ouverts)

---

## Project Structure

```
src/
├── core/
│   ├── orchestrator.py      # Coordinateur central
│   └── llm_abstraction.py   # Abstraction LLM (Claude, Gemini, Ollama)
├── analyzers/
│   └── doc_analyzer.py      # Analyse Markdown/HTML
├── dialogue/
│   └── needs_assessor.py    # Questionnaire besoins
├── generators/
│   └── agent_builder.py     # Génération d'agents
knowledge/
├── rules/
│   └── bpce-group-rules.yaml # Règles sécurité/compliance BPCE
demo/
└── run_demo.py              # Script de démonstration
```

---

## Key Commands

```bash
# Lancer la démo interactive
cd "/home/jimb/Projects/Assisstant Architect"
python demo/run_demo.py

# Démo non-interactive
python demo/run_demo.py --non-interactive

# Avec un autre provider
python demo/run_demo.py --provider gemini
```

---

## Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| LLM | Agnostique | Claude, Gemini, Ollama supportés |
| Validation | Workflow architecte | Approbation avant déploiement |
| Règles | Hybride | BPCE groupe + règles projet |
| Cible | Poste développeur | CLI + VS Code |
| Demo data | Spec-Kit (GitHub) | Projet open source pertinent |

---

## Demo: Spec-Kit Project

Le démonstrateur utilise le projet [spec-kit](https://github.com/github/spec-kit) de GitHub :
- Toolkit pour développement piloté par spécifications
- Documentation Markdown riche
- Stack: Python, CLI, intégrations AI

---

## BPCE Rules (3 règles démo)

1. **BPCE-SEC-001**: Protection données sensibles (PII, financières, credentials)
2. **BPCE-RGPD-001**: Conformité RGPD (minimisation, finalité, droits)
3. **BPCE-AUDIT-001**: Traçabilité pour audit réglementaire

---

## Next Steps

- [ ] Tester la démo complète
- [ ] Enrichir le catalogue d'agents
- [ ] Implémenter les métriques (hooks actifs)
- [ ] Ajouter des templates d'agents

---

*Last updated: 2025-11-25*
