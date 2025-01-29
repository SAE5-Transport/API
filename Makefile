OS := $(shell uname)

venv:
	python -m venv .venv
ifeq ($(OS), Linux)
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
endif
ifeq ($(OS), Windows)
	.venv\Scripts\pip install --upgrade pip
	.venv\Scripts\pip install -r requirements.txt
endif

.PHONY: *