"""
Requirement Analyzer & Spec File Generator
============================================
Reads requirements from a text/CSV file or interactive input,
analyzes them (categorizes, prioritizes, detects gaps, estimates complexity),
and generates a structured specification document (Markdown + JSON).

Usage:
  python spec_generator.py                     # Interactive mode
  python spec_generator.py requirements.txt    # From file
  python spec_generator.py requirements.csv    # From CSV
"""

import os
import sys
import json
import csv
import re
import textwrap
from datetime import datetime
from collections import Counter, defaultdict


# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

CATEGORIES = {
    "functional":     ["shall", "must", "should", "allow", "enable", "support", "provide",
                       "display", "show", "create", "update", "delete", "search", "filter",
                       "login", "register", "submit", "upload", "download", "export", "import",
                       "send", "receive", "process", "calculate", "validate", "verify", "generate"],
    "non-functional": ["performance", "scalable", "secure", "security", "availability",
                       "reliability", "uptime", "latency", "response time", "load",
                       "throughput", "concurrent", "encrypt", "comply", "compliance",
                       "accessible", "accessibility", "backup", "recovery", "audit"],
    "ui/ux":          ["interface", "layout", "design", "responsive", "mobile", "theme",
                       "color", "font", "button", "menu", "navigation", "modal", "tooltip",
                       "animation", "drag", "drop", "click", "hover", "scroll", "popup",
                       "dashboard", "widget", "icon", "image", "css", "style"],
    "data":           ["database", "store", "storage", "table", "field", "column", "record",
                       "query", "schema", "migration", "backup", "cache", "index",
                       "relationship", "foreign key", "primary key", "normalize", "api",
                       "endpoint", "json", "xml", "csv", "payload", "request", "response"],
    "integration":    ["integrate", "third-party", "external", "webhook", "api", "rest",
                       "soap", "oauth", "sso", "sync", "connect", "plugin", "sdk",
                       "microservice", "message queue", "kafka", "rabbitmq", "notification"],
    "testing":        ["test", "qa", "automation", "selenium", "cypress", "junit", "pytest",
                       "coverage", "regression", "smoke", "sanity", "acceptance", "uat",
                       "bug", "defect", "report", "scenario", "test case", "assertion"],
}

PRIORITY_KEYWORDS = {
    "critical": ["must", "critical", "mandatory", "essential", "required", "blocker",
                 "immediately", "urgent", "security", "compliance", "legal"],
    "high":     ["should", "important", "high priority", "needed", "significant",
                 "expected", "key", "primary", "core"],
    "medium":   ["could", "nice to have", "moderate", "standard", "typical",
                 "default", "normal", "regular"],
    "low":      ["may", "optional", "future", "later", "consider", "if possible",
                 "stretch", "bonus", "wish", "enhancement"],
}

COMPLEXITY_SIGNALS = {
    "high":   ["integrate", "migration", "real-time", "concurrent", "distributed",
               "machine learning", "ai", "algorithm", "encrypt", "multi-tenant",
               "microservice", "workflow", "orchestrat", "batch processing",
               "third-party", "legacy", "complex", "advanced"],
    "medium": ["api", "database", "authentication", "authorization", "report",
               "dashboard", "notification", "search", "filter", "export",
               "import", "validation", "role-based", "schedule", "queue"],
    "low":    ["display", "show", "list", "view", "page", "label", "text",
               "button", "link", "color", "font", "static", "simple", "basic"],
}

AMBIGUITY_PATTERNS = [
    (r"\betc\.?\b", "Vague listing with 'etc.' — specify all items explicitly"),
    (r"\bsome\b", "'Some' is ambiguous — quantify exactly"),
    (r"\bvarious\b", "'Various' is vague — enumerate the items"),
    (r"\bappropriate\b", "'Appropriate' is subjective — define criteria"),
    (r"\buser[- ]friendly\b", "'User-friendly' is subjective — define measurable UX criteria"),
    (r"\bfast\b", "'Fast' is unmeasurable — specify response time in ms/seconds"),
    (r"\bquickly\b", "'Quickly' is unmeasurable — specify time threshold"),
    (r"\befficient\b", "'Efficient' is vague — define metrics (CPU, memory, time)"),
    (r"\bflexible\b", "'Flexible' is subjective — specify what can be configured"),
    (r"\brobust\b", "'Robust' is vague — define error-handling expectations"),
    (r"\bintuitive\b", "'Intuitive' is subjective — define UX acceptance criteria"),
    (r"\bseamless\b", "'Seamless' is vague — define integration points and flows"),
    (r"\bas needed\b", "'As needed' is ambiguous — define triggers/conditions"),
    (r"\bsimilar to\b", "'Similar to' is unclear — specify exact behavior"),
    (r"\bmay\s+or\s+may\s+not\b", "Contradictory requirement — clarify intent"),
]

