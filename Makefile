.PHONY: cv-sync cv-tailor cv-lint cv-publish cv-render cv-build cv-test

GIST_ID  := $(shell sed -n 's/^GIST_ID=//p' scripts/cv-sync.env 2>/dev/null | tr -d '"[:space:]')

# Headless Chrome used by cv-render to print HTML -> PDF.
# Auto-detects the macOS app, a Linux chromium, or google-chrome on PATH.
# Override: make cv-render CHROME=/path/to/chrome
CHROME ?= $(shell \
  for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
           "$$(command -v chromium 2>/dev/null)" \
           "$$(command -v chromium-browser 2>/dev/null)" \
           "$$(command -v google-chrome 2>/dev/null)"; do \
    [ -x "$$c" ] && { echo "$$c"; break; }; \
  done)

cv-sync: ## Fold portal/blog content into docs/resume/cv.json — assisted; use the /cv-sync skill
	@echo "Flow 1 (intake) is LLM-assisted: run the /cv-sync skill in Claude Code."
	@echo "(legacy portal→Gist tool scripts/cv_sync.py is superseded by the SSOT design.)"

cv-tailor: ## Curate cv.json into a facet resume — assisted; use the /cv-tailor skill
	@echo "Flow 2 (targeting) is LLM-assisted: run the /cv-tailor <a|b|c> [--jd <url>] skill in Claude Code."

cv-lint: ## Drift backstop: invariants in resume-*.json must match cv.json (decision #13)
	python3 scripts/cv-lint.py

cv-publish: cv-lint ## Push docs/resume/cv.json to the public Gist (decision #11)
	@test -n "$(GIST_ID)" || { echo "GIST_ID missing in scripts/cv-sync.env"; exit 1; }
	python3 -c "import json,sys; c=open('docs/resume/cv.json').read(); \
sys.stdout.write(json.dumps({'files':{'resume.json':{'content':c}}}))" \
	  | gh api -X PATCH /gists/$(GIST_ID) --input - >/dev/null
	@echo "✓ Gist $(GIST_ID) updated from docs/resume/cv.json"
	@cp docs/resume/cv.json apps/portal/src/data/resume.json && echo "✓ portal data copy refreshed"

cv-render: ## Render cv.json (detailed) + resume-*.json (1-page) to PDF via scripts/cv_render.py + headless Chrome (decision #12)
	@test -n "$(CHROME)" || { echo "No Chrome/Chromium found; set CHROME=/path/to/chrome"; exit 1; }
	@set -e; cd docs/resume; \
	for f in cv.json resume-*.json; do \
	  [ -e "$$f" ] || continue; \
	  n="$${f%.json}"; \
	  case "$$f" in cv.json) mode=cv ;; *) mode=resume ;; esac; \
	  python3 ../../scripts/cv_render.py "$$f" --mode $$mode --out "$$n.html"; \
	  "$(CHROME)" --headless=new --disable-gpu --no-pdf-header-footer \
	    --print-to-pdf="$$n.pdf" "$$n.html" 2>/dev/null; \
	  rm -f "$$n.html"; \
	  echo "  ✓ $$n.pdf ($$mode)"; \
	done
	@echo "✓ PDFs rendered into docs/resume/"

cv-test: ## Run the resume tooling test suite
	python3 -m pytest scripts/tests -q
