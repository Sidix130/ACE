# Makefile pour ACE (Adaptive Chat Extractor)

.PHONY: help setup test clean run install b

install: setup
	$(PIP) install -e .

# Variables
VENV = venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip
PYTEST = $(VENV)/bin/pytest
MAIN = ace/main.py

help:
	@echo "Usage:"
	@echo "  make setup    : Crée l'environnement virtuel et installe les dépendances"
	@echo "  make test     : Lance la suite complète de tests unitaires"
	@echo "  make run IN=<file.html> OUT=<file.md> : Lance la conversion d'un fichier"
	@echo "  make b   : Génère un bundle Repomix optimisé pour l'audit"

setup:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install beautifulsoup4 pytest

test:
	PYTHONPATH=. $(PYTEST) tests/

clean:
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run:
	@if [ -z "$(IN)" ] || [ -z "$(OUT)" ]; then \
		echo "Erreur : Spécifiez IN et OUT. Exemple: make run IN=chat.html OUT=chat.md"; \
		exit 1; \
	fi
	PYTHONPATH=. $(PYTHON) $(MAIN) "$(IN)" "$(OUT)"

b:
	repomix --ignore "input/**,venv/**,__pycache__/**,.git/**,dist/**,build/**,*.egg-info/**,conversations.json,user.json,*.zip,*.html.md,repomix-output.xml,demo_grok_*.md,extres-demo-grok.md,test_chat.*,*.html,*.json" --include "ace/**,tests/**,README.md,pyproject.toml" --style xml -o repomix-output-opti.xml
