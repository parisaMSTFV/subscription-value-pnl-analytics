.PHONY: reproduce fixture check

reproduce:
	MPLCONFIGDIR=.matplotlib subscription-value demo --data-dir data/sample --output-dir artifacts --reports-dir reports

fixture:
	MPLCONFIGDIR=.matplotlib subscription-value analyze --data-dir data/fixture --output-dir artifacts/fixture --reports-dir artifacts/fixture-reports --start 2025-07-01 --end 2025-10-01 --as-of 2026-01-01

check:
	python -m ruff check .
	python -m ruff format --check .
	MPLCONFIGDIR=.matplotlib python -m pytest
	python scripts/check_sensitive.py
