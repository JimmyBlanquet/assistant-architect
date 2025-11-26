"""
Documentation Analyzer - Extracts project intelligence from Markdown and HTML docs.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    from ..core.llm_abstraction import LLMProvider, get_provider
except ImportError:
    from core.llm_abstraction import LLMProvider, get_provider


@dataclass
class ProjectProfile:
    """Extracted profile of a project from its documentation."""
    name: str = ""
    description: str = ""
    stack: list[str] = field(default_factory=list)
    patterns: list[str] = field(default_factory=list)
    complexity: str = "medium"  # low, medium, high
    pain_points: list[str] = field(default_factory=list)
    conventions: dict[str, Any] = field(default_factory=dict)
    features: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    team_indicators: dict[str, Any] = field(default_factory=dict)
    raw_content: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "stack": self.stack,
            "patterns": self.patterns,
            "complexity": self.complexity,
            "pain_points": self.pain_points,
            "conventions": self.conventions,
            "features": self.features,
            "dependencies": self.dependencies,
            "team_indicators": self.team_indicators
        }


class MarkdownAnalyzer:
    """Analyzes Markdown documentation to extract project information."""

    def __init__(self, llm: LLMProvider | None = None):
        self.llm = llm

    def parse_file(self, file_path: Path) -> str:
        """Read and return content of a Markdown file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def extract_headers(self, content: str) -> list[dict]:
        """Extract all headers with their levels."""
        headers = []
        for match in re.finditer(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE):
            headers.append({
                "level": len(match.group(1)),
                "text": match.group(2).strip()
            })
        return headers

    def extract_code_blocks(self, content: str) -> list[dict]:
        """Extract code blocks with their languages."""
        blocks = []
        for match in re.finditer(r'```(\w*)\n(.*?)```', content, re.DOTALL):
            blocks.append({
                "language": match.group(1) or "unknown",
                "code": match.group(2).strip()
            })
        return blocks

    def extract_links(self, content: str) -> list[dict]:
        """Extract all links from the document."""
        links = []
        for match in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', content):
            links.append({
                "text": match.group(1),
                "url": match.group(2)
            })
        return links

    def detect_technologies(self, content: str, code_blocks: list[dict]) -> list[str]:
        """Detect technologies mentioned in the documentation."""
        tech_patterns = {
            # Languages
            "Python": r'\bpython\b|\.py\b|pip\s+install|requirements\.txt',
            "JavaScript": r'\bjavascript\b|\.js\b|npm\s+install|node_modules',
            "TypeScript": r'\btypescript\b|\.ts\b|tsconfig',
            "Java": r'\bjava\b|\.java\b|maven|gradle|pom\.xml',
            "Go": r'\bgolang\b|\.go\b|go\s+mod',
            "Rust": r'\brust\b|\.rs\b|cargo',
            # Frameworks
            "React": r'\breact\b|jsx|useState|useEffect',
            "Vue": r'\bvue\b|\.vue\b|vuex',
            "Angular": r'\bangular\b|ng\s+serve',
            "Spring": r'\bspring\b|@SpringBoot|@RestController',
            "Django": r'\bdjango\b|manage\.py',
            "FastAPI": r'\bfastapi\b|@app\.(get|post)',
            "Flask": r'\bflask\b|@app\.route',
            # Databases
            "PostgreSQL": r'\bpostgres|postgresql\b|psql',
            "MySQL": r'\bmysql\b',
            "MongoDB": r'\bmongodb\b|mongoose',
            "Redis": r'\bredis\b',
            # Tools
            "Docker": r'\bdocker\b|dockerfile|docker-compose',
            "Kubernetes": r'\bkubernetes\b|kubectl|k8s',
            "Git": r'\bgit\b|\.git',
            "CI/CD": r'\bci/cd\b|github\s+actions|gitlab\s+ci|jenkins',
            # AI/ML
            "Claude": r'\bclaude\b|anthropic',
            "OpenAI": r'\bopenai\b|gpt-',
            "LangChain": r'\blangchain\b',
        }

        detected = set()
        search_content = content.lower()

        # Also search in code blocks
        for block in code_blocks:
            search_content += "\n" + block["code"].lower()

        for tech, pattern in tech_patterns.items():
            if re.search(pattern, search_content, re.IGNORECASE):
                detected.add(tech)

        return sorted(list(detected))

    def detect_patterns(self, content: str) -> list[str]:
        """Detect architectural patterns mentioned."""
        pattern_keywords = {
            "microservices": r'\bmicroservices?\b',
            "monolith": r'\bmonolith\b',
            "event-driven": r'\bevent[- ]driven\b|event\s+sourcing',
            "REST API": r'\brest\s+api\b|restful',
            "GraphQL": r'\bgraphql\b',
            "serverless": r'\bserverless\b|lambda|cloud\s+functions',
            "MVC": r'\bmvc\b|model[- ]view[- ]controller',
            "clean architecture": r'\bclean\s+architecture\b|hexagonal',
            "DDD": r'\bdomain[- ]driven\b|ddd\b',
            "CQRS": r'\bcqrs\b|command\s+query',
            "pub/sub": r'\bpub/?sub\b|publish[- ]subscribe',
            "specification-driven": r'\bspec[- ]driven\b|specification',
        }

        detected = []
        for pattern, regex in pattern_keywords.items():
            if re.search(regex, content, re.IGNORECASE):
                detected.append(pattern)

        return detected

    def estimate_complexity(self, content: str, headers: list, code_blocks: list, tech: list) -> str:
        """Estimate project complexity based on documentation."""
        score = 0

        # Number of headers indicates documentation depth
        if len(headers) > 20:
            score += 2
        elif len(headers) > 10:
            score += 1

        # Number of code blocks
        if len(code_blocks) > 15:
            score += 2
        elif len(code_blocks) > 5:
            score += 1

        # Technology stack size
        if len(tech) > 8:
            score += 2
        elif len(tech) > 4:
            score += 1

        # Content length
        if len(content) > 20000:
            score += 2
        elif len(content) > 5000:
            score += 1

        if score >= 5:
            return "high"
        elif score >= 2:
            return "medium"
        return "low"