MISSING_SECTION_CHECKS = [
    ("error handling", ["error", "exception", "fail", "invalid", "retry", "fallback"]),
    ("authentication/authorization", ["login", "auth", "role", "permission", "access", "sso", "oauth"]),
    ("data validation", ["validate", "validation", "input check", "sanitize", "format"]),
    ("logging/monitoring", ["log", "monitor", "audit", "track", "alert", "metric"]),
    ("performance requirements", ["performance", "latency", "throughput", "load", "response time"]),
    ("security requirements", ["security", "encrypt", "ssl", "tls", "xss", "injection", "csrf"]),
    ("backup/recovery", ["backup", "recovery", "disaster", "restore", "failover"]),
    ("accessibility", ["accessible", "accessibility", "wcag", "aria", "screen reader"]),
]


# ═══════════════════════════════════════════════════════════════
# REQUIREMENT CLASS
# ═══════════════════════════════════════════════════════════════

class Requirement:
    """Represents a single parsed and analyzed requirement."""

    _counter = 0

    def __init__(self, text, source="user_input", raw_priority=None, raw_category=None):
        Requirement._counter += 1
        self.id = f"REQ-{Requirement._counter:04d}"
        self.text = text.strip()
        self.source = source
        self.category = raw_category or self._detect_category()
        self.priority = raw_priority or self._detect_priority()
        self.complexity = self._estimate_complexity()
        self.ambiguities = self._find_ambiguities()
        self.keywords = self._extract_keywords()
        self.dependencies = []
        self.acceptance_criteria = self._generate_acceptance_criteria()
        self.test_scenarios = self._generate_test_scenarios()

    def _detect_category(self):
        lower = self.text.lower()
        scores = {}
        for cat, words in CATEGORIES.items():
            scores[cat] = sum(1 for w in words if w in lower)
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else "functional"

    def _detect_priority(self):
        lower = self.text.lower()
        for pri, words in PRIORITY_KEYWORDS.items():
            if any(w in lower for w in words):
                return pri
        return "medium"

    def _estimate_complexity(self):
        lower = self.text.lower()
        for level, signals in COMPLEXITY_SIGNALS.items():
            if any(s in lower for s in signals):
                return level
        return "medium"

    def _find_ambiguities(self):
        issues = []
        for pattern, message in AMBIGUITY_PATTERNS:
            if re.search(pattern, self.text, re.IGNORECASE):
                issues.append(message)
        if len(self.text.split()) < 5:
            issues.append("Requirement is too brief — add context and specifics")
        if len(self.text.split()) > 80:
            issues.append("Requirement is very long — consider splitting into sub-requirements")
        if "?" in self.text:
            issues.append("Contains a question — requirements should be declarative")
        return issues

    def _extract_keywords(self):
        stopwords = {"the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
                     "have", "has", "had", "do", "does", "did", "will", "would", "shall",
                     "should", "may", "might", "must", "can", "could", "to", "of", "in",
                     "for", "on", "with", "at", "by", "from", "as", "into", "through",
                     "and", "but", "or", "not", "no", "nor", "it", "its", "this", "that",
                     "these", "those", "all", "each", "every", "any", "both", "such", "than"}
        words = re.findall(r'\b[a-zA-Z]{3,}\b', self.text.lower())
        return [w for w in words if w not in stopwords][:10]

    def _generate_acceptance_criteria(self):
        criteria = []
        lower = self.text.lower()

        if any(w in lower for w in ["login", "auth", "register", "sign"]):
            criteria.append("GIVEN a valid user, WHEN credentials are submitted, THEN access is granted")
            criteria.append("GIVEN invalid credentials, WHEN login is attempted, THEN an error message is shown")
        elif any(w in lower for w in ["create", "add", "insert", "new"]):
            criteria.append("GIVEN valid input data, WHEN the create action is performed, THEN a new record is saved")
            criteria.append("GIVEN invalid input, WHEN the create action is performed, THEN validation errors are displayed")
        elif any(w in lower for w in ["update", "edit", "modify"]):
            criteria.append("GIVEN an existing record, WHEN updated fields are submitted, THEN changes are persisted")
            criteria.append("GIVEN invalid updates, WHEN submitted, THEN the original data remains unchanged")
        elif any(w in lower for w in ["delete", "remove"]):
            criteria.append("GIVEN an existing record, WHEN deletion is confirmed, THEN the record is removed")
            criteria.append("GIVEN a protected record, WHEN deletion is attempted, THEN it is blocked with a message")
        elif any(w in lower for w in ["search", "filter", "find"]):
            criteria.append("GIVEN search criteria, WHEN submitted, THEN matching results are returned")
            criteria.append("GIVEN no matching data, WHEN searched, THEN a 'no results' message is shown")
        elif any(w in lower for w in ["display", "show", "view", "list"]):
            criteria.append("GIVEN available data, WHEN the page loads, THEN the information is displayed correctly")
        elif any(w in lower for w in ["export", "download"]):
            criteria.append("GIVEN data to export, WHEN export is triggered, THEN a file is downloaded in the correct format")
        elif any(w in lower for w in ["upload", "import"]):
            criteria.append("GIVEN a valid file, WHEN uploaded, THEN data is imported and confirmed")
            criteria.append("GIVEN an invalid file, WHEN uploaded, THEN an error message describes the issue")
        else:
            criteria.append("GIVEN the precondition is met, WHEN the action is performed, THEN the expected result occurs")

        return criteria

    def _generate_test_scenarios(self):
        scenarios = []
        lower = self.text.lower()

        scenarios.append(f"TC-{self.id}: Verify positive flow — {self.text[:60]}...")
        scenarios.append(f"TC-{self.id}-NEG: Verify negative/error handling")

        if any(w in lower for w in ["input", "form", "field", "enter"]):
            scenarios.append(f"TC-{self.id}-BND: Boundary value testing for input fields")
            scenarios.append(f"TC-{self.id}-INV: Invalid input validation")
        if any(w in lower for w in ["role", "permission", "access", "admin"]):
            scenarios.append(f"TC-{self.id}-AUTH: Authorization check for different user roles")
        if any(w in lower for w in ["concurrent", "load", "multiple"]):
            scenarios.append(f"TC-{self.id}-PERF: Concurrent usage / load test")
        if any(w in lower for w in ["api", "endpoint", "service"]):
            scenarios.append(f"TC-{self.id}-API: API contract and response validation")

        return scenarios

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "category": self.category,
            "priority": self.priority,
            "complexity": self.complexity,
            "source": self.source,
            "keywords": self.keywords,
            "ambiguities": self.ambiguities,
            "acceptance_criteria": self.acceptance_criteria,
            "test_scenarios": self.test_scenarios,
            "dependencies": self.dependencies,
        }


