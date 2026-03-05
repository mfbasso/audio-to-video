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

## MVP atual

- Seleção de arquivo de áudio
- Seleção de duas cores de gradiente
- Avatar opcional
- Geração de vídeo MP4 (H.264 + AAC) em 720p 30fps
- Barra de progresso e cancelamento
