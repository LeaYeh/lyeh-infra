.PHONY: cv-sync

cv-sync: ## Interactively sync JSON Resume with portal content
	uv run scripts/cv_sync.py
