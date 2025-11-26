# Architecture Technique - Assistant Architect

**Version** : 1.1.0
**Date** : 2025-11-26
**Statut** : MVP Démo Fonctionnel + V2 en cours

---

## 1. Vue d'Ensemble

### 1.1 Objectif

**Assistant Architect** est un système intelligent de génération d'agents IA spécialisés pour les équipes de développement. Il analyse la documentation d'un projet, dialogue avec l'utilisateur pour comprendre ses besoins, et génère des agents IA contextualisés et conformes aux règles d'entreprise.

### 1.2 Principes Architecturaux

| Principe | Description |
|----------|-------------|
| **LLM-Agnostique** | Support Claude, Gemini, Ollama via couche d'abstraction |
| **Modularité** | Composants indépendants et remplaçables |
| **Conformité** | Règles BPCE intégrées automatiquement |
| **Traçabilité** | Workflow de validation architecte obligatoire |

---

## 2. Architecture Système

### 2.1 Diagramme de Composants

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ASSISTANT ARCHITECT                                  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    ORCHESTRATEUR CENTRAL                             │   │
│  │                      orchestrator.py                                 │   │
│  │         (Gère le flux, maintient le contexte de session)            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│           │              │              │              │                    │
│           ▼              ▼              ▼              ▼                    │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │  ANALYSEUR   │ │  DIALOGUEUR  │ │ GÉNÉRATEUR   │ │  DÉPLOYEUR   │       │
│  │              │ │              │ │              │ │              │       │
│  │doc_analyzer  │ │needs_assessor│ │agent_builder │ │  (to_files)  │       │
│  │     .py      │ │     .py      │ │     .py      │ │              │       │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘       │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                 COUCHE D'ABSTRACTION LLM                             │   │
│  │                    llm_abstraction.py                                │   │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐                        │   │
│  │  │  Claude   │  │  Gemini   │  │  Ollama   │                        │   │
│  │  │  Adapter  │  │  Adapter  │  │  Adapter  │                        │   │
│  │  └───────────┘  └───────────┘  └───────────┘                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    BASES DE CONNAISSANCES                            │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐            │   │
│  │  │  Catalogue    │  │   Règles      │  │   Agents      │            │   │
│  │  │   Agents      │  │    BPCE       │  │   Générés     │            │   │
│  │  └───────────────┘  └───────────────┘  └───────────────┘            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Flux de Données

```
ENTRÉES                         PROCESSUS                          SORTIE
────────                        ─────────                          ──────

┌─────────────────┐
│ Documentation   │────┐
│ MD / HTML       │    │
└─────────────────┘    │      ┌───────────┐      ┌───────────┐
                       ├─────▶│ ANALYSEUR │─────▶│ DIALOGUEUR│──┐
┌─────────────────┐    │      └───────────┘      └───────────┘  │
│ Besoin exprimé  │────┤            │                  │        │
│ par utilisateur │    │            ▼                  ▼        │
└─────────────────┘    │      ProjectProfile    NeedsAssessment │
                       │                                        │
┌─────────────────┐    │                                        │
│ Règles BPCE     │────┤                                        │
│ (YAML)          │    │                                        │    ┌──────────────┐
└─────────────────┘    │      ┌────────────────────────────┐    │    │   AGENT IA   │
                       │      │       GÉNÉRATEUR           │    ├───▶│  SPÉCIALISÉ  │
                       │      │  ┌──────────────────────┐  │    │    │  & VALIDÉ    │
                       │      │  │  AgentRecommender    │  │    │    └──────────────┘
                       │      │  │  AgentBuilder        │  │    │
                       └─────▶│  │  AgentCatalog        │  │────┘
                              │  └──────────────────────┘  │
                              └────────────────────────────┘
                                          │
                                          ▼
                              ┌────────────────────────────┐
                              │   VALIDATION ARCHITECTE    │
                              │   (Approbation requise)    │
                              └────────────────────────────┘
```