# ═══════════════════════════════════════════════════════════════
# ANALYZER
# ═══════════════════════════════════════════════════════════════

class RequirementAnalyzer:
    """Analyzes a collection of requirements and produces insights."""

    def __init__(self, project_name="Project"):
        self.project_name = project_name
        self.requirements = []
        self.analysis = {}

    def add(self, text, source="user_input", priority=None, category=None):
        if text.strip():
            req = Requirement(text, source, priority, category)
            self.requirements.append(req)
            return req
        return None

    def load_from_text(self, content, source="file"):
        lines = content.strip().split("\n")
        count = 0
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("//"):
                continue
            # Handle numbered lines: "1. requirement" or "1) requirement"
            line = re.sub(r'^\d+[\.\)]\s*', '', line)
            # Handle bullet lines
            line = re.sub(r'^[-•*]\s*', '', line)
            if len(line) > 5:
                self.add(line, source)
                count += 1
        return count

    def load_from_csv(self, filepath):
        count = 0
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            headers_lower = {h.lower().strip(): h for h in reader.fieldnames} if reader.fieldnames else {}

            # Try to find the right column names
            text_col = None
            for candidate in ["requirement", "description", "text", "detail", "story", "feature"]:
                if candidate in headers_lower:
                    text_col = headers_lower[candidate]
                    break
            if not text_col and reader.fieldnames:
                text_col = reader.fieldnames[0]  # fallback to first column

            pri_col = None
            for candidate in ["priority", "severity", "importance"]:
                if candidate in headers_lower:
                    pri_col = headers_lower[candidate]
                    break

            cat_col = None
            for candidate in ["category", "type", "module", "area"]:
                if candidate in headers_lower:
                    cat_col = headers_lower[candidate]
                    break

            for row in reader:
                text = row.get(text_col, "").strip()
                pri = row.get(pri_col, "").strip().lower() if pri_col else None
                cat = row.get(cat_col, "").strip().lower() if cat_col else None
                if text and len(text) > 5:
                    self.add(text, os.path.basename(filepath), pri if pri else None, cat if cat else None)
                    count += 1
        return count

    def analyze(self):
        if not self.requirements:
            return {}

        all_text = " ".join(r.text for r in self.requirements).lower()

        # Category distribution
        cat_dist = Counter(r.category for r in self.requirements)

        # Priority distribution
        pri_dist = Counter(r.priority for r in self.requirements)

        # Complexity distribution
        comp_dist = Counter(r.complexity for r in self.requirements)

        # All ambiguities
        ambiguous_reqs = [(r.id, r.text[:80], r.ambiguities) for r in self.requirements if r.ambiguities]

        # Missing areas
        missing = []
        for area, keywords in MISSING_SECTION_CHECKS:
            if not any(kw in all_text for kw in keywords):
                missing.append(area)

        # Keyword frequency
        all_kw = []
        for r in self.requirements:
            all_kw.extend(r.keywords)
        top_keywords = Counter(all_kw).most_common(20)

        # Dependency detection (simple: if keywords overlap significantly)
        for i, r1 in enumerate(self.requirements):
            for j, r2 in enumerate(self.requirements):
                if i != j:
                    shared = set(r1.keywords) & set(r2.keywords)
                    if len(shared) >= 3:
                        if r2.id not in r1.dependencies:
                            r1.dependencies.append(r2.id)

        # Effort estimation
        complexity_points = {"low": 1, "medium": 3, "high": 8}
        total_points = sum(complexity_points.get(r.complexity, 3) for r in self.requirements)

        self.analysis = {
            "total_requirements": len(self.requirements),
            "category_distribution": dict(cat_dist),
            "priority_distribution": dict(pri_dist),
            "complexity_distribution": dict(comp_dist),
            "ambiguous_requirements": len(ambiguous_reqs),
            "ambiguity_details": ambiguous_reqs,
            "missing_areas": missing,
            "top_keywords": top_keywords,
            "estimated_story_points": total_points,
            "quality_score": self._quality_score(ambiguous_reqs, missing),
        }
        return self.analysis

    def _quality_score(self, ambiguous, missing):
        total = len(self.requirements)
        if total == 0:
            return 0
        ambiguity_penalty = len(ambiguous) / total * 40
        missing_penalty = len(missing) / len(MISSING_SECTION_CHECKS) * 30
        brevity_penalty = sum(1 for r in self.requirements if len(r.text.split()) < 8) / total * 30
        score = max(0, 100 - ambiguity_penalty - missing_penalty - brevity_penalty)
        return round(score, 1)


