# Assistant Architect - Document de Cadrage

**Client** : Direction Architecture - Groupe BPCE
**Statut** : Phase de cadrage
**Date** : 2025-11-25

---

## 1. Contexte & Vision

### Situation Actuelle
Le client dispose déjà d'agents IA qui génèrent automatiquement de la documentation à partir de repositories de code.

### Besoin Exprimé
Créer un système intelligent capable de :
1. **Analyser** la documentation générée
2. **Dialoguer** avec l'utilisateur (chef de projet/architecte) pour comprendre ses besoins
3. **Recommander** les assistants IA les plus pertinents pour l'équipe
4. **Générer** ces assistants configurés et contextualisés
5. **Déployer** dans l'environnement cible

### Vision Long Terme
- Ajouter des commandes pour collecter des métriques d'entreprise
- Collecter des données pour l'entraînement de futurs modèles IA internes
- Intégrer les règles métier bancaires

### Philosophie
> **"System first, implementation second"**
>
> Architecture LLM-agnostique, déclinable sur Claude, Gemini, ou modèles ouverts.

---

## 2. Décisions Confirmées

| Élément | Décision |
|---------|----------|
| LLM | **Agnostique** - Gemini, Claude, modèles ouverts |
| Réseau | **Connecté** (démo autonome requise) |
| Audience démo | Directeur Architecture + équipe architectes |
| Utilisateurs finaux | Développeurs (adoption critique) |
| Coeur du système | Détermination intelligente du type d'assistant |
| Capacités assistants | **Agents IA complets** - skills, commands, exécution |
| Validation | **Oui** - approbation architecte avant déploiement |
| Mises à jour | **À prévoir** - versioning, rollback (v2) |
| Règles métier | **Hybride** - centralisées groupe + spécifiques projet |
| Format source | **Markdown + HTML** |
| Interface démo | **CLI ou VS Code** |
| LLM démo | **Claude** (choix par défaut) |
| Données démo | **Repo existant** (à fournir) |
| Environnement cible | **Poste développeur** (CLI, VS Code, IDE) |

---

## 3. Architecture Proposée

### 3.1 Vue Globale

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ASSISTANT ARCHITECT                                  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    ORCHESTRATEUR CENTRAL                             │   │
│  │         (Gère le flux, maintient le contexte de session)            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│           │              │              │              │                    │
│           ▼              ▼              ▼              ▼                    │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │  ANALYSEUR   │ │  DIALOGUEUR  │ │ GÉNÉRATEUR   │ │  DÉPLOYEUR   │       │
│  │              │ │              │ │              │ │              │       │
│  │ - Parse docs │ │ - Questions  │ │ - Templates  │ │ - Packager   │       │
│  │ - Extrait    │ │ - Clarifier  │ │ - Assembler  │ │ - Installer  │       │
│  │   contexte   │ │ - Valider    │ │ - Valider    │ │ - Vérifier   │       │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘       │
│                          │                                                  │
│                          ▼                                                  │
│                 ┌──────────────────┐                                       │
│                 │   VALIDATEUR     │  ← Approbation architecte             │
│                 │   (Workflow)     │                                       │
│                 └──────────────────┘                                       │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      COUCHE D'ABSTRACTION LLM                        │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐                 │   │
│  │  │ Claude  │  │ Gemini  │  │ Ollama  │  │ Azure   │  ...            │   │
│  │  │ Adapter │  │ Adapter │  │ Adapter │  │ OpenAI  │                 │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      BASES DE CONNAISSANCES                          │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐            │   │
│  │  │  Catalogue    │  │   Règles      │  │  Templates    │            │   │
│  │  │  Capacités    │  │  BPCE+Projet  │  │  Assistants   │            │   │
│  │  └───────────────┘  └───────────────┘  └───────────────┘            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                 COUCHE MÉTRIQUES & TÉLÉMÉTRIE (v2+)                  │   │
│  │  - Hooks sur les interactions                                        │   │
│  │  - Collecte anonymisée pour entraînement                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Flux de Création d'un Assistant

