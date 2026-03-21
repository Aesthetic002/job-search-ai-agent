# Git Workflow Guide — Job Search AI Agent

> A step-by-step guide for all team members on how to collaborate using Git and GitHub.

---

## 1. Clone the Repository

Each team member should run this once to download the project locally:

```bash
git clone https://github.com/Aesthetic002/job-search-ai-agent.git
cd job-search-ai-agent
```

---

## 2. Create Your Own Branch

> **No one should ever work directly on `main`.**

Each person creates their own feature branch off `main`:

```bash
git checkout main
git pull origin main
git checkout -b feature/your-branch-name
```

### Branch names for this team:

| Branch Name | Owner | Phase |
|---|---|---|
| `feature/langgraph-agent` | Hemanth | Phase 1 |
| `feature/resume-parser` | Kaisen | Phase 1 |
| `feature/frontend-dashboard` | Rohith | Phase 2 — after Phase 1 is done |
| `feature/job-api-integrations` | Aaryan | Phase 3 — after Phase 1 is merged |

> See `docs/branch-guide.md` for the full breakdown of what each branch should build.

---

## 3. Make Changes and Commit

After making your changes, stage and commit them:

```bash
git add path/to/changed/file
git commit -m "Brief description of what changed"
```

> Avoid using `git add .` — stage only the files you intentionally changed to avoid accidentally committing unwanted files.

**Write clear commit messages** that describe what you changed, for example:
```
Add JWT login route to auth_service
Implement PDF parsing in resume_parser.py
Add job search filter UI component
```

---

## 4. Push Your Branch to GitHub

```bash
git push origin feature/your-branch-name
```

Your branch will now appear on GitHub for others to see.

---

## 5. Open a Pull Request (PR)

On GitHub:

1. Click **"Compare & Pull Request"**
2. Set the merge direction: `feature/your-branch-name → main`
3. Add a clear description of what was built and what was tested

---

## 6. Review and Merge

At least **1 team member must approve** the PR before it can be merged:

```
Team member  →  opens PR
Any other member  →  reviews and approves
Hemanth (lead)  →  merges into main
```

> Branch protection on `main` ensures **no one can push directly** — all changes must go through an approved PR.

---

## 7. Daily Workflow

Before starting work each day, sync your branch with the latest `main`:

```bash
git checkout main
git pull origin main
git checkout feature/your-branch-name
git merge main
```

This keeps your branch up to date and prevents large merge conflicts.

---

## Team Branch Structure

```
main (protected)
├── feature/langgraph-agent       ← Hemanth  (Phase 1)
├── feature/resume-parser         ← Kaisen   (Phase 1)
├── feature/frontend-dashboard    ← Rohith   (Phase 2 — starts after Phase 1)
└── feature/job-api-integrations  ← Aaryan   (Phase 3 — starts after Phase 1 merged)
```

Each person owns one branch. PRs are reviewed and merged into `main` at the end of each phase.

---

## Example Full Team Workflow

```
Hemanth  →  feature/langgraph-agent       →  PR  →  Review  →  Merge  (Phase 1)
Kaisen   →  feature/resume-parser         →  PR  →  Review  →  Merge  (Phase 1)
Rohith   →  feature/frontend-dashboard    →  PR  →  Review  →  Merge  (Phase 2)
Aaryan   →  feature/job-api-integrations  →  PR  →  Review  →  Merge  (Phase 3)
```

---

## The Three Rules

```
1. Never commit directly to main
2. Always create a feature branch
3. Always open a PR
```

---

*Last updated: March 2026*
