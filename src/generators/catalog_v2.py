"""
Catalog V2 - Enhanced agent catalog with Technical Experts and Transversal Assistants.

This catalog provides dynamic agent recommendations based on:
- Technical Experts: Specialized by detected stack (Frontend, Backend, Data, DevOps, Mobile, Cloud)
- Transversal Assistants: Based on user needs (Security, Onboarding, Docs, Refactoring, Perf, Tests)

Key principle: Recommendations are DYNAMIC, not hardcoded. The content adapts to each project.
"""

from dataclasses import dataclass, field
from typing import Any

import sys
from pathlib import Path

# Ensure src is in path
_src_path = str(Path(__file__).parent.parent)
if _src_path not in sys.path:
    sys.path.insert(0, _src_path)

try:
    from analyzers.doc_analyzer import ProjectProfile
    from dialogue.needs_assessor import NeedsAssessment
    from generators.agent_builder import AgentCapability, AgentRecommendation
except ImportError:
    from ..analyzers.doc_analyzer import ProjectProfile
    from ..dialogue.needs_assessor import NeedsAssessment
    from .agent_builder import AgentCapability, AgentRecommendation


# =============================================================================
# SPECIALIZATION DEFINITIONS
# =============================================================================

@dataclass
class TechSpecialization:
    """A technology specialization within an expert domain."""
    name: str
    keywords: list[str]  # Detection keywords
    capabilities: list[str]  # Specific capabilities for this tech
    commands: list[str]  # Suggested slash commands


# Frontend specializations
FRONTEND_SPECIALIZATIONS = {
    "react": TechSpecialization(
        name="React",
        keywords=["react", "jsx", "tsx", "next.js", "nextjs", "redux", "zustand", "react-query"],
        capabilities=["Hooks patterns", "State management (Redux/Zustand)", "React Testing Library", "Performance optimization (memo, lazy)"],
        commands=["/component", "/hook", "/test-rtl"]
    ),
    "vue": TechSpecialization(
        name="Vue.js",
        keywords=["vue", "vuex", "pinia", "nuxt", "vite"],
        capabilities=["Composition API", "Pinia/Vuex patterns", "Vue Test Utils", "Nuxt conventions"],
        commands=["/component", "/composable", "/test-vue"]
    ),
    "angular": TechSpecialization(
        name="Angular",
        keywords=["angular", "@angular", "ngrx", "rxjs"],
        capabilities=["RxJS patterns", "NgModules vs Standalone", "Angular Testing", "Signals"],
        commands=["/component", "/service", "/test-angular"]
    ),
    "svelte": TechSpecialization(
        name="Svelte",
        keywords=["svelte", "sveltekit"],
        capabilities=["Svelte stores", "SvelteKit routing", "Svelte testing"],
        commands=["/component", "/store"]
    ),
    "typescript": TechSpecialization(
        name="TypeScript",
        keywords=["typescript", ".ts", "tsconfig"],
        capabilities=["Type definitions", "Generics", "Utility types", "Type guards"],
        commands=["/types", "/interface"]
    ),
}