```
ENTRÉES                              PROCESSUS                         SORTIE
────────                             ─────────                         ──────

┌─────────────────┐
│ Documentation   │───┐
│ MD / HTML       │   │
└─────────────────┘   │      ┌───────────┐      ┌───────────┐
                      ├─────▶│ ANALYSEUR │─────▶│ DIALOGUEUR│──┐
┌─────────────────┐   │      └───────────┘      └───────────┘  │
│ Besoin exprimé  │───┤                                        │
│ par utilisateur │   │                                        │
└─────────────────┘   │                                        │
                      │      ┌────────────────────────────┐    │
┌─────────────────┐   │      │      PROFIL PROJET         │    │
│ Règles BPCE     │───┤      │  - Stack technique         │    │
│ (centralisées)  │   │      │  - Besoins clarifiés       │    │
└─────────────────┘   │      │  - Contraintes métier      │    │
                      │      └────────────────────────────┘    │
┌─────────────────┐   │                   │                    │
│ Règles Projet   │───┘                   ▼                    │
│ (spécifiques)   │          ┌────────────────────────────┐    │    ┌──────────────┐
└─────────────────┘          │       GÉNÉRATEUR           │    │    │   AGENT IA   │
                             │  - Skills custom           │    ├───▶│  SPÉCIALISÉ  │
┌─────────────────┐          │  - Commands                │    │    │  & VALIDÉ    │
│ Environnement   │─────────▶│  - Hooks métriques        │    │    └──────────────┘
│ cible           │          └────────────────────────────┘    │
└─────────────────┘                       │                    │
                                          ▼                    │
                             ┌────────────────────────────┐    │
                             │   VALIDATION ARCHITECTE    │────┘
                             │   (avant déploiement)      │
                             └────────────────────────────┘
```

### 3.3 Détail des Composants

#### ANALYSEUR
Extrait l'intelligence du projet à partir de la documentation.

**Entrées** : Documentation MD/HTML, fichiers config, README
**Sortie** : `project-profile.json`

```json
{
  "stack": ["Java", "Spring Boot", "PostgreSQL"],
  "patterns": ["microservices", "event-driven"],
  "complexity": "high",
  "pain_points": ["debugging distributed", "test coverage"],
  "conventions": {...}
}
```

#### DIALOGUEUR
Clarifie les besoins via conversation structurée.

| Phase | Objectif | Exemple |
|-------|----------|---------|
| Contexte | Comprendre l'équipe | "Taille de l'équipe ? Niveau ?" |
| Douleurs | Identifier frictions | "Qu'est-ce qui ralentit le plus ?" |
| Priorités | Hiérarchiser | "Debug rapide ou qualité code ?" |
| Contraintes | Intégrer métier | "Données sensibles à protéger ?" |
| Validation | Confirmer | "Je propose X, Y, Z - OK ?" |

**Sortie** : `needs-assessment.json`

#### GÉNÉRATEUR
Assemble un **agent IA complet** avec toutes les capacités.

**Structure d'un Agent généré** :
```
agent-{name}/
├── AGENT.md              # System prompt + personnalité
├── config.json           # Paramètres (modèle, température...)
├── skills/               # Capacités spécialisées
│   ├── code-analysis.py
│   ├── test-runner.py
│   └── doc-generator.py
├── commands/             # Commandes slash
│   ├── review.md
│   ├── debug.md
│   └── test.md
├── knowledge/            # Contexte projet injecté
│   ├── architecture.md
│   └── conventions.md
├── rules/                # Contraintes métier
│   ├── bpce-group.yaml       # Règles centralisées
│   └── project-specific.yaml # Règles projet
└── hooks/                # Points d'extension (métriques v2)
    ├── on-conversation-start.sh
    ├── on-task-complete.sh
    └── on-code-generated.sh
```