---

## 3. Composants Détaillés

### 3.1 Orchestrateur (`src/core/orchestrator.py`)

**Responsabilité** : Coordonne le workflow complet en 6 phases.

```python
class WorkflowState:
    phase: str          # init → analyzing → dialogue → recommending → generating → validating → deploying → complete
    project_profile: ProjectProfile
    needs_assessment: NeedsAssessment
    recommendations: list[AgentRecommendation]
    selected_agent: AgentRecommendation
    generated_agent: GeneratedAgent
    validation_status: str
```

**Phases du Workflow** :

| Phase | Méthode | Entrée | Sortie |
|-------|---------|--------|--------|
| 1. Analyse | `analyze_documentation()` | Path/String | `ProjectProfile` |
| 2. Dialogue | `conduct_dialogue()` | input_func | `NeedsAssessment` |
| 3. Recommandation | `get_recommendations()` | - | `list[AgentRecommendation]` |
| 4. Génération | `generate_agent()` | - | `GeneratedAgent` |
| 5. Validation | `validate()` | approved: bool | bool |
| 6. Déploiement | `deploy()` | target_path | Path |

### 3.2 Couche d'Abstraction LLM (`src/core/llm_abstraction.py`)

**Responsabilité** : Interface unifiée pour tous les providers LLM.

```python
class LLMProvider(ABC):
    @abstractmethod
    def complete(self, prompt: str, system: str | None) -> LLMResponse

    @abstractmethod
    def chat(self, messages: list[Message], system: str | None) -> LLMResponse

    @abstractmethod
    def analyze(self, content: str, schema: dict) -> dict
```

**Adapters Implémentés** :

| Adapter | Provider | Package Requis | Variable d'Environnement |
|---------|----------|----------------|--------------------------|
| `ClaudeAdapter` | Anthropic Claude | `anthropic` | `ANTHROPIC_API_KEY` |
| `GeminiAdapter` | Google Gemini | `google-generativeai` | `GOOGLE_API_KEY` |
| `OllamaAdapter` | Ollama (local) | - | - |

### 3.3 Analyseur de Documentation (`src/analyzers/doc_analyzer.py`)

**Responsabilité** : Extraire l'intelligence projet depuis la documentation.

**Sortie** : `ProjectProfile`

```python
@dataclass
class ProjectProfile:
    name: str                    # Nom du projet
    description: str             # Description extraite
    stack: list[str]             # Technologies détectées
    patterns: list[str]          # Patterns architecturaux
    complexity: str              # low | medium | high
    pain_points: list[str]       # Points de friction identifiés
    conventions: dict            # Conventions de code
    features: list[str]          # Fonctionnalités principales
    dependencies: list[str]      # Dépendances
```

**Détection Automatique** :
- Langages : Python, JavaScript, TypeScript, Java, Go, Rust
- Frameworks : React, Vue, Angular, Spring Boot, Django, FastAPI
- Outils : Docker, Kubernetes, Git, CI/CD

### 3.4 Évaluateur de Besoins (`src/dialogue/needs_assessor.py`)

**Responsabilité** : Dialogue structuré pour comprendre les besoins.

**Sortie** : `NeedsAssessment`

```python
@dataclass
class NeedsAssessment:
    team_size: str               # small | medium | large
    experience_level: str        # junior | mixed | senior
    priority: str                # quality | speed | security | maintainability
    pain_points: list[str]       # Difficultés principales
    sensitive_data: bool         # Données sensibles ?
    compliance_requirements: list[str]  # RGPD, normes internes...
    preferred_tools: list[str]   # Outils préférés
```

**Questions Posées** :

1. Taille de l'équipe
2. Niveau d'expérience
3. Difficultés principales (debugging, tests, onboarding...)
4. Priorité principale
5. Données sensibles à protéger
6. Exigences de conformité

### 3.5 Générateur d'Agents (`src/generators/agent_builder.py`)