# Backend specializations
BACKEND_SPECIALIZATIONS = {
    "spring": TechSpecialization(
        name="Spring Boot",
        keywords=["spring", "spring-boot", "springboot", "pom.xml", "gradle", "java", ".java"],
        capabilities=["Spring MVC/WebFlux", "JPA/Hibernate", "Spring Security", "Testing (JUnit/Mockito)"],
        commands=["/controller", "/service", "/repository", "/test-spring"]
    ),
    "django": TechSpecialization(
        name="Django",
        keywords=["django", "djangorestframework", "drf"],
        capabilities=["Django ORM", "DRF serializers", "Django testing", "Celery tasks"],
        commands=["/view", "/model", "/serializer", "/test-django"]
    ),
    "fastapi": TechSpecialization(
        name="FastAPI",
        keywords=["fastapi", "uvicorn", "starlette"],
        capabilities=["Pydantic models", "Dependency injection", "Async patterns", "OpenAPI"],
        commands=["/endpoint", "/schema", "/test-fastapi"]
    ),
    "nodejs": TechSpecialization(
        name="Node.js",
        keywords=["express", "nestjs", "koa", "node", "npm", "package.json"],
        capabilities=["Express/NestJS patterns", "Middleware", "Async/await", "Jest testing"],
        commands=["/route", "/middleware", "/test-node"]
    ),
    "go": TechSpecialization(
        name="Go",
        keywords=["golang", "go.mod", "go.sum", ".go"],
        capabilities=["Go idioms", "Goroutines/channels", "Go testing", "Error handling"],
        commands=["/handler", "/test-go"]
    ),
    "rust": TechSpecialization(
        name="Rust",
        keywords=["rust", "cargo.toml", ".rs"],
        capabilities=["Ownership/borrowing", "Error handling (Result)", "Async Rust", "Testing"],
        commands=["/impl", "/test-rust"]
    ),
}

# Data specializations
DATA_SPECIALIZATIONS = {
    "postgresql": TechSpecialization(
        name="PostgreSQL",
        keywords=["postgres", "postgresql", "psql", "pg_"],
        capabilities=["Query optimization", "Indexing strategies", "Stored procedures", "JSONB"],
        commands=["/query", "/index", "/explain"]
    ),
    "mongodb": TechSpecialization(
        name="MongoDB",
        keywords=["mongodb", "mongoose", "mongo"],
        capabilities=["Aggregation pipelines", "Schema design", "Indexing", "Transactions"],
        commands=["/aggregate", "/schema", "/index"]
    ),
    "redis": TechSpecialization(
        name="Redis",
        keywords=["redis", "ioredis", "redis-py"],
        capabilities=["Caching patterns", "Pub/Sub", "Data structures", "Lua scripts"],
        commands=["/cache", "/pubsub"]
    ),
    "elasticsearch": TechSpecialization(
        name="Elasticsearch",
        keywords=["elasticsearch", "elastic", "opensearch"],
        capabilities=["Query DSL", "Mappings", "Aggregations", "Performance tuning"],
        commands=["/search", "/mapping"]
    ),
    "sql": TechSpecialization(
        name="SQL",
        keywords=["sql", "mysql", "mariadb", "sqlite", ".sql"],
        capabilities=["Query optimization", "Joins", "Indexing", "Transactions"],
        commands=["/query", "/optimize"]
    ),
}

# DevOps specializations
DEVOPS_SPECIALIZATIONS = {
    "docker": TechSpecialization(
        name="Docker",
        keywords=["docker", "dockerfile", "docker-compose", "containerfile"],
        capabilities=["Multi-stage builds", "Compose orchestration", "Security best practices", "Optimization"],
        commands=["/dockerfile", "/compose"]
    ),
    "kubernetes": TechSpecialization(
        name="Kubernetes",
        keywords=["kubernetes", "k8s", "kubectl", "helm", "kustomize"],
        capabilities=["Deployment strategies", "Services/Ingress", "ConfigMaps/Secrets", "Helm charts"],
        commands=["/manifest", "/helm", "/debug-k8s"]
    ),
    "terraform": TechSpecialization(
        name="Terraform",
        keywords=["terraform", ".tf", "tfstate", "hcl"],
        capabilities=["Module design", "State management", "Provider patterns", "Best practices"],
        commands=["/resource", "/module"]
    ),
    "cicd": TechSpecialization(
        name="CI/CD",
        keywords=["github-actions", ".github/workflows", "gitlab-ci", "jenkins", "circleci"],
        capabilities=["Pipeline design", "Testing stages", "Deployment automation", "Security scanning"],
        commands=["/pipeline", "/workflow"]
    ),
    "ansible": TechSpecialization(
        name="Ansible",
        keywords=["ansible", "playbook", ".yml", "inventory"],
        capabilities=["Playbook design", "Roles", "Inventory management", "Vault"],
        commands=["/playbook", "/role"]
    ),
}

