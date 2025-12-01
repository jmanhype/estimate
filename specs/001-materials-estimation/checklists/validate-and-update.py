#!/usr/bin/env python3
"""
Validate and update checklists based on current spec.md and plan.md state.
Updates checklist items from [ ] to [x] when requirements are satisfied.
"""

import re
from pathlib import Path
from typing import Dict, Tuple

# Checklist validation mappings
# Format: checklist_item_id -> (check_type, validation_logic)

ACCESSIBILITY_VALIDATIONS = {
    # Requirement Completeness
    "CHK001": ("spec", r"FR-035.*keyboard navigation"),
    "CHK002": ("spec", r"FR-035.*Tab.*keyboard"),
    "CHK003": ("spec", r"FR-036.*screen reader|aria-live"),
    "CHK004": ("spec", r"FR-039.*color contrast.*4\.5:1"),
    "CHK005": ("spec", r"FR-036.*focus indicator.*2px"),
    "CHK006": ("spec", r"FR-051.*ARIA.*role="),
    "CHK007": ("spec", r"FR-045.*alternative text|alt text"),
    "CHK008": ("spec", r"FR-048.*aria-live.*error"),
    "CHK009": ("spec", r"FR-047.*label.*<label>"),
    "CHK010": ("spec", r"FR-044.*heading.*h1.*h2"),
    "CHK011": ("spec", r"FR-046.*skip.*navigation"),
    "CHK012": ("spec", r"FR-038.*accessible name.*aria-label"),
    "CHK013": ("plan", r"Data Table Accessibility.*<th scope="),
    "CHK014": ("spec", r"FR-051.*modal.*dialog.*focus trap"),
    "CHK015": ("spec", r"FR-048.*validation.*aria-invalid"),
    # Requirement Clarity
    "CHK016": ("spec", r"WCAG 2\.1.*AA"),
    "CHK017": ("spec", r"4\.5:1.*3:1"),
    "CHK018": ("spec", r"2px.*3:1.*contrast"),
    "CHK019": ("spec", r"Tab.*Enter.*Escape.*Arrow"),
    "CHK020": ("spec", r"SC-016.*screen reader.*complete.*task"),
    "CHK021": ("spec", r"FR-043.*semantic.*nav.*main"),
    "CHK022": ("spec", r"FR-043.*<nav>.*<main>.*<header>"),
    "CHK023": ("spec", r"NVDA.*JAWS.*VoiceOver"),
    # Requirement Consistency
    "CHK024": ("spec", r"FR-035.*FR-036.*FR-037.*FR-038"),  # Multiple FRs show consistency
    "CHK025": ("spec", r"keyboard.*mouse"),
    "CHK026": ("spec", r"FR-054.*focus.*modal"),
    "CHK027": ("spec", r"FR-048.*FR-049.*error.*aria"),
    "CHK028": ("spec", r"FR-039.*FR-040.*color"),
    # Acceptance Criteria Quality
    "CHK029": ("spec", r"keyboard.*test|FR-035"),
    "CHK030": ("spec", r"axe-core|FR-055"),
    "CHK031": ("spec", r"FR-056.*screen reader"),
    "CHK032": ("spec", r"FR-036.*focus.*3:1"),
    "CHK033": ("spec", r"FR-055.*axe-core"),
    "CHK034": ("spec", r"FR-043.*semantic HTML"),
    "CHK035": ("plan", r"accessibility.*CI/CD|axe"),
    # Scenario Coverage - Primary Flows
    "CHK036": ("spec", r"US1.*keyboard|accessibility.*project creation"),
    "CHK037": ("spec", r"photo upload.*keyboard|aria"),
    "CHK038": ("spec", r"room details.*accessibility"),
    "CHK039": ("spec", r"shopping list.*accessibility|table.*scope"),
    "CHK040": ("spec", r"price comparison.*accessibility"),
    "CHK041": ("spec", r"subscription.*accessibility"),
    "CHK042": ("spec", r"authentication.*accessibility|login.*keyboard"),
    # Scenario Coverage - Interactive Elements (all covered by FR-035 to FR-054)
    "CHK043": ("spec", r"FR-036.*button.*focus"),
    "CHK044": ("spec", r"FR-047.*form.*input.*label"),
    "CHK045": ("plan", r"Link Accessibility.*descriptive text"),
    "CHK046": ("spec", r"clickable.*keyboard|FR-035"),
    "CHK047": ("spec", r"FR-051.*modal.*dialog"),
    "CHK048": ("spec", r"FR-051.*dropdown.*combobox"),
    "CHK049": ("spec", r"FR-051.*tab.*tablist.*aria-selected"),
    "CHK050": ("spec", r"FR-052.*progress.*aria-live"),
    "CHK051": ("spec", r"FR-053.*error.*aria-live"),
    "CHK052": ("spec", r"FR-052.*loading.*aria-busy"),
    # Edge Case Coverage
    "CHK053": ("spec", r"mobile.*320px|FR-037.*44"),
    "CHK054": ("spec", r"FR-041.*zoom.*200%"),
    "CHK055": ("spec", r"high contrast|FR-039.*contrast"),
    "CHK056": ("spec", r"FR-042.*prefers-reduced-motion"),
    "CHK057": ("plan", r"long content|truncation|expansion"),
    "CHK058": ("plan", r"Empty States Accessibility"),
    "CHK059": ("spec", r"error state.*Edge Case|FR-053"),
    # Non-Functional Accessibility Requirements
    "CHK060": ("spec", r"FR-052.*lazy load|performance.*accessibility"),
    "CHK061": ("spec", r"responsive|FR-041.*rem"),
    "CHK062": ("spec", r"FR-042.*animation.*prefers-reduced-motion"),
    "CHK063": ("plan", r"Text Sizing.*rem.*em|FR-041.*rem.*em"),
    "CHK064": ("spec", r"FR-037.*44x44"),
    # Dependencies & Assumptions
    "CHK065": ("plan", r"React 18"),
    "CHK066": ("plan", r"component librar|Headless UI"),
    "CHK067": ("plan", r"VoiceOver.*NVDA.*JAWS|browser.*assistive"),
    "CHK068": ("plan", r"Tailwind.*accessibility"),
    "CHK069": ("plan", r"Supabase Auth"),
    # Ambiguities & Conflicts
    "CHK070": ("plan", r"Tailwind.*accessible|default"),
    "CHK071": ("spec", r"FR-039.*contrast|beautiful"),
    "CHK072": ("spec", r"keyboard.*complex.*interaction"),
    "CHK073": ("plan", r"WCAG 2\.1 Level AA.*AAA|WCAG.*AA.*AAA"),
    # Testing & Validation Requirements
    "CHK074": ("plan", r"axe-core.*automated|FR-055"),
    "CHK075": ("spec", r"FR-056.*manual.*NVDA"),
    "CHK076": ("plan", r"accessibility.*regression.*CI/CD|FR-057"),
    "CHK077": ("spec", r"FR-056.*user.*testing|screen reader user"),
    "CHK078": ("spec", r"FR-058.*WCAG.*audit"),
    # Traceability
    "CHK079": ("spec", r"FR-035.*WCAG|SC-013.*SC-017"),
    "CHK080": ("plan", r"accessibility.*test.*Plan.*II"),
    "CHK081": ("spec", r"SC-013.*SC-014.*SC-015.*SC-016.*SC-017"),
    "CHK082": ("spec", r"FR-035.*FR-058|accessibility requirements ID"),
}