**Responsabilité** : Générer des agents IA complets et déployables.

**Catalogue d'Agents** :

| Type | Description | Déclencheurs |
|------|-------------|--------------|
| `debug-helper` | Aide au debugging | logs, errors, stack complexe |
| `code-reviewer` | Review de code | qualité, standards, équipe junior |
| `test-generator` | Génération de tests | coverage, TDD |
| `onboarding-guide` | Guide d'intégration | projet legacy, turnover |
| `security-checker` | Vérification sécurité | données sensibles |
| `api-navigator` | Navigation API | nombreux endpoints |
| `refactoring-advisor` | Conseil refactoring | dette technique |

**Structure d'un Agent Généré** :

```
agent-{name}/
├── AGENT.md              # System prompt + personnalité
├── config.json           # Configuration LLM
├── commands/             # Commandes slash
│   ├── debug.md
│   └── trace.md
├── knowledge/            # Base de connaissances
│   └── architecture.md
├── rules/                # Règles appliquées
│   ├── enterprise.yaml
│   └── bpce-security.yaml
└── hooks/                # Scripts métriques
    ├── on-conversation-start.sh
    ├── on-task-complete.sh
    └── on-code-generated.sh
```

---

## 4. Modèle de Données

### 4.1 Classes Principales

```
┌─────────────────────┐     ┌─────────────────────┐
│   ProjectProfile    │     │   NeedsAssessment   │
├─────────────────────┤     ├─────────────────────┤
│ name                │     │ team_size           │
│ stack[]             │     │ experience_level    │
│ patterns[]          │     │ priority            │
│ complexity          │     │ pain_points[]       │
│ pain_points[]       │     │ sensitive_data      │
└─────────┬───────────┘     └─────────┬───────────┘
          │                           │
          └─────────────┬─────────────┘
                        ▼
          ┌─────────────────────────┐
          │    AgentRecommender     │
          └─────────────┬───────────┘
                        ▼
          ┌─────────────────────────┐
          │  AgentRecommendation[]  │
          ├─────────────────────────┤
          │ agent_type              │
          │ name                    │
          │ priority                │
          │ justification           │
          │ capabilities[]          │
          │ match_score             │
          └─────────────┬───────────┘
                        ▼
          ┌─────────────────────────┐
          │    GeneratedAgent       │
          ├─────────────────────────┤
          │ name                    │
          │ type                    │
          │ system_prompt           │
          │ config{}                │
          │ commands{}              │
          │ knowledge{}             │
          │ rules{}                 │
          │ hooks{}                 │
          └─────────────────────────┘
```

---

## 5. Règles BPCE

### 5.1 Règles Implémentées (Démo)

| ID | Nom | Description |
|----|-----|-------------|
| `BPCE-SEC-001` | Protection données | Pas de PII, données financières, credentials en clair |
| `BPCE-RGPD-001` | Conformité RGPD | Minimisation, finalité, droits d'accès |
| `BPCE-AUDIT-001` | Traçabilité | Logging des actions pour audit |

### 5.2 Application des Règles

Les règles sont :
1. Chargées depuis `knowledge/rules/bpce-group-rules.yaml`
2. Injectées dans l'agent lors de la génération
3. Incluses dans le system prompt
4. Exportées dans `rules/` de l'agent généré

---

## 6. Structure du Projet

```
assistant-architect/
├── src/
│   ├── core/
│   │   ├── orchestrator.py      # Coordinateur central
│   │   └── llm_abstraction.py   # Abstraction LLM multi-provider
│   ├── analyzers/
│   │   └── doc_analyzer.py      # Analyse Markdown/HTML
│   ├── dialogue/
│   │   └── needs_assessor.py    # Questionnaire besoins
│   ├── generators/
│   │   └── agent_builder.py     # Génération d'agents
│   ├── validators/              # (À implémenter)
│   ├── deployers/               # (À implémenter)
│   └── adapters/                # (Extensible)
├── knowledge/
│   └── rules/
│       └── bpce-group-rules.yaml
├── generated-agents/            # Agents générés
├── demo/
│   └── run_demo.py              # Script de démonstration
├── requirements.txt
├── CADRAGE.md                   # Document de cadrage
└── ARCHITECTURE.md              # Ce document
```

