# Fontes

Esta skill foi montada a partir de três relatos independentes do mesmo padrão — gravação
crua entra, corte editorial limpo sai, curadoria humana no meio — e não é um port de nenhum
deles; é uma implementação local (só Whisper + ffmpeg, sem chave de API paga) do mesmo
princípio.

- **Fable 5 editando seu próprio vídeo de lançamento** (Thariq Shihipar, Anthropic).
  17 takes, 4 cenas, 25GB de material 4K. Pipeline: *"taste in, pipeline out: transcribe →
  select → EDL → cut"* — Whisper transcreve, Claude Code seleciona os melhores takes, gera uma
  EDL com timestamps, ffmpeg executa os cortes. Curadoria humana no meio, não automação cega.
  Deck: https://thariqs.github.io/cc-video-editing-deck/

- **`claude-youtube-editor`** (Hasan Aboul Hasan / LearnWithHasan). Pipeline open source
  completo de gravação crua até upload no YouTube, com 8 skills (`/clean-cut`, `/make-tsx`,
  `/fake-screencast`, `/clean-audio`, `/suggest-sfx`, `/packaging`, `/thumbnail`,
  `/brand-setup`). A etapa `/clean-cut` de lá — AssemblyAI transcreve, você autora `cuts.json`
  a partir da transcrição, sai um master limpo + `edited-transcript.json` — é o modelo direto
  desta skill; a diferença é que aqui a transcrição roda local (Whisper) em vez de AssemblyAI,
  e a detecção de retake/silêncio é automática (rascunho para revisão) em vez de manual.
  Repo: https://github.com/hassancs91/claude-youtube-editor

- **Relato prático da XDA** ("I turned my terminal into a video editor using Claude Code").
  Regra de retake: grave a mesma frase várias vezes, "the LAST repetition is the keeper. Cut
  the earlier attempts" — a mesma lógica implementada em `detect_takes.py`. Também descreve o
  fallback de legenda "queimada" como frames de imagem quando os filtros de texto do ffmpeg
  não estão disponíveis, e um loop de revisão/re-render até o corte ficar limpo.
  https://www.xda-developers.com/turned-my-terminal-into-a-video-editor-using-claude-code/

## O que foi deliberadamente deixado de fora

Do pipeline completo de Hasan, esta skill cobre só a etapa 1 (o corte). As etapas 2-6 dele
(visuais TSX, limpeza de voz por IA, SFX, thumbnails, upload) já têm equivalente neste repo via
`/hyperframes`, `/remotion-*`, `/embedded-captions`, `/media-use` — ou dependem de chaves de API
pagas (ElevenLabs, Gemini, OAuth do YouTube) que não fazem parte do escopo pedido aqui.
