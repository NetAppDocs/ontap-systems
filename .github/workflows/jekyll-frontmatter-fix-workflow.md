# Jekyll Front Matter Fix Workflow

**Status**: Production workflow — proven across 16+ folders, 90+ files fixed

**Purpose**: Identify and fix unsupported characters in Jekyll front matter fields (`title`, `keywords`, `summary`) that cause publishing errors.

**Note**: This workflow document captures the actual working pattern. For historical agent architecture attempts, see `.github/agents/jekyll-frontmatter-check-orchestrator.md` and `jekyll-frontmatter-fix-subagent.md`.

---

## The Problem

Jekyll front matter fields must contain only plain text. Unsupported characters cause:
- Missing HTML files in published site
- Failed PDF generation
- Search indexing failures
- Rendering errors

**Field-specific validation rules:**

| Field | Disallowed characters | Allowed exceptions |
|-------|----------------------|-------------------|
| `title:` | `! @ # $ % & * ( ) + = [ ] { } \| \\ : ; , < > ? /` | None |
| `keywords:` | `! @ # $ % & * ( ) + = [ ] { } \| \\ : ; / < > ?` | `,` (delimiter) |
| `summary:` | `! @ # $ % & * ( ) + = [ ] { } \| \\ : ; < > ?` | `"` `'` `,` `/` |

**Critical distinctions:**
- `/` is **forbidden in keywords** (e.g., `time/date` → `time and date`)
- `/` is **allowed in summary** (e.g., `boot/recovery` is fine)

---

## Working Pattern

This is the proven pattern that successfully processed 16+ folders (a150, a70-90, a200, a1k, a20-30-50, a220, a250, a300, a320, a400, a700, a700s, a800, a900, afx-1k, asa-c250, asa-c400, asa-c800):

### Step 1: List directory

```
list_dir(target_folder)
```

Identify all `.adoc` files (exclude `sidebar.yml`, `_index.yml`, `_include/` files unless requested).

### Step 2: Read all front matter in parallel

```
read_file(file1, lines 1-15)
read_file(file2, lines 1-15)
...
read_file(file10, lines 1-15)
```

Read in batches of 10-15 files at once. Front matter is always in the first ~10 lines.

### Step 3: Identify issues

For each file, inspect `title:`, `keywords:`, and `summary:` fields:

**Common violations:**
- Bare parentheses: `(RTC)`, `(PSU)`, `(ECC)`, `(OKM)`, `(NSE)`, `(NVE)`
- Backslash-escaped parens: `\(OKM\)`, `\(SVMs\)`
- URLs: `https://mysupport.netapp.com/...`
- AsciiDoc notation: `[NetApp Support]`, `[text]`
- Phone numbers: `+800-800-80-800`, `888-463-8277`
- Semicolons: `(ECC); failure to do so`
- Ampersands: `&` (replace with `and`)
- **Keywords-specific**: `/` slash (e.g., `time/date`)

Build a list of files with issues.

### Step 4: Read leads for files needing rewrites

For files where the summary needs rewriting (not just character removal), read the `[.lead]` paragraph:

```
read_file(file_with_issues, lines 10-20)
```

Use lead text as the source for the corrected summary.

### Step 5: Apply all fixes in one batch

```
multi_replace_string_in_file([
  {file: "file1.adoc", oldString: "...", newString: "..."},
  {file: "file2.adoc", oldString: "...", newString: "..."},
  ...
])
```

**Fix patterns:**

| Issue | Fix |
|-------|-----|
| `(RTC)` | Remove parens → `RTC` |
| `\(OKM\)` | Remove backslash and parens → `OKM` |
| `time/date` in keywords | → `time and date` |
| `&` | → `and` |
| `;` | Rewrite sentence to avoid |
| URL, phone numbers, AsciiDoc links | Delete or rewrite from lead |
| Summary with multiple issues | Rewrite from lead paragraph |

**Example replacements:**

```javascript
// Bad summary with URL, phone, AsciiDoc notation
"Contact technical support at https://mysupport.netapp.com/site/global/dashboard[NetApp Support], 888-463-8277 (North America), 00-800-44-638277 (Europe), or +800-800-80-800 (Asia/Pacific) if you need the RMA number"

// Good summary from lead
"After you replace the boot media, return the failed part to NetApp."
```