# Mobile specializations
MOBILE_SPECIALIZATIONS = {
    "ios": TechSpecialization(
        name="iOS/Swift",
        keywords=["swift", "xcode", "cocoapods", "spm", ".swift", "xcodeproj"],
        capabilities=["SwiftUI/UIKit", "Combine", "Core Data", "XCTest"],
        commands=["/view", "/viewmodel", "/test-ios"]
    ),
    "android": TechSpecialization(
        name="Android/Kotlin",
        keywords=["kotlin", "android", "gradle", ".kt", "jetpack"],
        capabilities=["Jetpack Compose", "Coroutines/Flow", "Room", "Android testing"],
        commands=["/composable", "/viewmodel", "/test-android"]
    ),
    "flutter": TechSpecialization(
        name="Flutter",
        keywords=["flutter", "dart", "pubspec.yaml", ".dart"],
        capabilities=["Widget patterns", "State management (Bloc/Riverpod)", "Platform channels", "Testing"],
        commands=["/widget", "/bloc", "/test-flutter"]
    ),
    "reactnative": TechSpecialization(
        name="React Native",
        keywords=["react-native", "expo", "metro"],
        capabilities=["Native modules", "Navigation", "State management", "Testing"],
        commands=["/screen", "/hook", "/test-rn"]
    ),
}

# Cloud specializations
CLOUD_SPECIALIZATIONS = {
    "aws": TechSpecialization(
        name="AWS",
        keywords=["aws", "lambda", "s3", "dynamodb", "cloudformation", "cdk", "sam"],
        capabilities=["Lambda patterns", "API Gateway", "DynamoDB design", "CloudFormation/CDK"],
        commands=["/lambda", "/cloudformation"]
    ),
    "gcp": TechSpecialization(
        name="Google Cloud",
        keywords=["gcp", "google-cloud", "cloud-functions", "firestore", "bigquery"],
        capabilities=["Cloud Functions", "Firestore", "BigQuery", "Pub/Sub"],
        commands=["/function", "/firestore"]
    ),
    "azure": TechSpecialization(
        name="Azure",
        keywords=["azure", "azure-functions", "cosmosdb", "arm-template"],
        capabilities=["Azure Functions", "CosmosDB", "ARM templates", "Azure DevOps"],
        commands=["/function", "/arm"]
    ),
    "serverless": TechSpecialization(
        name="Serverless",
        keywords=["serverless", "serverless.yml", "netlify", "vercel"],
        capabilities=["Serverless patterns", "Cold start optimization", "Event-driven design"],
        commands=["/function", "/serverless"]
    ),
}


# =============================================================================
# EXPERT DEFINITIONS
# =============================================================================

@dataclass
class ExpertDefinition:
    """Definition of a technical expert."""
    id: str
    name: str
    icon: str
    description: str
    category: str  # "technical" or "transversal"
    detection_keywords: list[str]
    detection_files: list[str]
    specializations: dict[str, TechSpecialization]
    base_capabilities: list[AgentCapability]


