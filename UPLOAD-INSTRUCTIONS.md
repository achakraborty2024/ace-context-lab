# Manual GitHub upload

Target: https://github.com/achakraborty2024/ace-context-lab

## Browser upload

1. Extract `ace-context-lab-manual-upload.zip`.
2. Open the repository in GitHub while signed into an account with write access.
3. Choose **Add file → Upload files**.
4. Open the extracted `ace-context-lab` folder. Upload its contents, preserving subfolders. Do not upload the ZIP itself or put the outer `ace-context-lab` folder inside the repository.
5. Include `.github/workflows/tests.yml` for automated tests and `.gitignore`. On macOS, Command+Shift+Period reveals hidden files in Finder. If browser upload omits these, use the Git method below.
6. Replace the starter README with the included `README.md` and commit with the message `Add agent memory research pilot and reproducible demo`.
7. Open the repository home page to check the README chart and links. Open **Actions** to check test results after the upload.

## Git upload (preserves all folders)

Open a terminal in the directory containing the extracted `ace-context-lab` folder. These commands clone the existing repository so its initial commit is preserved:

```bash
git clone https://github.com/achakraborty2024/ace-context-lab.git ace-context-lab-upload
cp -R ace-context-lab/. ace-context-lab-upload/
cd ace-context-lab-upload
python3 -m unittest discover -s tests -v
git status --short
git add .
git commit -m "Add agent memory research pilot and reproducible demo"
git push origin main
```

Use your usual GitHub authentication. If `main` has changed since cloning, pull and reconcile those changes before pushing; do not force-push.

## Suggested repository About text

Reproducible Python and SQLite research lab for agent memory under changing operational rules, with simulation evidence and a selective-verification roadmap.

Suggested topics: `agent-memory`, `context-engineering`, `llm-agents`, `ai-agents`, `research`, `python`, `sqlite`, `reproducibility`.

Public visibility makes the repository accessible. Search indexing and traffic are not guaranteed. This package does not configure or publish a GitHub Pages website; the README is the project landing page.

## Included evidence and status

The project contains the six-policy simulator, optional Ollama adapter, 12 tests, GitHub Actions workflow, research paper, references, roadmap, charts and complete compressed pilot records. The trace contains 144,000 simulated decisions. It is not production data or a real-model evaluation. Selective verification remains proposed and untested.

Run the default demo from the project root:

```bash
python3 -m ace_lab.run --out results/reproduce --seeds 20 --steps 240
```

Choose a new output directory for each run. The simulator needs Python 3.10+ and no third-party packages. Matplotlib is optional for regenerating figures.
