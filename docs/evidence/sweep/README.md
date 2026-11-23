# Sweep.dev Autonomous Documentation Remediation & CI Flow

This directory documents the autonomous documentation drift remediation loop via **Sweep.dev** and GitHub Actions.

---

## 1. Architecture: The Closed-Loop Flow

```
[Developer PR]
       │
       ▼
 [GitHub Actions: docsync check]
       │
       ├─── No Drift detected ──────────► [Status Check: PASS]
       │
       └─── Drift detected (Confidence ≥ 0.8)
                 │
                 ├──► [Action: docsync comment] (Posts PR report with unified diff)
                 │
                 └──► [Action: docsync open-issue] (Creates Sweep remediation issue)
                           │
                           ▼
                    [Sweep.dev GitHub App]
                           │ (Reads AST evidence & proposed unified diff)
                           ▼
                    [Sweep Drafts Remediation PR]
                           │
                           ▼
              [GitHub Actions: docsync check runs on Sweep PR]
                           │
                           ▼
              [Loop Guard Verification: MATCH / Clean PASS]
```

---

## 2. Strict Loop Guards (Recursion Prevention)

To prevent automated bots and CI runners from triggering endless loops, `docsync open-issue` implements 4 rigorous guards:

1. **Bot Author Guard:** Automatically ignores PRs authored by automated accounts (`sweep[bot]`, `github-actions[bot]`, `dependabot`).
2. **Branch Name Guard:** Ignores PRs originating from branches prefixed with `sweep/`.
3. **Label Guard:** Ignores any PR or issue marked with the `docsync-ignore` label.
4. **De-duplication Guard:** Queries the repository's open issues via GitHub API and suppresses duplicate issue creation if an open issue with the title `Sweep: update docs for <symbol> in <doc file>` already exists.

---

## 3. Deployment Tiers

### Tier A (Sweep.dev App Installed & Active)
1. Install Sweep GitHub App on the repository.
2. Ensure repository setting **Settings → Actions → General → Workflow permissions** has:
   - *Read and write permissions*
   - *Allow GitHub Actions to create and approve pull requests*
3. When DocSync flags high-confidence drift, it creates an issue with label `sweep`.
4. Sweep reads the issue, applies the diff repair, and opens a draft PR.

### Tier B (Fallback / Offline / Limited Rate Mode)
If the Sweep GitHub App is unreachable or rate-limited:
1. DocSync exports the unified diff patch using `python -m docsync.cli apply-patch --input results/latest.json --out demo/patches/drift_repair.patch`.
2. A GitHub Action step creates a draft pull request directly from the patch for human engineering review.
3. The limitation is documented honestly without falsifying autonomous executions.

---

## 4. Student Evidence Checklist
- [ ] Screenshot 1: DocSync PR Comment posted on GitHub PR.
- [ ] Screenshot 2: Sweep issue created with label `sweep` and loop guards active.
- [ ] Screenshot 3: Sweep generated draft pull request containing the documentation patch.
- [ ] Screenshot 4: DocSync CI run on the Sweep PR passing cleanly (Closed loop).