TECHNICAL_EXPERTS = {
    "frontend-expert": ExpertDefinition(
        id="frontend-expert",
        name="Frontend Expert",
        icon="🎨",
        description="Expert en développement frontend et interfaces utilisateur",
        category="technical",
        detection_keywords=["react", "vue", "angular", "svelte", "frontend", "css", "tailwind", "scss"],
        detection_files=["*.tsx", "*.jsx", "*.vue", "angular.json", "next.config.*", "vite.config.*"],
        specializations=FRONTEND_SPECIALIZATIONS,
        base_capabilities=[
            AgentCapability("component-design", "Conception de composants réutilisables", "component", 9),
            AgentCapability("state-management", "Gestion d'état et flux de données", "state", 8),
            AgentCapability("performance", "Optimisation des performances frontend", "slow render", 8),
            AgentCapability("accessibility", "Accessibilité (a11y) et bonnes pratiques", "accessibility", 7),
            AgentCapability("testing", "Tests unitaires et d'intégration frontend", "test", 8),
        ]
    ),
    "backend-expert": ExpertDefinition(
        id="backend-expert",
        name="Backend Expert",
        icon="⚙️",
        description="Expert en développement backend et APIs",
        category="technical",
        detection_keywords=["spring", "django", "fastapi", "express", "nestjs", "api", "rest", "graphql"],
        detection_files=["pom.xml", "build.gradle", "requirements.txt", "go.mod", "Cargo.toml", "package.json"],
        specializations=BACKEND_SPECIALIZATIONS,
        base_capabilities=[
            AgentCapability("api-design", "Conception d'APIs REST/GraphQL", "api", 9),
            AgentCapability("database", "Intégration base de données et ORM", "database", 8),
            AgentCapability("security", "Sécurité backend (auth, validation)", "security", 9),
            AgentCapability("performance", "Optimisation des performances", "slow", 8),
            AgentCapability("testing", "Tests unitaires et d'intégration", "test", 8),
        ]
    ),
    "data-expert": ExpertDefinition(
        id="data-expert",
        name="Data Expert",
        icon="🗄️",
        description="Expert en bases de données et gestion des données",
        category="technical",
        detection_keywords=["postgres", "mongodb", "redis", "elasticsearch", "sql", "database", "etl"],
        detection_files=["*.sql", "docker-compose.yml", "schema.prisma", "migrations/"],
        specializations=DATA_SPECIALIZATIONS,
        base_capabilities=[
            AgentCapability("schema-design", "Conception de schémas de données", "schema", 9),
            AgentCapability("query-optimization", "Optimisation des requêtes", "slow query", 9),
            AgentCapability("indexing", "Stratégies d'indexation", "index", 8),
            AgentCapability("migration", "Migrations de données", "migration", 7),
            AgentCapability("backup", "Stratégies de backup/restore", "backup", 7),
        ]
    ),
    "devops-expert": ExpertDefinition(
        id="devops-expert",
        name="DevOps Expert",
        icon="🚀",
        description="Expert en infrastructure, CI/CD et déploiement",
        category="technical",
        detection_keywords=["docker", "kubernetes", "terraform", "ansible", "cicd", "pipeline", "helm"],
        detection_files=["Dockerfile", "docker-compose.yml", "*.tf", ".github/workflows/*", "k8s/", "helm/"],
        specializations=DEVOPS_SPECIALIZATIONS,
        base_capabilities=[
            AgentCapability("containerization", "Containerisation et orchestration", "docker", 9),
            AgentCapability("ci-cd", "Pipelines CI/CD", "pipeline", 9),
            AgentCapability("infrastructure", "Infrastructure as Code", "infra", 8),
            AgentCapability("monitoring", "Monitoring et observabilité", "monitor", 8),
            AgentCapability("security", "Sécurité DevOps (DevSecOps)", "security", 8),
        ]
    ),
    "mobile-expert": ExpertDefinition(
        id="mobile-expert",
        name="Mobile Expert",
        icon="📱",
        description="Expert en développement mobile (iOS, Android, Cross-platform)",
        category="technical",
        detection_keywords=["ios", "android", "swift", "kotlin", "flutter", "react-native", "mobile"],
        detection_files=["*.swift", "*.kt", "pubspec.yaml", "Podfile", "build.gradle"],
        specializations=MOBILE_SPECIALIZATIONS,
        base_capabilities=[
            AgentCapability("ui-patterns", "Patterns UI mobile", "ui", 9),
            AgentCapability("navigation", "Navigation et routing", "navigation", 8),
            AgentCapability("state", "Gestion d'état mobile", "state", 8),
            AgentCapability("platform", "Intégrations natives", "native", 7),
            AgentCapability("testing", "Tests mobile", "test", 8),
        ]
    ),
    "cloud-expert": ExpertDefinition(
        id="cloud-expert",
        name="Cloud Expert",
        icon="☁️",
        description="Expert en services cloud et architectures serverless",
        category="technical",
        detection_keywords=["aws", "gcp", "azure", "lambda", "serverless", "cloud"],
        detection_files=["serverless.yml", "template.yaml", "cloudformation.yaml", "*.tf"],
        specializations=CLOUD_SPECIALIZATIONS,
        base_capabilities=[
            AgentCapability("architecture", "Architecture cloud", "architecture", 9),
            AgentCapability("serverless", "Patterns serverless", "serverless", 8),
            AgentCapability("cost", "Optimisation des coûts", "cost", 7),
            AgentCapability("security", "Sécurité cloud", "security", 9),
            AgentCapability("scaling", "Auto-scaling et haute disponibilité", "scale", 8),
        ]
    ),
}