### Step 6: Create JSON checkpoint

```
create_file("folder/_frontmatter-check-state.json", jsonContent)
```

**JSON structure:**

```json
[
  {
    "fileName": "bootmedia-complete-rma.adoc",
    "hasIssues": "Yes",
    "titleIssues": [],
    "keywordsIssues": [],
    "summaryIssues": ["URL with disallowed chars", "Phone numbers with disallowed chars"],
    "originalTitle": null,
    "originalKeywords": null,
    "originalSummary": "Contact technical support at https://...",
    "fixedTitle": null,
    "fixedKeywords": null,
    "fixedSummary": "After you replace the boot media, return the failed part to NetApp.",
    "fixApplied": "Yes"
  },
  {
    "fileName": "install-setup.adoc",
    "hasIssues": "No",
    "titleIssues": [],
    "keywordsIssues": [],
    "summaryIssues": [],
    "originalTitle": null,
    "originalKeywords": null,
    "originalSummary": null,
    "fixedTitle": null,
    "fixedKeywords": null,
    "fixedSummary": null,
    "fixApplied": "No"
  }
]
```

---

## Performance Characteristics

**Typical folder (40 files):**
- List directory: <1 second
- Read all front matter (4 batches of 10): ~5 seconds
- Identify issues: <1 second
- Read leads (6 files): ~2 seconds
- Apply fixes: 2-3 seconds
- Create checkpoint: <1 second

**Total: ~10-15 seconds per folder**

**Success rate**: 100% (all `multi_replace_string_in_file` operations succeeded)

---

## Common File Patterns

Files that consistently have issues across folders:

1. **bootmedia-complete-rma.adoc** — URL, phone numbers, AsciiDoc notation
2. **bootmedia-encryption-restore.adoc** — `\(OKM\)`, `\(NSE\)`, `\(NVE\)`
3. **controller-replace-restore-system-rma.adoc** — `(if necessary)`, URL, phone numbers
4. **dimm-replace.adoc** — `(ECC)`, semicolon
5. **power-supply-replace.adoc** — `(PSU)`
6. **rtc-battery-replace.adoc** — `(RTC)`, `time/date` in keywords
7. **bootmedia-2n-mcc-switchback.adoc** — `\(SVMs\)`
8. **bootmedia-replace-overview.adoc** — `\(boot image\)`

---

## Validation

After applying fixes, optionally re-read front matter (lines 1-15) and verify:

**Title field check:**
```regex
[!@#$%&*()+=[]{}\|\\:;,<>?/]
```
Should find no matches.

**Keywords field check:**
```regex
[!@#$%&*()+=[]{}\|\\:;/<>?]
```
Should find no matches. (Commas are OK)

**Summary field check:**
```regex
[!@#$%&*()+=[]{}\|\\:;<>?]
```
Should find no matches. (Quotes, commas, slashes are OK)

---

## Tips

**Parallel reads:**
- Read 10-15 files at once (don't wait for each sequentially)
- Front matter is always in first 10-15 lines, safe to read without checking length

**Field-specific fixes:**
- Don't validate all fields with same rules — keywords ≠ summary
- Keywords: watch for `/` (common in `time/date`)
- Summary: prefer rewriting from lead over stripping characters

**Batch edits:**
- `multi_replace_string_in_file` is atomic — all succeed or all fail
- Include enough context (3-5 lines before/after) for unique match
- Test patterns: RMA files always need rewrites, DIMM files always have semicolons

**Checkpoint files:**
- One per folder, created at end
- Useful for tracking progress across 50+ folders
- Exclude from git (they're documentation artifacts)

---

## Historical Note

This workflow evolved from initial agent-based architecture (see `.github/agents/` for reference). The agent approach proved unnecessary — the task is straightforward enough for direct execution without delegation or progressive checkpointing.

**Why this works better than agents:**
1. Parallel batch reads (10x faster than sequential)
2. All fixes applied atomically (no partial states)
3. Simple validation (field-specific character checks)
4. No delegation overhead (direct tool usage)
5. Single checkpoint at end (no incremental complexity)

The pattern is proven across 90+ files with 100% success rate.