# ═══════════════════════════════════════════════════════════════
# SPEC FILE GENERATORS
# ═══════════════════════════════════════════════════════════════

def generate_markdown_spec(analyzer, output_path):
    """Generate a professional Markdown specification document."""
    a = analyzer.analysis
    reqs = analyzer.requirements
    now = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    pri_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
    comp_emoji = {"high": "🔺", "medium": "🔹", "low": "🔻"}

    lines = []
    w = lines.append

    w(f"# 📋 Specification Document — {analyzer.project_name}")
    w(f"\n> Auto-generated on **{now}** by Requirement Analyzer v1.0")
    w(f"> Source requirements: **{a['total_requirements']}** | Quality Score: **{a['quality_score']}/100**")
    w("")

    # ─── TABLE OF CONTENTS ───
    w("---\n## 📑 Table of Contents\n")
    w("1. [Executive Summary](#executive-summary)")
    w("2. [Requirements Overview](#requirements-overview)")
    w("3. [Detailed Requirements](#detailed-requirements)")
    w("4. [Analysis & Insights](#analysis--insights)")
    w("5. [Gap Analysis](#gap-analysis)")
    w("6. [Acceptance Criteria](#acceptance-criteria)")
    w("7. [Test Scenarios](#test-scenarios)")
    w("8. [Dependency Map](#dependency-map)")
    w("9. [Effort Estimation](#effort-estimation)")
    w("10. [Recommendations](#recommendations)")
    w("")

    # ─── EXECUTIVE SUMMARY ───
    w("---\n## 1. Executive Summary\n")
    w(f"| Metric | Value |")
    w(f"|--------|-------|")
    w(f"| Total Requirements | {a['total_requirements']} |")
    w(f"| Quality Score | {a['quality_score']}/100 |")
    w(f"| Estimated Story Points | {a['estimated_story_points']} |")
    w(f"| Ambiguous Requirements | {a['ambiguous_requirements']} |")
    w(f"| Missing Coverage Areas | {len(a['missing_areas'])} |")
    w("")

    w("### Priority Breakdown\n")
    w("| Priority | Count | Percentage |")
    w("|----------|-------|------------|")
    for pri in ["critical", "high", "medium", "low"]:
        cnt = a["priority_distribution"].get(pri, 0)
        pct = round(cnt / a["total_requirements"] * 100, 1) if a["total_requirements"] else 0
        w(f"| {pri_emoji.get(pri, '')} {pri.title()} | {cnt} | {pct}% |")
    w("")

    w("### Category Breakdown\n")
    w("| Category | Count |")
    w("|----------|-------|")
    for cat, cnt in sorted(a["category_distribution"].items(), key=lambda x: -x[1]):
        w(f"| {cat.title()} | {cnt} |")
    w("")

    # ─── REQUIREMENTS OVERVIEW ───
    w("---\n## 2. Requirements Overview\n")
    w("| ID | Requirement | Category | Priority | Complexity |")
    w("|----|------------|----------|----------|------------|")
    for r in reqs:
        short = r.text[:100] + ("..." if len(r.text) > 100 else "")
        w(f"| {r.id} | {short} | {r.category} | {pri_emoji.get(r.priority, '')} {r.priority} | {comp_emoji.get(r.complexity, '')} {r.complexity} |")
    w("")

    # ─── DETAILED REQUIREMENTS ───
    w("---\n## 3. Detailed Requirements\n")
    for r in reqs:
        w(f"### {r.id}: {r.text[:80]}{'...' if len(r.text) > 80 else ''}\n")
        w(f"- **Full Text:** {r.text}")
        w(f"- **Category:** {r.category}")
        w(f"- **Priority:** {pri_emoji.get(r.priority, '')} {r.priority}")
        w(f"- **Complexity:** {comp_emoji.get(r.complexity, '')} {r.complexity}")
        w(f"- **Keywords:** {', '.join(r.keywords)}")
        if r.ambiguities:
            w(f"- **⚠️ Ambiguities:**")
            for amb in r.ambiguities:
                w(f"  - {amb}")
        if r.dependencies:
            w(f"- **Dependencies:** {', '.join(r.dependencies)}")
        w("")

    # ─── ANALYSIS ───
    w("---\n## 4. Analysis & Insights\n")
    w("### Top Keywords\n")
    w("| Keyword | Frequency |")
    w("|---------|-----------|")
    for kw, freq in a["top_keywords"]:
        w(f"| {kw} | {freq} |")
    w("")

    if a["ambiguity_details"]:
        w("### ⚠️ Ambiguous Requirements\n")
        for req_id, text, issues in a["ambiguity_details"]:
            w(f"**{req_id}:** {text}...")
            for issue in issues:
                w(f"  - ⚠️ {issue}")
            w("")

    # ─── GAP ANALYSIS ───
    w("---\n## 5. Gap Analysis\n")
    if a["missing_areas"]:
        w("The following areas are **not covered** by the current requirements:\n")
        for area in a["missing_areas"]:
            w(f"- ❌ **{area.title()}** — Consider adding requirements for this area")
    else:
        w("✅ All major requirement areas are covered.")
    w("")

    # ─── ACCEPTANCE CRITERIA ───
    w("---\n## 6. Acceptance Criteria\n")
    for r in reqs:
        w(f"### {r.id}\n")
        for ac in r.acceptance_criteria:
            w(f"- {ac}")
        w("")

    # ─── TEST SCENARIOS ───
    w("---\n## 7. Test Scenarios\n")
    w("| Scenario ID | Description |")
    w("|-------------|-------------|")
    for r in reqs:
        for ts in r.test_scenarios:
            w(f"| {r.id} | {ts} |")
    w("")

    # ─── DEPENDENCY MAP ───
    w("---\n## 8. Dependency Map\n")
    has_deps = [r for r in reqs if r.dependencies]
    if has_deps:
        w("| Requirement | Depends On |")
        w("|-------------|------------|")
        for r in has_deps:
            w(f"| {r.id} | {', '.join(r.dependencies)} |")
    else:
        w("No inter-requirement dependencies detected.")
    w("")

    # ─── EFFORT ESTIMATION ───
    w("---\n## 9. Effort Estimation\n")
    w("| Complexity | Count | Points Each | Subtotal |")
    w("|------------|-------|-------------|----------|")
    cp = {"low": 1, "medium": 3, "high": 8}
    for level in ["low", "medium", "high"]:
        cnt = a["complexity_distribution"].get(level, 0)
        w(f"| {comp_emoji.get(level, '')} {level.title()} | {cnt} | {cp[level]} | {cnt * cp[level]} |")
    w(f"| **Total** | **{a['total_requirements']}** | | **{a['estimated_story_points']}** |")
    w("")

    # ─── RECOMMENDATIONS ───
    w("---\n## 10. Recommendations\n")
    recs = []
    if a["ambiguous_requirements"] > 0:
        recs.append(f"🔍 **Clarify ambiguous requirements** — {a['ambiguous_requirements']} requirement(s) contain vague language. Review and add specific, measurable criteria.")
    if a["missing_areas"]:
        recs.append(f"📋 **Address coverage gaps** — {len(a['missing_areas'])} area(s) are missing: {', '.join(a['missing_areas'])}. Add requirements for each.")
    if a["quality_score"] < 60:
        recs.append("⚠️ **Low quality score** — Many requirements need refinement. Schedule a requirements review workshop.")
    if a["priority_distribution"].get("critical", 0) > a["total_requirements"] * 0.5:
        recs.append("🔴 **Too many critical items** — Reprioritize to ensure realistic delivery.")
    short_reqs = sum(1 for r in reqs if len(r.text.split()) < 8)
    if short_reqs > 0:
        recs.append(f"📝 **Expand brief requirements** — {short_reqs} requirement(s) are too short. Add context, actors, and expected outcomes.")
    recs.append("✅ **Next steps:** Review this spec with stakeholders, assign owners, create user stories, and plan sprints.")

    for rec in recs:
        w(f"- {rec}")
    w("")

    w("---\n*Generated by Requirement Analyzer & Spec Generator*")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))

    return output_path