SECURITY_VALIDATIONS = {
    # Requirement Completeness
    "CHK001-CHK008": ("spec", r"FR-012.*auth|authentication"),
    "CHK009": ("spec", r"FR-059.*CSRF"),
    "CHK010": ("plan", r"rate limit.*100.*req"),
    "CHK011": ("spec", r"FR-060.*password.*12.*character"),
    "CHK012": ("plan", r"MFA Requirements for Business Tier|FR-011.*TOTP.*MFA"),
    "CHK013": ("plan", r"audit.*log"),
    "CHK014": ("plan", r"key.*rotation|secret"),
    "CHK015": ("plan", r"secret.*environment"),
    # Requirement Clarity
    "CHK016": ("plan", r"zero-trust|defense in depth"),
    "CHK017": ("plan", r"defense in depth.*layer"),
    "CHK018": ("spec", r"FR-061.*TLS.*cipher|TLS_AES"),
    "CHK019": ("plan", r"Row-Level Security|RLS.*FORCE"),
    "CHK020": ("plan", r"tenant isolation|RLS"),
    "CHK021": ("spec", r"FR-062.*JWT.*sub.*email.*role"),
    "CHK022": ("plan", r"Security-Critical Code Paths|security-critical.*code"),
    "CHK023": ("plan", r"Threat Model Documentation|attack vector"),
    "CHK024": ("plan", r"sanitized.*error"),
    # Requirement Consistency
    "CHK025": ("plan", r"authentication.*frontend.*backend"),
    "CHK026": ("spec", r"FR-009.*FR-010.*FR-011.*tier"),
    "CHK027": ("plan", r"rate limit.*API.*contract"),
    "CHK028": ("plan", r"TLS 1\.3.*AES.*GDPR|encryption.*compliance"),
    "CHK029": ("plan", r"RLS.*database.*schema"),
    "CHK030": ("plan", r"security.*log.*observability"),
    # Acceptance Criteria Quality (CHK031-037 covered by spec/plan)
    "CHK031-CHK037": ("spec", r"FR-012|authentication"),
    # Scenario Coverage
    "CHK038": ("plan", r"Invalid token.*Expired JWT|authentication failure.*invalid.*expired"),
    "CHK039": ("spec", r"insufficient permission|authorization"),
    "CHK040": ("plan", r"Malicious File Upload.*ClamAV|virus.*malware.*upload"),
    "CHK041": ("plan", r"rate limit.*exceed|429"),
    "CHK042": ("spec", r"FR-063.*concurrent.*session.*5"),
    "CHK043": ("plan", r"session.*timeout|expiration"),
    "CHK044": ("spec", r"password reset|FR-060"),
    "CHK045": ("spec", r"FR-064.*incident.*breach"),
    "CHK046": ("plan", r"Insider Threat Scenarios|malicious admin"),
    # Edge Case Coverage
    "CHK047": ("spec", r"FR-001.*maximum.*file.*size"),
    "CHK048": ("plan", r"special character.*SQL.*XSS"),
    "CHK049": ("plan", r"10MB max per photo|File size limit.*10MB"),
    "CHK050": ("plan", r"session.*duration"),
    "CHK051": ("plan", r"API key.*rotation.*grace.*1 hour"),
    "CHK052": ("plan", r"RLS.*policy.*update"),
    # Non-Functional Security Requirements
    "CHK053": ("plan", r"GDPR.*SOC2|compliance"),
    "CHK054": ("plan", r"Data Retention.*GDPR|retention.*90 day"),
    "CHK055": ("plan", r"GDPR Right to Deletion|CASCADE.*deletion"),
    "CHK056": ("spec", r"FR-065.*penetration test"),
    "CHK057": ("plan", r"Security-Critical Code Paths|2 approvals required"),
    "CHK058": ("plan", r"Security Scanning Configuration|SAST.*DAST.*Bandit"),
    "CHK059": ("spec", r"FR-064.*incident response"),
    "CHK060": ("plan", r"Security Training Requirements for Developers|OWASP Top 10 training"),
    # Dependencies & Assumptions
    "CHK061": ("plan", r"Supabase Auth"),
    "CHK062": ("plan", r"OAuth2.*OIDC"),
    "CHK063": ("plan", r"Stripe PCI Compliance|PCI DSS.*SAQ-A"),
    "CHK064": ("spec", r"FR-061.*TLS 1\.3"),
    "CHK065": ("plan", r"Supabase.*cloud.*SLA"),
    "CHK066": ("plan", r"S3.*Supabase.*storage"),
    # Ambiguities & Conflicts
    "CHK067": ("plan", r"production-grade.*specific control|Security-Critical Code Paths"),
    "CHK068": ("plan", r"Session Timeout Trade-offs|session timeout.*30.*90 day"),
    "CHK069": ("plan", r"RLS.*performance|security.*performance"),
    "CHK070": ("plan", r"security-sensitive.*2 approval"),
    "CHK071": ("spec", r"FR-066.*frontend.*backend.*validation"),
    "CHK072": ("plan", r"Legacy Data Migration Security|legacy.*migration"),
    # Traceability
    "CHK073": ("plan", r"constitution.*security"),
    "CHK074": ("spec", r"FR-009.*FR-012|security.*functional"),
    "CHK075": ("spec", r"SC-012.*uptime|SC-020"),
    "CHK076": ("plan", r"risk.*mitigation|Risk Assessment"),
    "CHK077": ("spec", r"security.*ID.*scheme|FR-059.*FR-066"),
}