#### VALIDATEUR
Workflow d'approbation avant déploiement.

| Étape | Action | Responsable |
|-------|--------|-------------|
| 1 | Génération agent | Système |
| 2 | Review configuration | Architecte |
| 3 | Validation règles BPCE | Auto (check) |
| 4 | Approbation finale | Architecte |
| 5 | Déploiement | Système |

#### DÉPLOYEUR
Packager et installer dans l'environnement cible.

| Cible | Format | Méthode |
|-------|--------|---------|
| Claude Code | .claude/ | Copy fichiers |
| VS Code | Extension config | JSON settings |
| CLI custom | Script + config | Installeur |

### 3.4 Catalogue des Types d'Agents

| Type | Déclencheur (détecté) | Valeur |
|------|----------------------|--------|
| **Debug Helper** | Stack complexe, logs | Accélère résolution incidents |
| **Code Reviewer** | Standards qualité, équipe junior | Homogénéise le code |
| **Test Generator** | Coverage faible | Augmente couverture |
| **Onboarding Guide** | Projet legacy, turnover | Réduit montée en compétence |
| **API Navigator** | Nombreux endpoints | Facilite consommation API |
| **Security Checker** | Données sensibles | Réduit risques |
| **Refactoring Advisor** | Dette technique | Guide modernisation |

### 3.5 Stratégie LLM-Agnostique

```python
# Interface commune
class LLMProvider(ABC):
    def complete(self, prompt: str, context: dict) -> str: ...
    def analyze(self, content: str, schema: dict) -> dict: ...
    def converse(self, messages: list, system: str) -> str: ...

# Adapters spécifiques
class ClaudeAdapter(LLMProvider): ...
class GeminiAdapter(LLMProvider): ...
class OllamaAdapter(LLMProvider): ...
```

---

## 4. Règles BPCE (Groupe)

### 4.1 Architecture des Règles

```
┌─────────────────────────────────────────────────────────────┐
│                    RÈGLES BPCE GROUPE                        │
│            (Obligatoires pour tous les projets)              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ Sécurité    │  │ Conformité  │  │ Traçabilité │          │
│  │ données     │  │ RGPD        │  │ audit       │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   RÈGLES PROJET/ÉQUIPE                       │
│              (Spécifiques, optionnelles)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ Conventions │  │ Patterns    │  │ Outils      │          │
│  │ code        │  │ archi       │  │ autorisés   │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Règles Groupe BPCE (Démo)

```yaml
# bpce-group-rules.yaml
# Règles obligatoires pour tous les agents IA du groupe BPCE

version: "1.0"
scope: "group"
mandatory: true

