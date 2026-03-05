# Audio to Video

A proposta desse projeto é que usando o tkinter o usuário consiga subir um áudio e o programa converta ele pra vídeo usando um gradiente de fundo e um equalizador gráfico seguindo a imagem abaixo:

![alt text](image.png)

O usuário poderá selecionar o arquivo de áudio, qual as cores do gradiente, a possibilidade opcional de colocar uma imagem de avatar (tipo imagem). O programa irá processar o áudio e gerar um vídeo com o equalizador gráfico animado de acordo com a música, além do gradiente de fundo e a imagem de avatar (se selecionada). O vídeo gerado poderá ser salvo no formato MP4 ou outro formato de vídeo comum.

## Plano Técnico

### 1) Abordagem de desenvolvimento

Para este projeto, vamos seguir **Arquitetura em Camadas + MVP incremental + ADR-lite**.

- **Arquitetura em Camadas**: separa interface (Tkinter), orquestração (casos de uso), domínio (regras de visualização/configuração) e infraestrutura (análise de áudio, render e encode).
- **MVP incremental**: entrega uma primeira versão funcional ponta a ponta rapidamente, evoluindo em ciclos curtos.
- **ADR-lite (Architecture Decision Record simplificado)**: registra decisões técnicas importantes de forma curta no próprio RFC (trade-offs e impacto).

Essa abordagem reduz acoplamento, facilita manutenção e permite evoluir visual/qualidade sem reescrever a base.

### 2) Escopo do MVP (v1)

O MVP deve entregar o fluxo completo abaixo:

1. Selecionar arquivo de áudio (entrada).
2. Selecionar duas cores para gradiente de fundo.
3. Selecionar imagem de avatar (opcional).
4. Gerar vídeo com:
   - fundo em gradiente,
   - equalizador animado com base no áudio,
   - avatar opcional sobreposto.
5. Exportar em **MP4 (H.264 + AAC), 720p, 30fps**.

### 3) Requisitos funcionais

- Upload de áudio em formatos comuns (ex.: mp3, wav, flac).
- Escolha de duas cores de gradiente via UI.
- Upload opcional de avatar (png/jpg/webp).
- Pré-validação de entradas antes de processar.
- Processamento com feedback visual de progresso.
- Salvamento do vídeo em caminho escolhido pelo usuário.

### 4) Requisitos não funcionais

- Compatibilidade inicial com macOS.
- Renderização estável para áudios curtos e longos (sem limite fixo no MVP).
- Tratamento de erros com mensagens claras (arquivo inválido, ffmpeg ausente, falha de encode).
- Logs básicos para diagnóstico.
- Uso controlado de memória (processamento por janelas/chunks).

### 5) Stack técnica proposta

- **UI desktop**: Tkinter.
- **Processamento numérico/FFT**: NumPy.
- **Composição de frames**: Pillow.
- **Encode e mux de áudio/vídeo**: FFmpeg (CLI).
- **Leitura de metadados/validação**: ffprobe (quando necessário).

Motivo da escolha: FFmpeg oferece robustez e compatibilidade de codec; NumPy + Pillow dão controle visual e boa performance para evolução futura.

### 6) Arquitetura (camadas)

Sugestão de módulos:

- `ui/`
  - telas Tkinter, seleção de arquivos, cores e progresso.
- `application/`
  - orquestra fluxo de geração (`RenderJobService`).
- `domain/`
  - modelos de configuração (`RenderConfig`, `VisualizerConfig`), validações e regras.
- `infrastructure/`
  - `audio_analyzer` (FFT e bandas),
  - `frame_renderer` (gradiente, barras, avatar),
  - `video_encoder` (integração com FFmpeg),
  - `storage` (temporários e saída final).

Princípio: a UI não conhece detalhes de FFmpeg/FFT; apenas dispara o caso de uso com configurações.

### 7) Pipeline de geração do vídeo

1. **Entrada**: usuário define áudio, cores, avatar opcional e arquivo de saída.
2. **Validação**: checar formato, acessos de leitura/escrita e disponibilidade do FFmpeg.
3. **Análise de áudio**:
   - dividir áudio em janelas temporais,
   - aplicar FFT,
   - mapear energia por bandas do equalizador,
   - suavizar transições para animação fluida.
4. **Render de frames**:
   - desenhar gradiente,
   - desenhar barras do equalizador por frame,
   - compor avatar opcional.
5. **Encode**:
   - gerar stream de vídeo com FFmpeg,
   - mux com áudio original,
   - exportar MP4 720p30.
6. **Finalização**:
   - limpar temporários,
   - informar sucesso/erro ao usuário.

### 8) Estratégia de UX

- Fluxo simples em uma janela principal (sem navegação complexa).
- Botão de gerar desabilitado até campos mínimos válidos.
- Barra de progresso por etapa (análise, render, encode).
- Botão de cancelar processamento com encerramento seguro.
- Mensagens de erro acionáveis (o que falhou + como resolver).

### 9) Estratégia de qualidade

**Validação manual (MVP):**

- Caso feliz: áudio curto/médio/longo com e sem avatar.
- Casos de erro: arquivo corrompido, extensão inválida, sem permissão de escrita, FFmpeg não instalado.
- Compatibilidade de saída: abrir MP4 em QuickTime e VLC.
- Verificação técnica: confirmar fps, resolução e codecs com ffprobe.

**Métricas mínimas de acompanhamento:**

- Tempo total de processamento por minuto de áudio.
- Taxa de falhas por etapa (análise/render/encode).
- Uso máximo aproximado de memória durante render.

### 10) Riscos e mitigação

- **Performance em áudios longos**
  - Mitigação: render por chunks, evitar acumular todos os frames em memória.
- **Dependência externa do FFmpeg**
  - Mitigação: checagem no startup e orientação clara de instalação.
- **Diferenças de codec/player**
  - Mitigação: padrão H.264 + AAC com parâmetros conservadores.
- **Acoplamento da UI com pipeline**
  - Mitigação: manter separação estrita por camadas.

### 11) Roadmap de entrega

**Fase 1 — Vertical slice (MVP funcional)**

- UI mínima com seleção de áudio e cores.
- Equalizador básico animado.
- Export MP4 720p30.

**Fase 2 — Recursos visuais e UX**

- Avatar opcional.
- Barra de progresso e cancelamento.
- Melhorias de suavização da animação.

**Fase 3 — Robustez e operação**

- Erros padronizados e logging.
- Melhorias de performance para arquivos longos.
- Documentação de execução e troubleshooting.

### 12) Critérios de aceite do MVP

O MVP será considerado concluído quando:

- Permitir selecionar áudio, definir gradiente e opcionalmente avatar.
- Gerar vídeo com equalizador sincronizado perceptivelmente com o áudio.
- Exportar MP4 720p30 reproduzível em players comuns.
- Exibir progresso e mensagens de erro claras nos principais cenários de falha.
- Não travar a interface durante processamento (responsividade mínima).