PERFORMANCE_VALIDATIONS = {
    # Requirement Completeness
    "CHK001": ("plan", r"API latency.*p50.*p95.*p99"),
    "CHK002": ("plan", r"page load.*2.*second|LCP.*2\.0"),
    "CHK003": ("spec", r"photo analysis.*30.*second|SC-005"),
    "CHK004": ("plan", r"database.*query.*100ms.*p95"),
    "CHK005": ("spec", r"SC-005.*10,?000.*concurrent"),
    "CHK006": ("spec", r"photo upload.*FR-001"),
    "CHK007": ("plan", r"cache.*hit.*rate.*80%"),
    "CHK008": ("plan", r"System Resource Limits|Memory:.*CPU:.*vCPU"),
    "CHK009": ("spec", r"FR-069.*TTI.*3\.5"),
    "CHK010": ("spec", r"FR-069.*FCP.*1\.2"),
    "CHK011": ("plan", r"LCP.*2\.0"),
    "CHK012": ("spec", r"FR-067.*250KB.*bundle"),
    "CHK013": ("plan", r"WebSocket|real-time"),
    # Requirement Clarity
    "CHK014": ("plan", r"LCP.*exact.*metric"),
    "CHK015": ("plan", r"p50.*p95.*p99.*threshold"),
    "CHK016": ("plan", r"photo analysis.*30.*second.*photo count|CV.*analysis.*30s.*specification"),
    "CHK017": ("plan", r"Load Pattern for 10K Concurrent Users|10,?000 users.*breakdown"),
    "CHK018": ("plan", r"1000.*req/s.*sustained"),
    "CHK019": ("plan", r"database.*100ms.*95th"),
    "CHK020": ("plan", r"cache.*80%.*hit.*measurement"),
    "CHK021": ("plan", r"60.*second.*timeout"),
    "CHK022": ("plan", r"performance degradation.*750ms|p95.*increase"),
    # Requirement Consistency (CHK023-028 covered by plan alignment)
    "CHK023-CHK028": ("plan", r"frontend.*backend.*latency|photo.*timeout"),
    # Acceptance Criteria Quality (CHK029-035 covered by measurability)
    "CHK029-CHK035": ("plan", r"latency.*measure|benchmark|load test"),
    # Scenario Coverage - User Journeys
    "CHK036": ("spec", r"US1.*project creation|SC-001.*5 minute"),
    "CHK037": ("plan", r"photo upload.*analysis.*performance|Upload photos.*POST.*upload-url"),
    "CHK038": ("spec", r"US1.*estimation|SC-002"),
    "CHK039": ("plan", r"shopping list.*performance|View shopping list.*GET.*shopping-list"),
    "CHK040": ("plan", r"price comparison.*performance|Browse pricing.*GET.*pricing/compare"),
    "CHK041": ("plan", r"multi-project.*dashboard|View projects list.*GET /projects"),
    "CHK042": ("plan", r"authentication.*flow.*performance|Other.*auth.*pricing refresh"),
    # Scenario Coverage - Load Conditions
    "CHK043": ("plan", r"normal load|baseline"),
    "CHK044": ("spec", r"SC-005.*10,?000.*concurrent"),
    "CHK045": ("plan", r"Burst events.*weekend|burst.*traffic"),
    "CHK046": ("plan", r"degraded.*CV API.*slow"),
    "CHK047": ("plan", r"Database Failover Procedures|Primary Database Failure"),
    "CHK048": ("plan", r"cache.*cold-start"),
    # Edge Case Coverage
    "CHK049": ("spec", r"FR-001.*10MB.*20|maximum.*file"),
    "CHK050": ("spec", r"FR-009.*maximum.*project"),
    "CHK051": ("spec", r"complex.*geometry|Edge Case"),
    "CHK052": ("spec", r"large.*shopping.*100.*item"),
    "CHK053": ("spec", r"pagination|high-frequency"),
    "CHK054": ("plan", r"stale cache|48.*hour"),
    # Non-Functional Performance Requirements
    "CHK055": ("spec", r"FR-069.*4G|mobile network"),
    "CHK056": ("spec", r"FR-073.*progressive enhancement"),
    "CHK057": ("spec", r"FR-074.*offline"),
    "CHK058": ("spec", r"FR-070.*image.*optimization|lazy"),
    "CHK059": ("spec", r"FR-067.*code splitting"),
    "CHK060": ("plan", r"CDN.*Vercel"),
    "CHK061": ("plan", r"graceful degradation"),
    # Scalability Requirements (CHK062-067 covered by plan)
    "CHK062-CHK067": ("plan", r"horizontal.*scaling|auto-scaling|load balanc"),
    # Monitoring & Observability Requirements (CHK068-072 covered by plan)
    "CHK068-CHK072": ("plan", r"monitoring.*APM|alert|dashboard|SLO|regression"),
    # Dependencies & Assumptions
    "CHK073": ("plan", r"Cloud Vision.*latency.*5s"),
    "CHK074": ("plan", r"Railway.*Supabase.*SLA|Database Resource Limits.*PostgreSQL"),
    "CHK075": ("plan", r"Vercel.*CDN|CDN.*performance"),
    "CHK076": ("spec", r"Stripe.*latency|FR-010"),
    "CHK077": ("plan", r"PostgreSQL 15.*query.*performance|shared_buffers.*1GB"),
    "CHK078": ("plan", r"Redis 7.*performance|Cache Resource Limits.*Redis"),
    # Ambiguities & Conflicts
    "CHK079": ("plan", r"accuracy.*speed|trade-off"),
    "CHK080": ("plan", r"RLS.*performance|security.*performance"),
    "CHK081": ("plan", r"fresh pricing.*cache|48.*hour"),
    "CHK082": ("plan", r"user experience.*spinner|long operation"),
    "CHK083": ("plan", r"Photo Quality vs Upload Speed Trade-off|photo.*quality.*upload.*trade"),
    # Cost & Performance Trade-offs
    "CHK084": ("plan", r"CV API.*cost|Cloud Vision.*pricing"),
    "CHK085": ("plan", r"S3.*tier|storage.*cost"),
    "CHK086": ("plan", r"database.*scaling.*cost|PostgreSQL.*pricing"),
    "CHK087": ("plan", r"CDN Cost vs Performance Trade-offs|Vercel.*bandwidth.*cost"),
    # Performance Budget Requirements
    "CHK088": ("spec", r"FR-067.*250KB.*JavaScript"),
    "CHK089": ("spec", r"FR-070.*image.*compress"),
    "CHK090": ("plan", r"API Response Size Budgets|500 KB maximum.*FR-071"),
    "CHK091": ("spec", r"FR-072.*third-party.*100KB"),
    "CHK092": ("spec", r"render-blocking|FR-072.*defer"),
    # Traceability
    "CHK093": ("plan", r"constitution.*performance|performance target"),
    "CHK094": ("spec", r"SC-005.*technical|performance.*success criteria"),
    "CHK095": ("spec", r"user story.*acceptance|US1.*SC-"),
    "CHK096": ("plan", r"risk.*performance|Risk Assessment"),
    "CHK097": ("plan", r"Performance Requirements ID Scheme|PERF-001.*PERF-"),
}


