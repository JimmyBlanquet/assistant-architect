# Assistant Architect - Project Memory

**Purpose**: Système de génération d'agents IA pour projets de développement
**Client**: Direction Architecture - Groupe BPCE
**Status**: MVP V1 Fonctionnel | V2 En Développement

---

## Quick Context

Système intelligent qui :
1. Analyse la documentation de code (Markdown/HTML)
2. Dialogue avec l'utilisateur pour comprendre ses besoins
3. Recommande des agents IA adaptés (dynamiquement selon le projet)
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
│   ├── agent_builder.py     # Génération d'agents (V1)
│   └── catalog_v2.py        # Catalogue enrichi (V2 - à créer)
knowledge/
├── rules/
│   └── bpce-group-rules.yaml # Règles sécurité/compliance BPCE
demo/
├── run_demo.py              # Script V1
├── run_demo_v2.py           # Script V2 (à créer)
└── lib/                     # Modules V2 (à créer)
    ├── feedback.py
    ├── selector.py
    └── batch_generator.py
```

---

## Key Commands

```bash
# V1 - Démo basique
cd "/home/jimb/Projects/Assisstant Architect"
python demo/run_demo.py
python demo/run_demo.py --non-interactive
python demo/run_demo.py --provider gemini

# V2 - Démo enrichie (à venir)
python demo/run_demo_v2.py
python demo/run_demo_v2.py --non-interactive
python demo/run_demo_v2.py --max-agents 10
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
| Catalogue V2 | Hybride | Experts techniques + Assistants transversaux |

---

## V2 - Catalogue Hybride

### Experts Techniques (par domaine - dynamique)

| Expert | Spécialisations |
|--------|-----------------|
| Frontend Expert | React, Vue, Angular, TypeScript |
| Backend Expert | Spring, Django, Node.js, FastAPI |
| Data Expert | SQL, NoSQL, ETL, BigData |
| DevOps Expert | Docker, K8s, Terraform, CI/CD |
| Mobile Expert | iOS, Android, Flutter |
| Cloud Expert | AWS, GCP, Azure |

### Assistants Transversaux (par besoin)

| Assistant | Déclencheurs |
|-----------|--------------|
| Security Checker | Données sensibles, compliance |
| Onboarding Guide | Équipe mixte, projet complexe |
| Doc Generator | Documentation manquante |
| Refactoring Advisor | Dette technique |
| Performance Optimizer | Problèmes perf |
| Test Advisor | Coverage faible |

**Important** : Les recommandations sont **dynamiques**, basées sur l'analyse du repo entrant. Rien n'est hardcodé.

---

## BPCE Rules (3 règles démo)

1. **BPCE-SEC-001**: Protection données sensibles (PII, financières, credentials)
2. **BPCE-RGPD-001**: Conformité RGPD (minimisation, finalité, droits)
3. **BPCE-AUDIT-001**: Traçabilité pour audit réglementaire

---

## Current Sprint - V2 Implementation

- [x] Tester la démo V1 complète
- [x] Définir l'architecture V2 (catalogue hybride)
- [x] Documenter le plan V2
- [ ] Implémenter le catalogue V2 enrichi
- [ ] Créer le module feedback utilisateur
- [ ] Créer le module multi-sélection
- [ ] Créer le générateur batch
- [ ] Assembler run_demo_v2.py
- [ ] Tests et ajustements

---

## Documentation

- [ARCHITECTURE.md](../ARCHITECTURE.md) - Architecture technique complète (V1 + V2)
- [CADRAGE.md](../CADRAGE.md) - Document de cadrage initial
- [PLAN_V2.md](../PLAN_V2.md) - Plan d'implémentation V2

---

## GitHub

**Repository**: https://github.com/JimmyBlanquet/assistant-architect

---

*Last updated: 2025-11-26*