rules:

  # ═══════════════════════════════════════════════════════════
  # RÈGLE 1 : PROTECTION DES DONNÉES SENSIBLES
  # ═══════════════════════════════════════════════════════════
  data_protection:
    id: "BPCE-SEC-001"
    name: "Protection des données bancaires et personnelles"
    description: |
      L'agent IA ne doit JAMAIS traiter, stocker ou transmettre
      de données sensibles en clair dans ses interactions.

    prohibited_data:
      - type: "PII"
        examples: ["numéro client", "nom complet", "adresse", "email personnel"]
        action: "mask_or_reject"
      - type: "FINANCIAL"
        examples: ["IBAN", "numéro de carte", "RIB", "solde compte"]
        action: "reject"
      - type: "CREDENTIALS"
        examples: ["mot de passe", "token API", "clé SSH", "certificat"]
        action: "reject_and_alert"

    validation:
      - "Scan automatique des prompts entrants"
      - "Scan des réponses générées avant affichage"
      - "Blocage immédiat si données sensibles détectées"

    message_on_violation: |
      ⚠️ DONNÉES SENSIBLES DÉTECTÉES
      Cette requête contient des données protégées ({{type}}).
      Veuillez reformuler sans inclure : {{detected_items}}

  # ═══════════════════════════════════════════════════════════
  # RÈGLE 2 : CONFORMITÉ RGPD
  # ═══════════════════════════════════════════════════════════
  rgpd_compliance:
    id: "BPCE-RGPD-001"
    name: "Conformité au Règlement Général sur la Protection des Données"
    description: |
      Toute interaction avec l'agent doit respecter les principes
      du RGPD : minimisation, finalité, conservation limitée.

    principles:
      minimisation:
        description: "Ne collecter que les données strictement nécessaires"
        implementation:
          - "Pas de stockage des conversations au-delà de la session"
          - "Pas de profilage utilisateur"
          - "Anonymisation des logs techniques"

      finalite:
        description: "Utilisation uniquement pour l'aide au développement"
        prohibited_uses:
          - "Analyse comportementale des développeurs"
          - "Évaluation de performance individuelle"
          - "Marketing ou recommandation commerciale"

      droit_acces:
        description: "L'utilisateur peut demander ses données"
        implementation:
          - "Commande /mes-donnees disponible"
          - "Export possible en JSON"
          - "Suppression sur demande"

    audit:
      frequency: "mensuel"
      responsible: "DPO BPCE"

  # ═══════════════════════════════════════════════════════════
  # RÈGLE 3 : TRAÇABILITÉ ET AUDIT
  # ═══════════════════════════════════════════════════════════
  traceability:
    id: "BPCE-AUDIT-001"
    name: "Traçabilité des actions pour audit réglementaire"
    description: |
      Toutes les actions significatives de l'agent doivent être
      tracées pour permettre un audit a posteriori.

    logged_events:
      - event: "session_start"
        data: ["timestamp", "user_id_hash", "project_id", "agent_type"]
      - event: "code_generated"
        data: ["timestamp", "file_path", "language", "lines_count"]
      - event: "code_modified"
        data: ["timestamp", "file_path", "diff_hash", "validation_status"]
      - event: "command_executed"
        data: ["timestamp", "command_name", "exit_code"]
      - event: "rule_violation_attempt"
        data: ["timestamp", "rule_id", "severity", "action_taken"]

    storage:
      format: "JSON structured"
      retention: "12 mois"
      location: "SIEM interne BPCE"
      encryption: "AES-256"

    access:
      - role: "audit_interne"
        permission: "read"
      - role: "security_team"
        permission: "read"
      - role: "compliance_officer"
        permission: "read_export"

    reports:
      - name: "Rapport mensuel d'activité"
        content: ["nb_sessions", "nb_generations", "violations"]
      - name: "Rapport d'incident"
        trigger: "rule_violation"
        content: ["full_context", "user_action", "remediation"]
```

### 4.3 Exemple de Règles Projet (Override possible)

```yaml
# project-rules.yaml (exemple)
version: "1.0"
scope: "project"
project_id: "PROJ-12345"

extends: "bpce-group-rules"  # Hérite des règles groupe

rules:
  coding_conventions:
    id: "PROJ-CONV-001"
    java:
      style: "Google Java Style"
      max_line_length: 120
      enforce_javadoc: true

  allowed_frameworks:
    id: "PROJ-TECH-001"
    backend: ["Spring Boot 3.x", "Quarkus"]
    frontend: ["Angular 17+", "React 18+"]
    database: ["PostgreSQL", "Oracle"]
    messaging: ["Kafka", "RabbitMQ"]

  restricted_actions:
    id: "PROJ-SEC-001"
    - action: "direct_database_query"
      allowed: false
      reason: "Utiliser les repositories Spring Data"
    - action: "external_api_call"
      allowed: "with_approval"
      approver: "tech_lead"
