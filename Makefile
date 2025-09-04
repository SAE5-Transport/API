OS := $(shell uname)

venv:
	python3 -m venv .venv
ifeq ($(OS), Linux)
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
endif
ifeq ($(OS), Windows)
	.venv\Scripts\pip install --upgrade pip
	.venv\Scripts\pip install -r requirements.txt
endif

build:
	python3 -m build --wheel

start: build
	pip install --force-reinstall dist/*
	flask --app api run

.PHONY: *