# VeriText · Document Similarity Checker

A responsive document comparison workspace built with HTML, CSS, JavaScript, Python, and scikit-learn. Compare a submitted document with a reference corpus using hybrid TF-IDF and cosine similarity, then inspect sentence-level evidence and download a report.

**GitHub Pages ready:** the default browser engine runs without a server, API key, npm install, or build step. An optional FastAPI backend uses scikit-learn for the same hybrid methodology.

## Features

- Fixed full-screen research-desk photograph with scrolling, readable content panels and responsive layout.
- Paste text or upload UTF-8 `.txt` files; drag and drop reference uploads.
- Compare against up to 10 references, with per-source word, character, and hybrid scores.
- Word unigram/bigram and character 3–5-gram TF-IDF representations.
- Adjustable sentence-match threshold and best-source evidence per flagged sentence.
- Download JSON and plain-text reports; load a working example with one click.
- Local browser processing by default; optional explicitly selected Python API.
- No accounts, document persistence, or analytics.

## Run immediately

Extract the project and open `index.html` in a current browser. Click **Load example → Analyze similarity**.

For a local HTTP server, run from the project directory:

```bash
python -m http.server 5500
```

Open `http://localhost:5500`. The Google Fonts stylesheet is optional; system fonts are used if it cannot load. Document text is not sent to Google Fonts. Text is sent only to a backend you explicitly configure.

## Upload to GitHub and publish — easiest method