---

## 7. Interfaces et API

### 7.1 API Python

```python
from src.core.orchestrator import create_orchestrator

# Créer l'orchestrateur
orchestrator = create_orchestrator(
    provider="claude",           # ou "gemini", "ollama"
    enterprise_rules_path=Path("knowledge/rules/bpce-group-rules.yaml"),
    output_dir=Path("./generated-agents")
)

# Phase 1: Analyser la documentation
profile = orchestrator.analyze_documentation(Path("./docs"))

# Phase 2: Évaluer les besoins (interactif)
assessment = orchestrator.conduct_dialogue()

# Phase 3: Obtenir les recommandations
recommendations = orchestrator.get_recommendations(max_recommendations=3)

# Phase 4: Sélectionner et générer
orchestrator.select_agent(0)
agent = orchestrator.generate_agent()

# Phase 5: Valider
orchestrator.validate(approved=True, validator="architecte")

# Phase 6: Déployer
path = orchestrator.deploy()
```

### 7.2 CLI

```bash
# Mode interactif
python demo/run_demo.py

# Mode non-interactif
python demo/run_demo.py --non-interactive

# Avec un autre provider
python demo/run_demo.py --provider gemini
```

---

## 8. Sécurité

### 8.1 Gestion des Secrets

| Secret | Méthode | Variable |
|--------|---------|----------|
| API Key Claude | Env var | `ANTHROPIC_API_KEY` |
| API Key Gemini | Env var | `GOOGLE_API_KEY` |
| Tokens GitHub | Ne pas committer | `.gitignore` |

### 8.2 Données Sensibles

- Les conversations ne sont pas stockées au-delà de la session
- Les agents générés n'incluent pas de données réelles
- Les règles BPCE filtrent les données sensibles

---

## 9. Architecture V2 - Man in the Loop

### 9.1 Objectifs V2

La version 2 introduit :
- **Catalogue enrichi** : Experts techniques + Assistants transversaux
- **Recommandations dynamiques** : Adaptées à chaque projet analysé
- **Feedback utilisateur** : Retours sur les propositions avant sélection
- **Multi-sélection** : Génération de plusieurs agents en batch
- **Man in the loop** : L'utilisateur guide le processus de recommandation

### 9.2 Nouveau Workflow (8 phases)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DEMO V2 - WORKFLOW                                 │
│                                                                             │
│  Phase 1          Phase 2         Phase 3           Phase 4                 │
│  ┌─────────┐      ┌─────────┐     ┌─────────────┐   ┌─────────────┐        │
│  │ ANALYSE │─────▶│ DIALOGUE│────▶│ RECOMMAND.  │──▶│ FEEDBACK    │        │
│  │         │      │         │     │ (dynamique) │   │ (man in     │        │
│  └─────────┘      └─────────┘     └─────────────┘   │  the loop)  │        │
│                                                      └──────┬──────┘        │
│                                                             │               │
│                     ┌───────────────────────────────────────┘               │
│                     ▼                                                       │
│  Phase 5           Phase 6         Phase 7          Phase 8                 │
│  ┌─────────────┐   ┌─────────────┐ ┌─────────────┐  ┌─────────────┐        │
│  │ SÉLECTION   │──▶│ GÉNÉRATION  │▶│ VALIDATION  │─▶│ DÉPLOIEMENT │        │
│  │ (multiple)  │   │ (batch)     │ │ (par agent) │  │ (batch)     │        │
│  └─────────────┘   └─────────────┘ └─────────────┘  └─────────────┘        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.3 Catalogue V2 - Approche Hybride