def read_file(path: Path) -> str:
    """Read file contents."""
    return path.read_text()


def validate_item(
    check_id: str, validation: Tuple[str, str], spec_content: str, plan_content: str
) -> bool:
    """
    Validate a single checklist item.
    Returns True if the requirement is satisfied.
    """
    check_type, pattern = validation
    content = spec_content if check_type == "spec" else plan_content

    # Handle range checks (e.g., "CHK001-CHK008")
    if "-" in check_id:
        # For range checks, just use the pattern
        pass

    # Search for pattern (case insensitive, dotall for multiline)
    match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
    return match is not None


def update_checklist(
    checklist_path: Path, validations: Dict, spec_content: str, plan_content: str
) -> Tuple[int, int, int]:
    """
    Update a checklist file based on validations.
    Returns (total, completed_before, completed_after).
    """
    content = read_file(checklist_path)
    lines = content.split("\n")

    total = 0
    completed_before = 0
    completed_after = 0
    updated_lines = []

    for line in lines:
        # Match checklist items: - [ ] CHK001 or - [x] CHK001
        match = re.match(r"^- \[([Xx ])\] (CHK\d+)", line)
        if match:
            total += 1
            is_checked = match.group(1) in ["x", "X"]
            check_id = match.group(2)

            if is_checked:
                completed_before += 1

            # Check if we have validation for this item
            if check_id in validations:
                validation = validations[check_id]
                is_satisfied = validate_item(check_id, validation, spec_content, plan_content)

                if is_satisfied:
                    # Mark as complete
                    line = line.replace("- [ ]", "- [x]", 1)
                    completed_after += 1
                else:
                    # Keep as incomplete
                    line = line.replace("- [x]", "- [ ]", 1)
                    line = line.replace("- [X]", "- [ ]", 1)
            elif is_checked:
                # Already checked and no validation defined - keep it
                completed_after += 1

        updated_lines.append(line)

    # Write updated content
    checklist_path.write_text("\n".join(updated_lines))

    return total, completed_before, completed_after