1. Extract `veritext-github-ready.zip` on your computer.
2. On GitHub, create a **public** repository named `veritext`. A public repository supports Pages on GitHub Free.
3. Choose **Add file → Upload files** (or the new repository's “uploading an existing file” link).
4. Open the extracted `veritext` folder. Upload its **contents**, keeping `index.html`, `README.md`, and `assets/` at the repository root. Do not upload the ZIP or put everything inside another `veritext/` folder.
5. Commit the files to `main`. Browser upload may omit dotfiles; they are not needed for the basic demo. Use the Git method below to include `.gitignore`, `.nojekyll`, and CI.
6. Open **Settings → Pages**. Under **Build and deployment**, select **Deploy from a branch**.
7. Select **main** and **/(root)**, then **Save**.
8. Wait for the Pages deployment to finish. Settings → Pages displays **Visit site**, normally `https://YOUR_USERNAME.github.io/veritext/`.
9. Open the site and use **Load example → Analyze similarity** to check it. If it fails, inspect the repository's **Actions** tab for deployment errors.
10. In the repository's **About** panel, add the live URL and topics such as `tf-idf`, `document-similarity`, `javascript`, `python`, and `scikit-learn`.

GitHub Pages hosts the browser engine. It does **not** execute the Python API. No backend is required for the published demo.

### Upload the complete project with Git

Install Git from its official source first. Create an empty GitHub repository without initializing another README, then run these commands **inside the extracted project folder**:

```bash
git init
git branch -M main
git add .
git commit -m "Build VeriText document similarity checker"
git remote add origin https://github.com/YOUR_USERNAME/veritext.git
git push -u origin main
```

Replace `YOUR_USERNAME`. Complete GitHub's prompted authentication; do not put access tokens in these files. Then configure Pages using steps 6–9 above. If the remote already has files, clone it first and copy the project into that clone rather than forcing a push.

## Optional Python / scikit-learn backend

Requires Python 3.10+. Run all commands from the project root:

```bash
python -m venv .venv
```

Activate on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```bash
source .venv/bin/activate
```

Then:

```bash
python -m pip install -r backend/requirements.txt
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

In a second terminal, serve the frontend with `python -m http.server 5500`. Open `http://localhost:5500`, expand **Optional Python backend**, enter `http://127.0.0.1:8000`, and select **Apply engine**. Analyze normally. Clear the URL and apply to switch back. The setting is intentionally not persisted across reloads.

- Health: `GET /health`
- API documentation: `http://127.0.0.1:8000/docs`
- Analysis: `POST /api/analyze`

Example JSON body:

```json
{
  "document": "Machine learning finds patterns in data.",
  "references": [{"name": "Notes", "text": "Machine learning finds patterns in data."}],
  "threshold": 0.45
}
```

For separate backend hosting, use a Python-capable host with the repository root as its working directory, install `backend/requirements.txt`, and run `python -m uvicorn backend.app:app --host 0.0.0.0 --port PORT` using the host's port value. Set `ALLOWED_ORIGINS` to your exact frontend origin, for example `https://YOUR_USERNAME.github.io` (no repository path). In the UI use the deployed HTTPS backend URL. A hosted frontend needs a reachable backend; another person's `localhost` cannot reach your computer.

This is a portfolio API, not a hardened public service. Add authentication/rate limiting, request timeouts, concurrency and memory limits at the hosting layer before exposing it to heavy or untrusted traffic. CORS controls browsers, not API authorization. The API does not deliberately store or log submitted text; your host's policies still apply.

## How scoring works

1. Normalize casing and whitespace.
2. Fit smoothed TF-IDF separately for word 1–2-grams and character 3–5-grams on target plus references.
3. Normalize vectors and compute cosine similarity to each reference.
4. Blend: **hybrid = 0.65 × word similarity + 0.35 × character similarity**.
5. Show the highest reference score as maximum document similarity.
6. Split text at sentence punctuation/newlines. Fit a separate TF-IDF space over all target and reference sentences. Select the best matching reference sentence for every target sentence and flag scores meeting the threshold.

Scores are multiplied by 100 for display. The threshold affects sentence flags, not whole-document scores. Adding references changes IDF weights and can change results. The two implementations share the methodology but may differ slightly in Unicode tokenization and floating-point behavior. Sentence splitting is heuristic; abbreviations and decimal points can split unexpectedly. Short text can produce unstable scores.

**The complement, 100 − maximum similarity, is not a verified originality percentage.** Similarity is not a plagiarism verdict, copying probability, or percentage of words copied. Quotes, common phrases, and legitimate reuse can match. This compares only supplied references; it does not search the internet, identify AI writing, or reliably detect semantic paraphrases.

## Limits

- `.txt` UTF-8 only; convert PDF, DOCX, and scanned files externally first.
- 50,000 characters per document; 150,000 reference characters total; 10 sources.
- Upload files up to 100 KB; API request bodies up to 1 MB.
- Target up to 300 sentences; reference corpus up to 1,500 sentences.
- Browser work is synchronous and large inputs can briefly pause the interface.
- No database, account system, web crawling, or plagiarism certification.

## Project map

| Path | Purpose |
| --- | --- |
| `index.html` | Frontend layout and entry point |
| `assets/styles.css` | Responsive styling |
| `assets/engine.js` | Dependency-free browser TF-IDF engine |
| `assets/app.js` | Inputs, validation, rendering, API selection, report exports |
| `backend/engine.py` | scikit-learn comparison engine |
| `backend/app.py` | Stateless FastAPI API with request validation and CORS |
| `backend/requirements.txt` | Python runtime dependencies |
| `examples/` | Example target and reference text |
| `tests/` | Browser and Python engine regression checks |
| `.github/workflows/checks.yml` | Engine checks on push and pull request |
| `LICENSE` | MIT license |

## Tests

JavaScript engine (Node.js 18+):

```bash
node tests/engine.test.cjs
```

Python engine (install backend requirements first):

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Checks cover exact copies, unrelated documents, passage thresholds, very short inputs, and sentence limits. They are regression checks, not an accuracy benchmark. No precision/recall claim is made.

## Why GitHub may show only HTML

The language label on a repository card identifies the primary detected language; it is not a list of the entire stack. GitHub Linguist analyzes files on the default branch and calculates language shares by code bytes. CSS and JS can be present even when the card says HTML. Open the repository's **Languages** panel for its full breakdown.

Inline `<style>` and `<script>` blocks live inside an HTML file rather than separate CSS and JS files. Confirm that actual `.css` and `.js` files were committed to the default branch. Vendor/generated exclusions and `.gitattributes` can also affect detection. Statistics can take time to update after a push. Do not manipulate language statistics just to make the label look different.

## Sources

- [GitHub Pages publishing configuration](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
- [Creating a GitHub Pages site](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)
- [GitHub repository languages](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-repository-languages)
- [GitHub Linguist methodology](https://github.com/github-linguist/linguist/blob/main/docs/how-linguist-works.md)

## License

MIT. See [LICENSE](LICENSE). Before publishing, personalize the repository description and add your own screenshots or evaluation results if desired.

## Background photograph

Photo by Mikhail Nilov on [Pexels](https://www.pexels.com/photo/laptops-and-documents-on-desk-7989234/), included locally as `assets/research-desk.jpg` under the [Pexels License](https://www.pexels.com/license/). The MIT license covers project code, not the third-party photograph. No remote image request is needed at runtime.