```

---

## 5. Démonstrateur (1 semaine)

### Objectif
Illustrer le flux complet de manière simplifiée mais fonctionnelle.

### Scope Démo

| Composant | Démo | Complet |
|-----------|------|---------|
| Analyseur | MD + HTML | Multi-format |
| Dialogueur | 5-7 questions | Conversation libre |
| Catalogue | 3 types d'agents | N extensibles |
| Générateur | Skills + commands | Agents complets |
| Validateur | Check basique | Workflow complet |
| Déployeur | VS Code / CLI | Multi-cibles |
| Règles BPCE | 3 règles démo | Catalogue complet |
| Métriques | Hooks préparés | Implémentés |

### Scénario de Démo

```
1. INPUT
   └── Repo existant + documentation MD/HTML

2. ANALYSE (30 sec)
   └── "J'ai analysé votre projet : Spring Boot, microservices,
        complexité élevée sur Kafka..."

3. DIALOGUE (2-3 min)
   └── Questions ciblées sur l'équipe, les frictions, les contraintes

4. RECOMMANDATION
   └── "Je recommande 3 agents :
        1. Kafka Debug Helper (priorité haute)
        2. Code Reviewer Spring (priorité moyenne)
        3. Test Generator (priorité basse)

        Voulez-vous que je génère le premier ?"

5. GÉNÉRATION
   └── Création de l'agent avec :
        - Skills spécialisés Kafka
        - Commands /debug, /trace, /explain-error
        - Règles BPCE injectées
        - Hooks métriques préparés

6. VALIDATION
   └── Review par architecte (écran récapitulatif)

7. DÉPLOIEMENT
   └── Installation dans VS Code ou CLI
```

### Stack Technique Démo

```
assistant-architect/
├── src/
│   ├── core/
│   │   ├── orchestrator.py
│   │   ├── llm_abstraction.py
│   │   └── session.py
│   ├── analyzers/
│   │   ├── markdown_analyzer.py
│   │   └── html_analyzer.py
│   ├── dialogue/
│   │   └── needs_assessor.py
│   ├── generators/
│   │   ├── agent_builder.py
│   │   ├── skill_generator.py
│   │   └── command_generator.py
│   ├── validators/
│   │   └── approval_workflow.py
│   ├── deployers/
│   │   ├── vscode_deployer.py
│   │   └── cli_deployer.py
│   └── adapters/
│       └── claude_adapter.py
├── knowledge/
│   ├── agent_catalog.yaml
│   ├── rules/
│   │   ├── bpce-group-rules.yaml
│   │   └── sample-project-rules.yaml
│   └── templates/
│       ├── debug-agent/
│       ├── reviewer-agent/
│       └── test-agent/
├── demo/
│   └── run_demo.py
└── config/
    └── providers.yaml
```

---

## 6. Adoption Développeurs

### Facteurs Clés de Succès

| Facteur | Comment l'adresser |
|---------|-------------------|
| Valeur immédiate | Agent utilisable en <5 min |
| Pas de friction | Intégration VS Code / CLI native |
| Pertinence | Contexte projet réel, pas générique |
| Confiance | Transparence sur les actions |
| Conformité | Règles BPCE automatiquement appliquées |

### Anti-patterns à Éviter
- Agent trop générique (pas mieux que ChatGPT)
- Configuration complexe
- Déconnexion avec la réalité du code
- Règles trop restrictives qui bloquent

---

## 7. Prochaines Étapes

- [x] Définir les capacités des agents (A1)
- [x] Confirmer workflow validation (A2)
- [x] Prévoir versioning (A3)
- [x] Architecture règles hybride (A4)
- [x] Définir règles BPCE démo (C3)
- [x] Préciser environnement cible (C2) → **Poste développeur**
- [ ] Recevoir repo de démo
- [ ] Valider architecture globale
- [ ] Démarrer développement

---

## 8. Notes de Session

### Session 1 - 2025-11-25
- Initialisation du projet dans `/home/jimb/Projects/Assisstant Architect`
- Architecture système proposée et validée
- **Toutes les questions de cadrage répondues**
- Règles BPCE démo définies (3 règles)
- Environnement cible : poste développeur (CLI/VS Code)
- **CADRAGE COMPLET** - Prêt pour développement

---

*Document vivant - Mis à jour à chaque session*