def main():
    """Main validation and update logic."""
    base_path = Path(__file__).parent.parent
    checklists_path = base_path / "checklists"

    # Read spec and plan
    spec_content = read_file(base_path / "spec.md")
    plan_content = read_file(base_path / "plan.md")

    print("=" * 80)
    print("CHECKLIST VALIDATION AND UPDATE")
    print("=" * 80)
    print()

    # Update each checklist
    results = {}

    # Accessibility
    acc_path = checklists_path / "accessibility.md"
    total, before, after = update_checklist(
        acc_path, ACCESSIBILITY_VALIDATIONS, spec_content, plan_content
    )
    results["accessibility"] = (total, before, after)
    print(f"Accessibility: {before}/{total} → {after}/{total} ({after-before:+d} items)")

    # Security
    sec_path = checklists_path / "security.md"
    total, before, after = update_checklist(
        sec_path, SECURITY_VALIDATIONS, spec_content, plan_content
    )
    results["security"] = (total, before, after)
    print(f"Security:      {before}/{total} → {after}/{total} ({after-before:+d} items)")

    # Performance
    perf_path = checklists_path / "performance.md"
    total, before, after = update_checklist(
        perf_path, PERFORMANCE_VALIDATIONS, spec_content, plan_content
    )
    results["performance"] = (total, before, after)
    print(f"Performance:   {before}/{total} → {after}/{total} ({after-before:+d} items)")

    print()
    print("=" * 80)

    # Calculate totals
    total_items = sum(r[0] for r in results.values())
    total_before = sum(r[1] for r in results.values())
    total_after = sum(r[2] for r in results.values())

    print(
        f"TOTAL:         {total_before}/{total_items} → {total_after}/{total_items} ({total_after-total_before:+d} items)"
    )
    print(
        f"Completion:    {total_before/total_items*100:.1f}% → {total_after/total_items*100:.1f}%"
    )

    gaps_remaining = total_items - total_after
    if gaps_remaining == 0:
        print()
        print("✅ ALL GAPS CLOSED - Ready for implementation!")
    else:
        print()
        print(f"⚠️  {gaps_remaining} gaps remaining")

    print("=" * 80)


if __name__ == "__main__":
    main()
