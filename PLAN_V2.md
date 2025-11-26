# Plan d'Implémentation - Demo V2 "Man in the Loop"

**Date** : 2025-11-26
**Statut** : Planifié
**Objectif** : Enrichir la démo avec feedback utilisateur, multi-sélection et catalogue dynamique

---

## 1. Résumé des Changements

### V1 (Actuelle)
- 5 types d'agents fixes
- Maximum 3 recommandations
- Sélection d'un seul agent
- Génération unique
- Pas de feedback utilisateur

### V2 (Cible)
- 12 types d'agents (6 experts + 6 transversaux)
- Toutes les recommandations pertinentes affichées
- Multi-sélection d'agents
- Génération batch
- Feedback utilisateur sur chaque recommandation
- Contenu des agents dynamique selon le projet

---

## 2. Architecture V2

### 2.1 Nouveau Workflow (8 phases)

```
Phase 1: ANALYSE          → Détection stack et contexte projet
Phase 2: DIALOGUE         → Évaluation des besoins utilisateur
Phase 3: RECOMMANDATION   → Génération dynamique des recommandations
Phase 4: FEEDBACK         → [NOUVEAU] Retours utilisateur sur propositions
Phase 5: SÉLECTION        → [AMÉLIORÉ] Multi-sélection d'agents
Phase 6: GÉNÉRATION       → [AMÉLIORÉ] Batch de plusieurs agents
Phase 7: VALIDATION       → Approbation architecte (par agent)
Phase 8: DÉPLOIEMENT      → Batch vers environnement cible
```

### 2.2 Catalogue Hybride

#### Experts Techniques (détection automatique)

| ID | Nom | Technos Associées | Fichiers Déclencheurs |
|----|-----|-------------------|----------------------|
| `frontend-expert` | Frontend Expert | React, Vue, Angular, Svelte, TypeScript | `*.tsx`, `*.vue`, `angular.json` |
| `backend-expert` | Backend Expert | Spring, Django, FastAPI, Node.js, Go | `pom.xml`, `requirements.txt`, `go.mod` |
| `data-expert` | Data Expert | PostgreSQL, MongoDB, Redis, Elasticsearch | `*.sql`, `docker-compose.yml` (db) |
| `devops-expert` | DevOps Expert | Docker, K8s, Terraform, Ansible | `Dockerfile`, `*.yaml` (k8s), `*.tf` |
| `mobile-expert` | Mobile Expert | iOS, Android, Flutter, React Native | `*.swift`, `*.kt`, `pubspec.yaml` |
| `cloud-expert` | Cloud Expert | AWS, GCP, Azure, Serverless | `serverless.yml`, `cloudformation.yaml` |

#### Assistants Transversaux (besoins utilisateur)

| ID | Nom | Déclencheurs Dialogue | Déclencheurs Analyse |
|----|-----|----------------------|---------------------|
| `security-checker` | Security Checker | sensitive_data=true, compliance | Fichiers auth, .env |
| `onboarding-guide` | Onboarding Guide | team=mixed/junior, complexity=high | README pauvre |
| `doc-generator` | Doc Generator | documentation=needed | Peu de commentaires |
| `refactoring-advisor` | Refactoring Advisor | pain_point=dette_technique | Code complexe |
| `perf-optimizer` | Performance Optimizer | pain_point=performance | Pas de cache |
| `test-advisor` | Test Advisor | pain_point=tests, coverage=low | Peu de tests |

---

## 3. Plan d'Implémentation

### Étape 1 : Catalogue V2 Enrichi

**Fichier** : `src/generators/catalog_v2.py`

**Contenu** :
```python
# Structure du catalogue V2
EXPERT_TYPES = {
    "frontend-expert": {
        "name": "Frontend Expert",
        "category": "technical",
        "detection": {
            "files": ["*.tsx", "*.jsx", "*.vue", "angular.json", "next.config.*"],
            "packages": ["react", "vue", "angular", "@angular/core"],
        },
        "specializations": {
            "react": {...},
            "vue": {...},
            "angular": {...},
        },
        "capabilities": [...]
    },
    # ... autres experts
}

TRANSVERSAL_TYPES = {
    "security-checker": {
        "name": "Security Checker",
        "category": "transversal",
        "triggers": {
            "assessment": ["sensitive_data", "compliance"],
            "analysis": ["auth patterns", ".env files"],
        },
        "capabilities": [...]
    },
    # ... autres assistants
}
```

**Effort** : 2-3 heures

---

### Étape 2 : Module Feedback

**Fichier** : `demo/lib/feedback.py`

**Fonctionnalités** :
- Afficher chaque recommandation avec détails
- Collecter l'avis utilisateur (Très utile / Peut-être / Pas pertinent)
- Collecter commentaires optionnels
- Option de raffinement des recommandations
- Export des feedbacks en JSON (optionnel)

**Interface** :
```
╔══════════════════════════════════════════════════════════════╗
║  1. Frontend Expert (React/TypeScript) 🔴 HIGH               ║
║     Spécialisation: Hooks, State Management, Testing RTL     ║
║                                                              ║
║     Votre avis: [1] Très utile [2] Peut-être [3] Pas besoin  ║
║     Commentaire (Entrée pour passer): ___________________    ║
╚══════════════════════════════════════════════════════════════╝
```

**Effort** : 2 heures

---

### Étape 3 : Module Multi-Sélection

**Fichier** : `demo/lib/selector.py`

**Fonctionnalités** :
- Afficher liste numérotée des agents recommandés
- Grouper par catégorie (Experts / Transversaux)
- Sélection par numéros séparés par virgules
- Options rapides : [A] Tous, [H] High priority only
- Validation de la sélection