# =============================================================================
# TRANSVERSAL ASSISTANT DEFINITIONS
# =============================================================================

TRANSVERSAL_ASSISTANTS = {
    "security-checker": ExpertDefinition(
        id="security-checker",
        name="Security Checker",
        icon="🔒",
        description="Vérification de la sécurité du code et conformité",
        category="transversal",
        detection_keywords=["security", "auth", "password", "token", "secret"],
        detection_files=[".env", "auth/", "security/", "credentials"],
        specializations={},
        base_capabilities=[
            AgentCapability("vulnerability-scan", "Détection de vulnérabilités OWASP", "security", 10),
            AgentCapability("secrets-detection", "Détection de secrets exposés", "secret", 10),
            AgentCapability("compliance-check", "Vérification de conformité", "compliance", 9),
            AgentCapability("code-review-security", "Review sécurité du code", "review", 8),
            AgentCapability("dependency-audit", "Audit des dépendances", "dependency", 8),
        ]
    ),
    "onboarding-guide": ExpertDefinition(
        id="onboarding-guide",
        name="Onboarding Guide",
        icon="📚",
        description="Aide à la montée en compétence sur le projet",
        category="transversal",
        detection_keywords=["readme", "documentation", "getting-started"],
        detection_files=["README.md", "CONTRIBUTING.md", "docs/"],
        specializations={},
        base_capabilities=[
            AgentCapability("architecture-explain", "Explication de l'architecture", "architecture", 9),
            AgentCapability("code-walkthrough", "Parcours guidé du code", "understand", 9),
            AgentCapability("conventions", "Explication des conventions", "convention", 8),
            AgentCapability("setup-guide", "Guide de configuration", "setup", 8),
            AgentCapability("faq", "Réponses aux questions fréquentes", "question", 7),
        ]
    ),
    "doc-generator": ExpertDefinition(
        id="doc-generator",
        name="Doc Generator",
        icon="📝",
        description="Génération et amélioration de la documentation",
        category="transversal",
        detection_keywords=["documentation", "readme", "api-doc"],
        detection_files=["README.md", "docs/", "*.md"],
        specializations={},
        base_capabilities=[
            AgentCapability("readme", "Génération de README", "readme", 9),
            AgentCapability("api-docs", "Documentation API (OpenAPI/Swagger)", "api", 9),
            AgentCapability("code-comments", "Commentaires de code", "comment", 7),
            AgentCapability("changelog", "Génération de changelog", "changelog", 7),
            AgentCapability("diagrams", "Génération de diagrammes", "diagram", 8),
        ]
    ),
    "refactoring-advisor": ExpertDefinition(
        id="refactoring-advisor",
        name="Refactoring Advisor",
        icon="♻️",
        description="Conseil en refactoring et amélioration du code",
        category="transversal",
        detection_keywords=["refactor", "legacy", "technical-debt", "cleanup"],
        detection_files=[],
        specializations={},
        base_capabilities=[
            AgentCapability("code-smells", "Détection de code smells", "smell", 9),
            AgentCapability("patterns", "Suggestion de design patterns", "pattern", 8),
            AgentCapability("solid", "Principes SOLID", "solid", 8),
            AgentCapability("simplification", "Simplification du code", "complex", 8),
            AgentCapability("modularization", "Découpage en modules", "module", 7),
        ]
    ),
    "perf-optimizer": ExpertDefinition(
        id="perf-optimizer",
        name="Performance Optimizer",
        icon="⚡",
        description="Optimisation des performances",
        category="transversal",
        detection_keywords=["performance", "optimization", "slow", "cache", "profiling"],
        detection_files=[],
        specializations={},
        base_capabilities=[
            AgentCapability("profiling", "Analyse de performance", "slow", 9),
            AgentCapability("caching", "Stratégies de cache", "cache", 9),
            AgentCapability("lazy-loading", "Chargement différé", "lazy", 8),
            AgentCapability("memory", "Optimisation mémoire", "memory", 8),
            AgentCapability("database-perf", "Performance base de données", "query", 8),
        ]
    ),
    "test-advisor": ExpertDefinition(
        id="test-advisor",
        name="Test Advisor",
        icon="🧪",
        description="Conseil en stratégie de tests",
        category="transversal",
        detection_keywords=["test", "testing", "coverage", "tdd", "bdd"],
        detection_files=["tests/", "test/", "__tests__/", "*.test.*", "*.spec.*"],
        specializations={},
        base_capabilities=[
            AgentCapability("unit-tests", "Tests unitaires", "unit", 9),
            AgentCapability("integration-tests", "Tests d'intégration", "integration", 8),
            AgentCapability("e2e-tests", "Tests end-to-end", "e2e", 8),
            AgentCapability("mocking", "Stratégies de mocking", "mock", 8),
            AgentCapability("coverage", "Amélioration de la couverture", "coverage", 8),
        ]
    ),
}