Le catalogue V2 combine deux catégories d'agents :

#### Experts Techniques (par domaine)

Spécialisés par stack technologique, **générés dynamiquement** selon le projet analysé.

| Expert | Spécialisations | Détection |
|--------|-----------------|-----------|
| 🎨 **Frontend Expert** | React, Vue, Angular, TypeScript, CSS, Tailwind | Frameworks JS détectés |
| ⚙️ **Backend Expert** | Spring Boot, Django, Node.js, FastAPI, Go, Rust | Frameworks backend détectés |
| 🗄️ **Data Expert** | PostgreSQL, MongoDB, Redis, ETL, BigData | Base de données détectées |
| 🚀 **DevOps Expert** | Docker, Kubernetes, Terraform, CI/CD, Ansible | Fichiers infra détectés |
| 📱 **Mobile Expert** | iOS/Swift, Android/Kotlin, Flutter, React Native | SDK mobile détectés |
| ☁️ **Cloud Expert** | AWS, GCP, Azure, Serverless | Services cloud détectés |

#### Assistants Transversaux (par besoin)

Recommandés selon les besoins identifiés lors du dialogue.

| Assistant | Déclencheurs | Capacités |
|-----------|--------------|-----------|
| 🔒 **Security Checker** | Données sensibles, compliance | OWASP, secrets, audit |
| 📚 **Onboarding Guide** | Équipe mixte/junior, projet complexe | Architecture, conventions |
| 📝 **Doc Generator** | Documentation manquante | README, API docs, comments |
| ♻️ **Refactoring Advisor** | Dette technique identifiée | Clean code, patterns, SOLID |
| ⚡ **Performance Optimizer** | Problèmes de perf signalés | Profiling, caching, lazy loading |
| 🧪 **Test Advisor** | Coverage faible, besoin TDD | Unit tests, mocking, E2E |

### 9.4 Génération Dynamique

Les agents ne sont **pas hardcodés**. Le contenu est généré dynamiquement :

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     GÉNÉRATION DYNAMIQUE                                     │
│                                                                             │
│   REPO ENTRANT              ANALYSE                 AGENT GÉNÉRÉ            │
│                                                                             │
│   ┌─────────────┐      ┌─────────────────┐      ┌─────────────────────┐    │
│   │ Project A   │      │ Stack détectée: │      │ Frontend Expert     │    │
│   │ - React 18  │─────▶│ - React 18      │─────▶│                     │    │
│   │ - TypeScript│      │ - TypeScript    │      │ Spécialisé React:   │    │
│   │ - Tailwind  │      │ - Tailwind      │      │ - Hooks patterns    │    │
│   └─────────────┘      └─────────────────┘      │ - State management  │    │
│                                                 │ - Testing RTL       │    │
│                                                 │ - Performance React │    │
│                                                 └─────────────────────┘    │
│                                                                             │
│   ┌─────────────┐      ┌─────────────────┐      ┌─────────────────────┐    │
│   │ Project B   │      │ Stack détectée: │      │ Frontend Expert     │    │
│   │ - Vue 3     │─────▶│ - Vue 3         │─────▶│                     │    │
│   │ - Pinia     │      │ - Pinia         │      │ Spécialisé Vue:     │    │
│   │ - Vite      │      │ - Vite          │      │ - Composition API   │    │
│   └─────────────┘      └─────────────────┘      │ - Pinia patterns    │    │
│                                                 │ - Testing Vitest    │    │
│                                                 │ - Performance Vue   │    │
│                                                 └─────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Éléments dynamiques** :
- Spécialisations de l'expert (selon technos détectées)
- System prompt (contextualisé au projet)
- Commandes disponibles (adaptées à la stack)
- Base de connaissances (conventions du projet)
- Score de pertinence (calculé pour chaque projet)

**Éléments statiques** :
- Types d'experts possibles (catalogue de base)
- Structure des agents générés
- Règles BPCE (appliquées uniformément)