def generate_json_spec(analyzer, output_path):
    """Generate a JSON specification for programmatic consumption."""
    spec = {
        "meta": {
            "project": analyzer.project_name,
            "generated_at": datetime.now().isoformat(),
            "generator": "Requirement Analyzer v1.0",
            "total_requirements": len(analyzer.requirements),
            "quality_score": analyzer.analysis.get("quality_score", 0),
        },
        "analysis": {
            "category_distribution": analyzer.analysis.get("category_distribution", {}),
            "priority_distribution": analyzer.analysis.get("priority_distribution", {}),
            "complexity_distribution": analyzer.analysis.get("complexity_distribution", {}),
            "estimated_story_points": analyzer.analysis.get("estimated_story_points", 0),
            "missing_areas": analyzer.analysis.get("missing_areas", []),
            "top_keywords": analyzer.analysis.get("top_keywords", []),
        },
        "requirements": [r.to_dict() for r in analyzer.requirements],
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)

    return output_path


# ═══════════════════════════════════════════════════════════════
# INTERACTIVE MODE
# ═══════════════════════════════════════════════════════════════

def interactive_mode():
    """Run the tool in interactive mode with user prompts."""
    print("\n" + "=" * 60)
    print("  📋 REQUIREMENT ANALYZER & SPEC GENERATOR")
    print("=" * 60)

    project = input("\n📁 Project name (default: 'MyProject'): ").strip() or "MyProject"
    analyzer = RequirementAnalyzer(project)

    print(f"\n📝 Enter requirements one per line.")
    print(f"   • Type a blank line when done")
    print(f"   • Lines starting with # are ignored (comments)")
    print(f"   • Numbered items (1. ...) and bullets (- ...) are auto-cleaned\n")

    while True:
        try:
            line = input("  ➤ ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not line:
            if analyzer.requirements:
                break
            print("  ⚠️  Enter at least one requirement.")
            continue
        if line.startswith("#"):
            continue
        line = re.sub(r'^\d+[\.\)]\s*', '', line)
        line = re.sub(r'^[-•*]\s*', '', line)
        req = analyzer.add(line)
        if req:
            print(f"     ✅ {req.id} [{req.category}/{req.priority}]")

    return analyzer


def run(input_path=None):
    """Main entry point."""
    if input_path:
        ext = os.path.splitext(input_path)[1].lower()
        base_dir = os.path.dirname(os.path.abspath(input_path))
        base_name = os.path.splitext(os.path.basename(input_path))[0]

        project = base_name.replace("_", " ").replace("-", " ").title()
        analyzer = RequirementAnalyzer(project)

        print(f"\n📂 Loading requirements from: {input_path}")

        if ext == ".csv":
            count = analyzer.load_from_csv(input_path)
        else:
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
            count = analyzer.load_from_text(content, os.path.basename(input_path))

        print(f"   ✅ Loaded {count} requirements")
    else:
        analyzer = interactive_mode()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        base_name = analyzer.project_name.lower().replace(" ", "_")

    if not analyzer.requirements:
        print("\n❌ No requirements to analyze. Exiting.")
        return

    # Analyze
    print("\n🔍 Analyzing requirements...")
    analysis = analyzer.analyze()

    # Print summary
    print(f"\n{'─' * 50}")
    print(f"  📊 ANALYSIS SUMMARY")
    print(f"{'─' * 50}")
    print(f"  Total Requirements : {analysis['total_requirements']}")
    print(f"  Quality Score      : {analysis['quality_score']}/100")
    print(f"  Story Points       : {analysis['estimated_story_points']}")
    print(f"  Ambiguous Items    : {analysis['ambiguous_requirements']}")
    print(f"  Missing Areas      : {len(analysis['missing_areas'])}")
    if analysis['missing_areas']:
        for area in analysis['missing_areas']:
            print(f"    ❌ {area}")
    print(f"\n  Priority: ", end="")
    for pri in ["critical", "high", "medium", "low"]:
        cnt = analysis["priority_distribution"].get(pri, 0)
        if cnt:
            print(f"{pri}={cnt}  ", end="")
    print(f"\n  Category: ", end="")
    for cat, cnt in sorted(analysis["category_distribution"].items(), key=lambda x: -x[1]):
        print(f"{cat}={cnt}  ", end="")
    print()

    # Generate outputs
    md_path = os.path.join(base_dir, f"{base_name}_spec.md")
    json_path = os.path.join(base_dir, f"{base_name}_spec.json")

    print(f"\n📄 Generating specification files...")
    generate_markdown_spec(analyzer, md_path)
    print(f"   ✅ Markdown: {md_path}")
    generate_json_spec(analyzer, json_path)
    print(f"   ✅ JSON:     {json_path}")

    print(f"\n{'═' * 50}")
    print(f"  ✅ DONE! Open the .md file for the full specification.")
    print(f"{'═' * 50}\n")

    return md_path, json_path


# ═══════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        if not os.path.exists(filepath):
            print(f"❌ File not found: {filepath}")
            sys.exit(1)
        run(filepath)
    else:
        run()
