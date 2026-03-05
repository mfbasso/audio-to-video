APP_NAME := audio-to-video
DIST_DIR := dist
BUILD_DIR := build
SPEC_FILE := packaging/pyinstaller.spec
PYINSTALLER_CMD := uv run --with pyinstaller pyinstaller
VERSION ?= $(shell python -c "import tomllib;print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")
GIT_SHA ?= $(shell git rev-parse --short HEAD)
OS_NAME := $(shell uname -s)

.PHONY: install-build-deps clean build build-macos build-linux build-windows package

install-build-deps:
	uv sync --extra build

clean:
	rm -rf $(BUILD_DIR) $(DIST_DIR) *.spec

build:
	$(PYINSTALLER_CMD) --clean $(SPEC_FILE)

build-macos:
	$(PYINSTALLER_CMD) --clean $(SPEC_FILE)

build-linux:
	$(PYINSTALLER_CMD) --clean $(SPEC_FILE)

build-windows:
	$(PYINSTALLER_CMD) --clean $(SPEC_FILE)

package: build
	@if [ "$(OS_NAME)" = "Darwin" ]; then \
		tar -czf $(APP_NAME)-macos-$(GIT_SHA).tar.gz -C $(DIST_DIR) $(APP_NAME); \
		echo "Pacote gerado: $(APP_NAME)-macos-$(GIT_SHA).tar.gz"; \
	elif [ "$(OS_NAME)" = "Linux" ]; then \
		tar -czf $(APP_NAME)-linux-$(GIT_SHA).tar.gz -C $(DIST_DIR) $(APP_NAME); \
		echo "Pacote gerado: $(APP_NAME)-linux-$(GIT_SHA).tar.gz"; \
	else \
		echo "Use package no Linux/macOS. No Windows, compacte a pasta dist/$(APP_NAME) em .zip."; \
		exit 1; \
	fi