class HTMLAnalyzer:
    """Analyzes HTML documentation."""

    def parse_file(self, file_path: Path) -> str:
        """Read HTML and extract text content."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Simple HTML to text conversion
        # Remove scripts and styles
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)

        # Replace common tags with text equivalents
        content = re.sub(r'<br\s*/?>', '\n', content)
        content = re.sub(r'<p[^>]*>', '\n', content)
        content = re.sub(r'</p>', '\n', content)
        content = re.sub(r'<h([1-6])[^>]*>', lambda m: '\n' + '#' * int(m.group(1)) + ' ', content)
        content = re.sub(r'</h[1-6]>', '\n', content)
        content = re.sub(r'<li[^>]*>', '- ', content)

        # Remove remaining tags
        content = re.sub(r'<[^>]+>', '', content)

        # Decode HTML entities
        content = content.replace('&nbsp;', ' ')
        content = content.replace('&lt;', '<')
        content = content.replace('&gt;', '>')
        content = content.replace('&amp;', '&')
        content = content.replace('&quot;', '"')

        return content.strip()


class DocumentationAnalyzer:
    """Main analyzer that combines Markdown and HTML analysis with LLM enrichment."""

    def __init__(self, llm: LLMProvider | None = None):
        self.llm = llm or get_provider("claude")
        self.md_analyzer = MarkdownAnalyzer(llm)
        self.html_analyzer = HTMLAnalyzer()

    def analyze_directory(self, doc_path: Path) -> ProjectProfile:
        """Analyze all documentation files in a directory."""
        all_content = []
        all_code_blocks = []
        all_headers = []

        # Find all documentation files
        doc_files = list(doc_path.glob("**/*.md")) + list(doc_path.glob("**/*.html"))

        for file_path in doc_files:
            if file_path.suffix == '.md':
                content = self.md_analyzer.parse_file(file_path)
                headers = self.md_analyzer.extract_headers(content)
                code_blocks = self.md_analyzer.extract_code_blocks(content)
            else:
                content = self.html_analyzer.parse_file(file_path)
                headers = self.md_analyzer.extract_headers(content)  # Works on converted content
                code_blocks = self.md_analyzer.extract_code_blocks(content)

            all_content.append(f"# File: {file_path.name}\n\n{content}")
            all_headers.extend(headers)
            all_code_blocks.extend(code_blocks)

        combined_content = "\n\n---\n\n".join(all_content)

        # Extract information using pattern matching
        technologies = self.md_analyzer.detect_technologies(combined_content, all_code_blocks)
        patterns = self.md_analyzer.detect_patterns(combined_content)
        complexity = self.md_analyzer.estimate_complexity(
            combined_content, all_headers, all_code_blocks, technologies
        )

        profile = ProjectProfile(
            stack=technologies,
            patterns=patterns,
            complexity=complexity,
            raw_content=combined_content
        )

        # Enrich with LLM analysis if available
        if self.llm:
            profile = self._enrich_with_llm(profile, combined_content)

        return profile

    def analyze_content(self, content: str, source_type: str = "markdown") -> ProjectProfile:
        """Analyze documentation content directly."""
        if source_type == "html":
            # Convert HTML to text-like format
            content = self.html_analyzer.parse_file(Path("/dev/null"))  # Not used, just for method
            # Actually parse the content string
            content = re.sub(r'<[^>]+>', '', content)

        headers = self.md_analyzer.extract_headers(content)
        code_blocks = self.md_analyzer.extract_code_blocks(content)
        technologies = self.md_analyzer.detect_technologies(content, code_blocks)
        patterns = self.md_analyzer.detect_patterns(content)
        complexity = self.md_analyzer.estimate_complexity(content, headers, code_blocks, technologies)

        profile = ProjectProfile(
            stack=technologies,
            patterns=patterns,
            complexity=complexity,
            raw_content=content
        )

        if self.llm:
            profile = self._enrich_with_llm(profile, content)

        return profile

    def _enrich_with_llm(self, profile: ProjectProfile, content: str) -> ProjectProfile:
        """Use LLM to extract additional insights."""
        # Truncate content if too long
        max_content_length = 15000
        truncated_content = content[:max_content_length]
        if len(content) > max_content_length:
            truncated_content += "\n\n[... content truncated ...]"

        schema = {
            "name": "string - project name",
            "description": "string - brief project description (1-2 sentences)",
            "features": ["list of main features/capabilities"],
            "pain_points": ["potential difficulties/challenges for developers"],
            "conventions": {
                "code_style": "detected code style if any",
                "structure": "project structure pattern"
            },
            "team_indicators": {
                "size_estimate": "small/medium/large",
                "experience_level": "beginner/intermediate/advanced"
            }
        }

        prompt = f"""Analyze this project documentation and extract key information.

Documentation:
{truncated_content}

Already detected:
- Technologies: {profile.stack}
- Patterns: {profile.patterns}
- Complexity: {profile.complexity}

Extract additional insights and return as JSON."""

        try:
            result = self.llm.analyze(truncated_content, schema)

            profile.name = result.get("name", profile.name)
            profile.description = result.get("description", profile.description)
            profile.features = result.get("features", profile.features)
            profile.pain_points = result.get("pain_points", profile.pain_points)
            profile.conventions = result.get("conventions", profile.conventions)
            profile.team_indicators = result.get("team_indicators", profile.team_indicators)

        except Exception as e:
            # LLM enrichment failed, continue with basic analysis
            print(f"Warning: LLM enrichment failed: {e}")

        return profile
