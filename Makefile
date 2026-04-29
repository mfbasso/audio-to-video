APP_NAME := audio-to-video
DIST_DIR := dist
BUILD_DIR := build
SPEC_FILE := packaging/pyinstaller.spec
PYINSTALLER_CMD := uv run --with pyinstaller pyinstaller
VERSION ?= $(shell python -c "import tomllib;print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")
GIT_SHA ?= $(shell git rev-parse --short HEAD)
OS_NAME := $(shell uname -s)

FFMPEG_URL_MACOS := https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip
FFPROBE_URL_MACOS := https://evermeet.cx/ffmpeg/getrelease/ffprobe/zip
FFMPEG_URL_WINDOWS := https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip

.PHONY: install-build-deps clean download-ffmpeg build build-macos build-linux build-windows package

install-build-deps:
	uv sync --extra build

clean:
	rm -rf $(BUILD_DIR) $(DIST_DIR) *.spec bin/

download-ffmpeg:
	mkdir -p bin
	@if [ "$(OS_NAME)" = "Darwin" ]; then \
		curl -L $(FFMPEG_URL_MACOS) -o ffmpeg.zip && unzip -o ffmpeg.zip -d bin/ && rm ffmpeg.zip; \
		curl -L $(FFPROBE_URL_MACOS) -o ffprobe.zip && unzip -o ffprobe.zip -d bin/ && rm ffprobe.zip; \
		chmod +x bin/ffmpeg bin/ffprobe; \
	elif [ "$(OS_NAME)" = "Linux" ]; then \
		curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz -o ffmpeg.tar.xz && \
		mkdir -p bin/tmp && tar -xJf ffmpeg.tar.xz -C bin/tmp --strip-components=1 && \
		mv bin/tmp/ffmpeg bin/tmp/ffprobe bin/ && \
		rm -rf bin/tmp ffmpeg.tar.xz; \
		chmod +x bin/ffmpeg bin/ffprobe; \
	fi

download-ffmpeg-windows:
	powershell -Command "New-Item -ItemType Directory -Force -Path bin; \
		Invoke-WebRequest -Uri $(FFMPEG_URL_WINDOWS) -OutFile ffmpeg.zip; \
		Expand-Archive -Path ffmpeg.zip -DestinationPath bin/tmp; \
		Get-ChildItem -Path bin/tmp/ffmpeg-*/bin/*.exe | Move-Item -Destination bin/; \
		Remove-Item -Recurse -Force bin/tmp, ffmpeg.zip"

build: download-ffmpeg
	$(PYINSTALLER_CMD) --clean $(SPEC_FILE)

build-macos: download-ffmpeg
	$(PYINSTALLER_CMD) --clean $(SPEC_FILE)

build-linux: download-ffmpeg
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