### 9.5 Phase Feedback (Nouvelle)

L'utilisateur peut donner son avis sur chaque recommandation :

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    FEEDBACK SUR LES RECOMMANDATIONS                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Pour chaque agent, indiquez votre intérêt :                                ║
║                                                                              ║
║  1. Frontend Expert (React/TypeScript) 🔴 [HIGH]                            ║
║     └─ Votre avis: [1] Très utile  [2] Peut-être  [3] Pas pertinent         ║
║     └─ Commentaire (optionnel): ___________________________________         ║
║                                                                              ║
║  2. Backend Expert (Node.js) 🔴 [HIGH]                                      ║
║     └─ Votre avis: [1] Très utile  [2] Peut-être  [3] Pas pertinent         ║
║                                                                              ║
║  [R] Raffiner les recommandations avec mes retours                          ║
║  [S] Passer à la sélection                                                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### 9.6 Multi-Sélection et Génération Batch

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    SÉLECTION DES AGENTS À GÉNÉRER                            ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  📦 EXPERTS TECHNIQUES                                                       ║
║  [X] 1. Frontend Expert (React/TypeScript)         🔴 HIGH                  ║
║  [X] 2. Backend Expert (Node.js)                   🔴 HIGH                  ║
║  [ ] 3. Data Expert (MongoDB)                      🟡 MEDIUM                ║
║                                                                              ║
║  🔧 ASSISTANTS TRANSVERSAUX                                                  ║
║  [X] 4. Security Checker                           🔴 HIGH                  ║
║  [ ] 5. Onboarding Guide                           🟡 MEDIUM                ║
║                                                                              ║
║  Sélection: 1,2,4                                                            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════════════════╗
║                    GÉNÉRATION BATCH (3 agents)                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  [████████████████████████████████████████] 100%                            ║
║                                                                              ║
║  ✅ 1/3 Frontend Expert (React) .......... Généré                           ║
║  ✅ 2/3 Backend Expert (Node.js) ......... Généré                           ║
║  ✅ 3/3 Security Checker ................. Généré                           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### 9.7 Structure Fichiers V2

```
assistant-architect/
├── demo/
│   ├── run_demo.py              # V1 (conservée)
│   ├── run_demo_v2.py           # V2 (nouvelle)
│   └── lib/
│       ├── __init__.py
│       ├── feedback.py          # Module feedback utilisateur
│       ├── selector.py          # Module multi-sélection
│       └── batch_generator.py   # Génération batch
├── src/
│   └── generators/
│       ├── agent_builder.py     # V1 (existant)
│       └── catalog_v2.py        # Catalogue enrichi V2
└── ...
```

### 9.8 CLI V2

```bash
# V1 (inchangée)
python demo/run_demo.py
python demo/run_demo.py --non-interactive

# V2 (nouvelle)
python demo/run_demo_v2.py
python demo/run_demo_v2.py --non-interactive
python demo/run_demo_v2.py --max-agents 10
python demo/run_demo_v2.py --export-feedback feedback.json
```

---

## 10. Évolutions Futures (v3+)

| Fonctionnalité | Description | Priorité |
|----------------|-------------|----------|
| Métriques complètes | Hooks fonctionnels avec collecte | Haute |
| UI Web | Interface de validation architecte | Moyenne |
| Versioning agents | Gestion des versions et rollback | Moyenne |
| Multi-repo | Analyse de plusieurs repos simultanément | Basse |
| Fine-tuning | Adaptation des prompts par retours utilisateurs | Basse |

---

## 11. Références

- [CADRAGE.md](./CADRAGE.md) - Document de cadrage complet
- [knowledge/rules/bpce-group-rules.yaml](./knowledge/rules/bpce-group-rules.yaml) - Règles BPCE
- [demo/run_demo.py](./demo/run_demo.py) - Script de démonstration

---

*Document généré le 2025-11-26*
