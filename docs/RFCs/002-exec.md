# Exec

O objetivo é permitir que seja gerado um arquivo executável de fácil utilização e distribuição, para que o usuário final possa usar o programa sem precisar configurar um ambiente Python ou instalar dependências manualmente.

A ideia é ter também um Makefile que permita gerar o executável de forma simples de preferência para cada sistema operacional (Windows, macOS, Linux). O processo de empacotamento deve incluir o Python e todas as dependências necessárias para rodar o programa, garantindo que o usuário final tenha uma experiência suave ao usar o aplicativo.

Também deve ser adicionado um github action para automatizar o processo de build e gerar os executáveis para cada plataforma, facilitando a distribuição e garantindo que os arquivos estejam sempre atualizados com as últimas mudanças no código. O trigger deve ser configurado para rodar a cada push na branch main, garantindo que os executáveis estejam sempre disponíveis para os usuários finais.

## Plano Técnico

### 1) Objetivo e escopo

Entregar empacotamento do aplicativo em executáveis distribuíveis para **macOS, Windows e Linux**, sem exigir instalação manual de Python ou dependências por parte do usuário final.

Este plano cobre:

- Geração local via `Makefile`.
- Build automatizado via GitHub Actions a cada push na `main`.
- Publicação de artefatos por plataforma.

### 2) Estratégia de empacotamento

Será adotado **PyInstaller** como empacotador principal por ser maduro, multiplataforma e adequado para apps desktop com Tkinter.

- Modo padrão: `onedir` (mais estável para MVP de distribuição).
- Nome do app: `audio-to-video`.
- Entry point: `main.py`.
- Inclusão do interpretador Python e dependências no bundle final.

#### Sobre FFmpeg

Como o app depende de `ffmpeg`/`ffprobe`, haverá duas abordagens possíveis:

1. **MVP recomendado (mais simples e robusto):** manter `ffmpeg` como pré-requisito externo e validar no startup.
2. **Evolução futura:** embutir binários de `ffmpeg` por plataforma no bundle (aumenta complexidade de build/licenciamento/distribuição).

Para esta RFC, o plano inicial segue a opção 1 para reduzir risco e tempo de entrega.

### 3) Estrutura proposta de build

- `Makefile`
  - `install-build-deps`: instala dependências de build.
  - `clean`: remove `build/`, `dist/` e arquivos temporários.
  - `build`: build padrão para o SO atual.
  - `build-macos`, `build-linux`, `build-windows`: alvos explícitos (executados no respectivo SO).
  - `package`: compacta saída em `.zip` (Windows) e `.tar.gz` (macOS/Linux).

- `packaging/pyinstaller.spec` (opcional, recomendado)
  - Centraliza configurações de bundle.
  - Facilita manutenção de data files, ícones e ajustes por plataforma.

### 4) Dependências de build

Adicionar dependências de desenvolvimento para empacotamento:

- `pyinstaller`
- `build` (opcional, para distribuição wheel/sdist complementar)

No CI, manter instalação com `uv` ou `pip` (conforme padrão do repositório) para garantir reprodutibilidade.

### 5) Pipeline de CI/CD (GitHub Actions)

Criar workflow em `.github/workflows/build-executables.yml` com:

- **Trigger**: `push` na branch `main`.
- **Matriz de SO**:
  - `ubuntu-latest`
  - `windows-latest`
  - `macos-latest`
- **Passos por job**:
  1.  Checkout do código.
  2.  Setup do Python (versão do projeto).
  3.  Instalação de dependências de runtime + build.
  4.  Execução do alvo de build (`make build` ou comando equivalente no Windows).
  5.  Empacotamento do diretório final.
  6.  Upload de artefatos com nome contendo SO e commit SHA.

### 6) Convenção de artefatos

Nome sugerido:

- `audio-to-video-macos-<sha>.tar.gz`
- `audio-to-video-linux-<sha>.tar.gz`
- `audio-to-video-windows-<sha>.zip`

Conteúdo mínimo:

- Executável principal.
- Bibliotecas incluídas pelo PyInstaller.
- `README` curto de uso.

### 7) Experiência do usuário final

- O usuário baixa o artefato da plataforma.
- Descompacta e executa o binário.
- Caso `ffmpeg` não esteja disponível no sistema (MVP), o app exibe mensagem orientando instalação.

### 8) Segurança e confiabilidade

- Build isolado por plataforma (sem cross-compilar localmente).
- Logs de build preservados nos jobs.
- Checks mínimos antes de empacotar:
  - inicialização do app,
  - presença dos arquivos esperados em `dist/`.

### 9) Riscos e mitigação

- **Diferenças entre plataformas** (paths, permissões, runtime):
  - Mitigação: matriz nativa no GitHub Actions.
- **Falso sucesso de build sem executável funcional**:
  - Mitigação: smoke test simples no CI após gerar binário.
- **Dependência externa de ffmpeg no MVP**:
  - Mitigação: validação no startup + instruções claras no README.

### 10) Roadmap de entrega

**Fase 1 — Base de empacotamento**

- Adicionar PyInstaller e comando de build local.
- Criar `Makefile` com alvos `clean`, `build`, `package`.

**Fase 2 — Automação CI**

- Criar workflow GitHub Actions com matriz de SO.
- Publicar artefatos por push na `main`.

**Fase 3 — Refino de distribuição**

- Melhorar naming/versionamento dos artefatos.
- Adicionar smoke tests e checklist de release.

### 11) Critérios de aceite

Esta RFC será considerada atendida quando:

- Houver comando local simples para gerar executável.
- Houver `Makefile` com alvos de build e package.
- Houver workflow no GitHub Actions acionado por push em `main`.
- O workflow gerar artefatos para macOS, Linux e Windows.
- O usuário final conseguir executar o app sem instalar Python manualmente.
