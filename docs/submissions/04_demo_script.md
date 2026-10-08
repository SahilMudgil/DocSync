# 5-Minute Mid-Sem Evaluation Presentation Script (A2 Demo)
**Project:** DocSync — AI DevOps Documentation Intelligence in CI/CD  
**Audience:** Faculty Evaluator / Examiner  

---

### Step 1: Problem Definition & Motivation (30 Seconds)
> *"Good morning, faculty. In modern software engineering and continuous integration, developers frequently update code (changing default parameters, modifying return types, or updating exceptions). However, documentation and API guides often lag behind, misleading developers and users. Standard CI/CD unit tests pass because tests only verify runtime code, not documentation accuracy.*  
> *DocSync is an AI DevOps documentation intelligence gate that detects documentation drift on pull requests and provides an interactive repository code Q&A bot."*

---

### Step 2: Show the Deterministic Offline Demo (90 Seconds)
**Command to run:**
```bash
python scripts/run_demo.py
```
**Talking points while it runs:**
1. *"Here we simulate a live git repository across three commits."*
2. *"Commit C0 to C1 was a harmless developer refactor (adding a code comment). DocSync checks it and returns **MATCH**—proving we have no false alarms on cosmetic changes."*
3. *"Commit C1 to C2 changed the `timeout` parameter from 30 to 60 seconds in `client.py`, but the documentation was left untouched."*
4. *"DocSync immediately catches the contradiction, flags **DRIFT** with 1.0 confidence, cites evidence tokens `E2` and `D1`, and automatically generates a unified diff repair suggesting to change 30 to 60 seconds."*

---

### Step 3: Demonstrate the Interactive Repository Code Q&A Bot (60 Seconds)
**Command to run:**
```bash
python -m docsync.cli ask "How does fetch_data handle timeout?" --repo examples/demo_project
```
**Talking points:**
> *"This directly fulfills our A2 syllabus requirement for a **RAG-based Code Q&A bot**. Using LangChain and vector embeddings over our parsed code symbols and documentation chunks, the model answers the question and provides exact citations to file paths and line ranges (`docs/usage.md:3-13` and `client.py:5-12`)."*

---

### Step 4: Show DevOps Architecture & Containerization (60 Seconds)
**Show the screen / files:**
- **Dockerfile & docker-compose.yml:** *"DocSync is fully containerized with multi-stage builds and health checks, exposing our Streamlit web application on port 8501."*
- **GitHub Actions (`.github/workflows/docsync-pr.yml`):** *"Every pull request triggers our AI DevOps gate in CI/CD. It checks the PR diff, posts an automated review comment, and uploads run artifacts."*
- **AWS Cloud Instance:** *"To run resource-heavy open code models like DeepSeek-Coder without bogging down our local machines, we host an Ollama instance on an AWS EC2 Ubuntu instance and connect via environment endpoints."*

---

### Step 5: Web Application Demo & Q&A (60 Seconds)
**Command to launch:**
```bash
streamlit run dashboard/streamlit_app.py
```
**Talking points:**
> *"Our Streamlit dashboard allows reviewers to visually explore PR drift check runs, examine the unified diffs, and query the repository Q&A bot, satisfying the course criterion for a demonstrable web application."*
