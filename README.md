# Audio to Video

Aplicativo desktop em Python (Tkinter) para converter áudio em vídeo com gradiente e equalizador animado.

## Requisitos

- Python 3.13+
- `ffmpeg` e `ffprobe` instalados no sistema

No macOS (Homebrew):

```bash
brew install ffmpeg
```

## Instalação

Com `uv`:

```bash
uv sync
```

Ou com `pip`:

```bash
pip install -e .
```

## Execução

```bash
python main.py
```

ou

```bash
audio-to-video
```

## Gerar executável

### Pré-requisitos

- `uv` instalado
- `ffmpeg`/`ffprobe` instalados no sistema (pré-requisito de runtime do app)

### Build local

Instalar dependências de build:

```bash
make install-build-deps
```

Gerar executável para o SO atual:

```bash
make build
```

Saída esperada:

- Pasta `dist/audio-to-video` contendo o executável e bibliotecas.

Empacotar artefato (macOS/Linux):

```bash
make package
```

### CI automatizado

O workflow em `.github/workflows/build-executables.yml` roda a cada push na `main` e gera artefatos para:

- macOS
- Linux
- Windows

## MVP atual

- Seleção de arquivo de áudio
- Seleção de duas cores de gradiente
- Avatar opcional
- Geração de vídeo MP4 (H.264 + AAC) em 720p 30fps
- Barra de progresso e cancelamento