**Interface** :
```
╔══════════════════════════════════════════════════════════════╗
║  📦 EXPERTS TECHNIQUES                                       ║
║  [1] Frontend Expert (React)              🔴 HIGH            ║
║  [2] Backend Expert (Node.js)             🔴 HIGH            ║
║  [3] Data Expert (MongoDB)                🟡 MEDIUM          ║
║                                                              ║
║  🔧 ASSISTANTS TRANSVERSAUX                                  ║
║  [4] Security Checker                     🔴 HIGH            ║
║  [5] Onboarding Guide                     🟡 MEDIUM          ║
║                                                              ║
║  Sélection (ex: 1,2,4 ou A pour tous): _______              ║
╚══════════════════════════════════════════════════════════════╝
```

**Effort** : 1.5 heures

---

### Étape 4 : Générateur Batch

**Fichier** : `demo/lib/batch_generator.py`

**Fonctionnalités** :
- Générer plusieurs agents séquentiellement
- Afficher progression avec barre de statut
- Gérer les erreurs individuellement (continuer si un échoue)
- Résumé final avec statuts

**Interface** :
```
╔══════════════════════════════════════════════════════════════╗
║  GÉNÉRATION EN COURS (2/4)                                   ║
║  [████████████████░░░░░░░░░░░░░░░░░░░░░░] 50%               ║
║                                                              ║
║  ✅ Frontend Expert (React) ............. OK                ║
║  ⏳ Backend Expert (Node.js) ............ En cours          ║
║  ⏸️ Security Checker .................... En attente        ║
║  ⏸️ Onboarding Guide .................... En attente        ║
╚══════════════════════════════════════════════════════════════╝
```

**Effort** : 2 heures

---

### Étape 5 : Assemblage Demo V2

**Fichier** : `demo/run_demo_v2.py`

**Modifications** :
- Importer les nouveaux modules
- Intégrer les 8 phases du workflow
- Ajouter arguments CLI (`--max-agents`, `--export-feedback`)
- Mode non-interactif avec présets étendus
- Conservation de la compatibilité avec l'orchestrator existant

**Arguments CLI** :
```bash
python demo/run_demo_v2.py
    --non-interactive          # Mode automatique
    --provider [claude|gemini|ollama]
    --max-agents N             # Limiter les recommandations
    --export-feedback FILE     # Exporter feedbacks en JSON
    --preset FILE              # Charger réponses prédéfinies
```

**Effort** : 3 heures

---

### Étape 6 : Tests et Ajustements

**Actions** :
- Test manuel du workflow complet
- Test mode non-interactif
- Test avec différents providers
- Ajustements UX si nécessaire
- Documentation des commandes

**Effort** : 1.5 heures

---

## 4. Structure Finale des Fichiers

```
assistant-architect/
├── src/
│   ├── core/
│   │   ├── orchestrator.py          # Existant (modifications mineures)
│   │   └── llm_abstraction.py       # Existant
│   ├── analyzers/
│   │   └── doc_analyzer.py          # Existant (enrichir détection)
│   ├── dialogue/
│   │   └── needs_assessor.py        # Existant
│   └── generators/
│       ├── agent_builder.py         # Existant
│       └── catalog_v2.py            # NOUVEAU - Catalogue enrichi
├── demo/
│   ├── run_demo.py                  # V1 - Inchangé
│   ├── run_demo_v2.py               # NOUVEAU - Demo V2
│   └── lib/
│       ├── __init__.py              # NOUVEAU
│       ├── feedback.py              # NOUVEAU - Module feedback
│       ├── selector.py              # NOUVEAU - Multi-sélection
│       └── batch_generator.py       # NOUVEAU - Génération batch
├── knowledge/
│   └── rules/
│       └── bpce-group-rules.yaml    # Existant
├── generated-agents/                 # Existant
├── ARCHITECTURE.md                   # Mis à jour
├── CADRAGE.md                        # Existant
├── PLAN_V2.md                        # Ce document
└── requirements.txt                  # Existant
```

---

## 5. Estimation Totale

| Étape | Description | Effort Estimé |
|-------|-------------|---------------|
| 1 | Catalogue V2 enrichi | 2-3h |
| 2 | Module feedback | 2h |
| 3 | Module multi-sélection | 1.5h |
| 4 | Générateur batch | 2h |
| 5 | Assemblage demo V2 | 3h |
| 6 | Tests et ajustements | 1.5h |
| **Total** | | **12-13h** |

---

## 6. Critères de Succès

- [ ] La V1 continue de fonctionner sans régression
- [ ] La V2 affiche tous les agents pertinents (pas de limite artificielle)
- [ ] L'utilisateur peut donner son feedback sur chaque proposition
- [ ] L'utilisateur peut sélectionner plusieurs agents
- [ ] Tous les agents sélectionnés sont générés en batch
- [ ] Le contenu des agents est dynamique (adapté au projet analysé)
- [ ] Le mode non-interactif fonctionne avec présets

---

## 7. Risques et Mitigations

| Risque | Impact | Mitigation |
|--------|--------|------------|
| Complexité du catalogue V2 | Moyen | Commencer par 2-3 experts, étendre ensuite |
| UX trop complexe | Moyen | Interface claire, valeurs par défaut sensées |
| Temps de génération batch | Faible | Indicateur de progression, parallélisation future |
| Régression V1 | Moyen | Garder run_demo.py intouché, tests séparés |

---

## 8. Prochaines Actions

1. **Valider ce plan** avec le client
2. **Commencer par l'étape 1** (Catalogue V2) - fondation du reste
3. **Itérer** sur les modules 2-4
4. **Assembler** la demo V2
5. **Tester** et ajuster

---

*Document créé le 2025-11-26*