# =============================================================================
# CATALOG V2 CLASS
# =============================================================================

class CatalogV2:
    """
    Enhanced catalog with dynamic recommendations.

    Combines Technical Experts and Transversal Assistants to provide
    contextual recommendations based on project analysis.
    """

    def __init__(self):
        self.technical_experts = TECHNICAL_EXPERTS
        self.transversal_assistants = TRANSVERSAL_ASSISTANTS

    def get_all_experts(self) -> dict[str, ExpertDefinition]:
        """Get all technical experts."""
        return self.technical_experts

    def get_all_assistants(self) -> dict[str, ExpertDefinition]:
        """Get all transversal assistants."""
        return self.transversal_assistants

    def get_all_agents(self) -> dict[str, ExpertDefinition]:
        """Get all agents (experts + assistants)."""
        return {**self.technical_experts, **self.transversal_assistants}

    def detect_specializations(
        self,
        expert_id: str,
        profile: ProjectProfile
    ) -> list[TechSpecialization]:
        """
        Detect which specializations apply to this project.

        Returns list of relevant specializations based on project stack.
        """
        expert = self.technical_experts.get(expert_id)
        if not expert or not expert.specializations:
            return []

        detected = []
        profile_text = " ".join([
            " ".join(profile.stack),
            " ".join(profile.patterns),
            " ".join(profile.dependencies),
            profile.raw_content.lower() if profile.raw_content else ""
        ]).lower()

        for spec_id, spec in expert.specializations.items():
            for keyword in spec.keywords:
                if keyword.lower() in profile_text:
                    detected.append(spec)
                    break  # One match is enough

        return detected

    def calculate_expert_score(
        self,
        expert: ExpertDefinition,
        profile: ProjectProfile,
        assessment: NeedsAssessment
    ) -> float:
        """
        Calculate relevance score for a technical expert.

        Score is based on:
        - Detection keywords found in profile (0.4 max)
        - Specializations detected (0.4 max)
        - Assessment alignment (0.2 max)
        """
        score = 0.0

        # Check detection keywords
        profile_text = " ".join([
            " ".join(profile.stack),
            " ".join(profile.patterns),
            " ".join(profile.features),
            profile.description,
        ]).lower()

        keyword_matches = sum(1 for kw in expert.detection_keywords if kw.lower() in profile_text)
        if keyword_matches > 0:
            score += min(0.4, keyword_matches * 0.1)

        # Check specializations
        specs = self.detect_specializations(expert.id, profile)
        if specs:
            score += min(0.4, len(specs) * 0.15)

        # Assessment alignment
        if assessment.main_pain_points:
            pain_text = " ".join(assessment.main_pain_points).lower()
            for cap in expert.base_capabilities:
                if cap.trigger.lower() in pain_text:
                    score += 0.1
                    break

        return min(score, 1.0)

    def calculate_assistant_score(
        self,
        assistant: ExpertDefinition,
        profile: ProjectProfile,
        assessment: NeedsAssessment
    ) -> float:
        """
        Calculate relevance score for a transversal assistant.

        Score is based on:
        - Assessment triggers (0.6 max)
        - Profile analysis (0.4 max)
        """
        score = 0.0

        # Assessment-based scoring
        if assistant.id == "security-checker":
            if assessment.sensitive_data:
                score += 0.5
            if assessment.compliance_requirements:
                score += 0.3

        elif assistant.id == "onboarding-guide":
            if "mixte" in assessment.experience_level.lower():
                score += 0.3
            if "junior" in assessment.experience_level.lower():
                score += 0.4
            if profile.complexity in ["high", "medium"]:
                score += 0.2

        elif assistant.id == "doc-generator":
            pain_text = " ".join(assessment.main_pain_points).lower()
            if "documentation" in pain_text or "doc" in pain_text:
                score += 0.5

        elif assistant.id == "refactoring-advisor":
            pain_text = " ".join(assessment.main_pain_points).lower()
            if "dette" in pain_text or "legacy" in pain_text or "refactor" in pain_text:
                score += 0.5
            if profile.complexity == "high":
                score += 0.2

        elif assistant.id == "perf-optimizer":
            pain_text = " ".join(assessment.main_pain_points).lower()
            if "performance" in pain_text or "lent" in pain_text or "slow" in pain_text:
                score += 0.5

        elif assistant.id == "test-advisor":
            pain_text = " ".join(assessment.main_pain_points).lower()
            if "test" in pain_text or "coverage" in pain_text:
                score += 0.5

        # Profile-based bonus
        profile_text = " ".join([
            " ".join(profile.pain_points),
            profile.description,
        ]).lower()

        for keyword in assistant.detection_keywords:
            if keyword.lower() in profile_text:
                score += 0.1

        return min(score, 1.0)

    def get_recommendations(
        self,
        profile: ProjectProfile,
        assessment: NeedsAssessment,
        min_score: float = 0.2
    ) -> list[AgentRecommendation]:
        """
        Generate dynamic recommendations based on project analysis.

        Returns all agents with score >= min_score, sorted by score.
        No artificial limit on number of recommendations.
        """
        recommendations = []

        # Score technical experts
        for expert_id, expert in self.technical_experts.items():
            score = self.calculate_expert_score(expert, profile, assessment)

            if score >= min_score:
                # Detect specializations for this project
                specs = self.detect_specializations(expert_id, profile)
                spec_names = [s.name for s in specs]

                # Build dynamic name with specializations
                if spec_names:
                    display_name = f"{expert.name} ({'/'.join(spec_names[:2])})"
                else:
                    display_name = expert.name

                # Generate justification
                justification = self._generate_justification(expert, profile, assessment, score, specs)

                # Priority based on score
                priority = "high" if score >= 0.6 else "medium" if score >= 0.4 else "low"

                recommendations.append(AgentRecommendation(
                    agent_type=expert_id,
                    name=display_name,
                    description=expert.description,
                    priority=priority,
                    justification=justification,
                    capabilities=expert.base_capabilities.copy(),
                    match_score=score
                ))

        # Score transversal assistants
        for assistant_id, assistant in self.transversal_assistants.items():
            score = self.calculate_assistant_score(assistant, profile, assessment)

            if score >= min_score:
                justification = self._generate_justification(assistant, profile, assessment, score, [])
                priority = "high" if score >= 0.6 else "medium" if score >= 0.4 else "low"

                recommendations.append(AgentRecommendation(
                    agent_type=assistant_id,
                    name=assistant.name,
                    description=assistant.description,
                    priority=priority,
                    justification=justification,
                    capabilities=assistant.base_capabilities.copy(),
                    match_score=score
                ))

        # Sort by score (highest first)
        recommendations.sort(key=lambda x: x.match_score, reverse=True)

        return recommendations

    def _generate_justification(
        self,
        agent: ExpertDefinition,
        profile: ProjectProfile,
        assessment: NeedsAssessment,
        score: float,
        specializations: list[TechSpecialization]
    ) -> str:
        """Generate human-readable justification for recommendation."""
        reasons = []

        if agent.category == "technical":
            if specializations:
                spec_names = [s.name for s in specializations[:3]]
                reasons.append(f"Technologies détectées: {', '.join(spec_names)}")

            # Stack match
            stack_matches = [s for s in profile.stack if any(
                kw.lower() in s.lower() for kw in agent.detection_keywords
            )]
            if stack_matches:
                reasons.append(f"Stack correspondante: {', '.join(stack_matches[:2])}")

        else:  # Transversal
            if agent.id == "security-checker":
                if assessment.sensitive_data:
                    reasons.append("Données sensibles détectées")
                if assessment.compliance_requirements:
                    reasons.append(f"Compliance requise: {', '.join(assessment.compliance_requirements)}")

            elif agent.id == "onboarding-guide":
                reasons.append(f"Niveau équipe: {assessment.experience_level}")
                if profile.complexity in ["high", "medium"]:
                    reasons.append(f"Complexité projet: {profile.complexity}")

            elif agent.id == "test-advisor":
                reasons.append("Tests identifiés comme besoin")

            elif agent.id == "perf-optimizer":
                reasons.append("Performance identifiée comme priorité")

        if not reasons:
            reasons.append(f"Score de correspondance: {score:.0%}")

        return "; ".join(reasons)

    def format_recommendations(
        self,
        recommendations: list[AgentRecommendation],
        show_capabilities: bool = True
    ) -> str:
        """Format recommendations for display."""

        # Separate by category
        technical = [r for r in recommendations if r.agent_type in self.technical_experts]
        transversal = [r for r in recommendations if r.agent_type in self.transversal_assistants]

        output = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    AGENTS IA RECOMMANDÉS                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

        if technical:
            output += "\n📦 EXPERTS TECHNIQUES\n"
            output += "─" * 60 + "\n"
            for i, rec in enumerate(technical, 1):
                output += self._format_single_recommendation(i, rec, show_capabilities)

        if transversal:
            output += "\n🔧 ASSISTANTS TRANSVERSAUX\n"
            output += "─" * 60 + "\n"
            start_idx = len(technical) + 1
            for i, rec in enumerate(transversal, start_idx):
                output += self._format_single_recommendation(i, rec, show_capabilities)

        output += "\n" + "═" * 60
        return output

    def _format_single_recommendation(
        self,
        index: int,
        rec: AgentRecommendation,
        show_capabilities: bool
    ) -> str:
        """Format a single recommendation."""
        icon = self.get_all_agents().get(rec.agent_type, {})
        if isinstance(icon, ExpertDefinition):
            icon = icon.icon
        else:
            icon = "🤖"

        priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}[rec.priority]

        output = f"""
{index}. {icon} {rec.name} {priority_icon} [{rec.priority.upper()}]
   {rec.description}

   📋 Justification: {rec.justification}
"""

        if show_capabilities and rec.capabilities:
            output += "\n   🛠️  Capacités:\n"
            for cap in rec.capabilities[:4]:
                output += f"      • {cap.name}: {cap.description}\n"

        return output


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def get_catalog_v2() -> CatalogV2:
    """Factory function to get the V2 catalog instance."""
    return CatalogV2()
