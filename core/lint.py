import os
import json
from openai import AsyncOpenAI
from core.config import OPENAI_API_KEY
from core.memory import remember_permanent
from core.config import WIKI_DATASET

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

WIKI_PAGE_DIR = "wiki_pages"

def load_all_wiki_pages() -> dict[str, str]:
    """Load all wiki pages from disk. Returns {path: content}."""
    pages = {}
    for root, _, files in os.walk(WIKI_PAGE_DIR):
        for fname in files:
            if fname.endswith(".md"):
                full = os.path.join(root, fname)
                rel = os.path.relpath(full, WIKI_PAGE_DIR)
                with open(full) as f:
                    pages[rel] = f.read()
    return pages

async def run_lint() -> list[dict]:
    """Run all lint checks against current wiki pages."""
    pages = load_all_wiki_pages()
    if not pages:
        return [{"type": "info", "message": "No wiki pages found to lint."}]

    pages_text = "\n\n---\n\n".join(
        f"PAGE: {name}\n{content}" for name, content in pages.items()
    )

    prompt = f"""You are a wiki auditor. Review the following wiki pages and find issues.

Check for:
1. duplicates — multiple pages covering the same concept
2. conflicts — pages making contradictory claims
3. stale — pages referencing outdated behavior
4. missing_link — pages that should reference each other but don't
5. unsupported_claim — factual claims with no source

Return ONLY a valid JSON array of issues. Each issue:
{{
  "type": "conflict|duplicate|stale|missing_link|unsupported_claim",
  "page_a": "filename",
  "page_b": "filename or null",
  "claim_a": "the claim",
  "claim_b": "conflicting claim or null",
  "recommendation": "how to fix"
}}

Wiki pages:
{pages_text}

JSON array:"""

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )

    raw = response.choices[0].message.content.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return [{"type": "error", "message": "Failed to parse lint output.", "raw": raw}]

async def apply_lint_fix(issue: dict, fixed_content: str, page_name: str):
    """Apply a lint fix: overwrite the page on disk and in the graph."""
    filepath = os.path.join(WIKI_PAGE_DIR, page_name)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        f.write(fixed_content)
    await remember_permanent(fixed_content, dataset=WIKI_DATASET)

async def auto_fix_issue(issue: dict) -> tuple[str, str]:
    """Option 1: GPT automatically resolves the issue, returns (page_name, fixed_content)."""
    pages = load_all_wiki_pages()
    page_a = issue.get("page_a", "")
    page_b = issue.get("page_b", "")
    content_a = pages.get(page_a, "")
    content_b = pages.get(page_b, "")

    prompt = f"""You are a wiki editor. Two wiki pages have a {issue['type']} issue.

Page A: {page_a}
{content_a}

Page B: {page_b}
{content_b}

Issue:
Claim A: {issue.get('claim_a', '')}
Claim B: {issue.get('claim_b', '')}
Recommendation: {issue.get('recommendation', '')}

Automatically resolve this issue. Rewrite Page A to be correct and consistent with Page B (or vice versa — pick the more accurate version).
Return ONLY the corrected markdown content for the page that should be rewritten, and on the very first line write:
REWRITE_PAGE: <page_a or page_b>

Then the full corrected markdown."""

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    raw = response.choices[0].message.content.strip()
    lines = raw.split("\n")
    page_to_fix = page_a
    if lines[0].startswith("REWRITE_PAGE:"):
        which = lines[0].replace("REWRITE_PAGE:", "").strip()
        page_to_fix = page_a if "page_a" in which or which == page_a else page_b
        raw = "\n".join(lines[1:]).strip()

    return page_to_fix, raw

async def manual_fix_issue(issue: dict, chosen_page: str, user_instruction: str) -> tuple[str, str]:
    """Option 2: User picks which page is correct + gives instruction, GPT rewrites the other."""
    pages = load_all_wiki_pages()
    page_a = issue.get("page_a", "")
    page_b = issue.get("page_b", "")
    correct_content = pages.get(chosen_page, "")
    other_page = page_b if chosen_page == page_a else page_a
    other_content = pages.get(other_page, "")

    prompt = f"""You are a wiki editor. The user has decided that '{chosen_page}' is correct.
Rewrite '{other_page}' to be consistent with the correct page.

Correct page ({chosen_page}):
{correct_content}

Page to rewrite ({other_page}):
{other_content}

User instruction: {user_instruction}

Return ONLY the corrected markdown for '{other_page}'."""

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return other_page, response.choices[0].message.content.strip()
