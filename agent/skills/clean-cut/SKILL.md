---
name: clean-cut
description: >
  MANDATORY FIRST STEP sempre que o usuário pedir para "editar o vídeo" / "edita esse vídeo" /
  "corta esse vídeo" e a fonte for uma gravação bruta de talking-head (uma ou mais takes da
  mesma fala — falsos começos, repetições, "deixa eu tentar de novo", pausas longas) — mesmo
  que o pedido seja genérico, mesmo que um projeto já esteja aberto no Palmier Pro ou em
  qualquer outro editor. Não espere o usuário mencionar "corte", "transcrição" ou "EDL"
  explicitamente: se o vídeo em questão ainda não foi cortado, este é o ponto de entrada, antes
  de tocar em qualquer timeline. Produz um corte mestre limpo + transcrição palavra-a-palavra
  remapeada para a nova timeline. Cobre transcrição local (Whisper), detecção automática de
  repetições/silêncios, geração de uma EDL revisável (cuts.json) ANTES de renderizar, corte por
  ffmpeg, verificação de "ghost speech" (palavra cortada em cima da borda) e drift de duração, e
  revisão de palavras suspeitas da transcrição (termo técnico/nome próprio que o Whisper
  transcreveu errado) ANTES de qualquer legenda ser gerada. Não é para motion graphics nem
  composição do zero, nem para um vídeo que já está cortado —
  depois do corte mestre, passe para /hyperframes, /remotion-create, /talking-head-recut ou
  Palmier Pro (visual) e /embedded-captions (legendas). Se o vídeo já estiver limpo/cortado, ou
  a peça é puramente gráfica sem gravação de fala, use /hyperframes em vez disso.
---

# clean-cut

Estágio que falta entre "gravei falando" e "tenho uma composição HyperFrames/Remotion pronta
pra receber overlays": pegar a gravação crua — cheia de takes repetidos, silêncios e "deixa eu
tentar de novo" — e produzir um **corte mestre limpo** + uma **transcrição remapeada**, prontos
para as skills de composição já instaladas neste repo.

Baseado no pipeline usado pela Anthropic para editar o vídeo de lançamento do Fable 5
(transcrever → selecionar → EDL → cortar), na skill `/clean-cut` do
[claude-youtube-editor](https://github.com/hassancs91/claude-youtube-editor) de Hasan Aboul
Hasan, e no relato prático da XDA sobre editar vídeo dentro do Claude Code. Ver
`references/sources.md`. Diferença chave para o repo de Hasan: aqui a transcrição é 100% local
(Whisper), sem depender de uma chave paga de API — o mesmo espírito da skill `video-editor`
(ffmpeg local) já usada neste ambiente.

## Onde isso entra no pipeline do repo

```
gravação crua
     │
     ▼
  clean-cut  ──────────────►  master.mp4 + edited-transcript.json
     │                              │
     │                              ▼
     │                   revisar transcrição (flag_transcript.py)
     │                              │
     ▼                              ▼
/hyperframes, /remotion-create,   /embedded-captions, /captions-overlay
/talking-head-recut, /general-video   (legendas sobre o corte já limpo,
(camada visual: overlays, motion       com a transcrição já revisada)
graphics, screencasts, título, b-roll)
```

Nunca rode `/hyperframes` ou `/embedded-captions` direto na gravação crua se ela tiver
repetições/silêncios não cortados — o corte mestre é o que garante que a legenda e os overlays
sincronizam com o que efetivamente sobrou no vídeo.

## Se o Palmier Pro já estiver aberto com o vídeo carregado

Um pedido genérico como "edita esse vídeo" com um projeto já aberto no Palmier Pro (via MCP) é
tentador de resolver direto pelas ferramentas de timeline dele — mas isso pula a etapa de corte.
Antes de tocar na timeline do Palmier:

1. Pergunte-se (ou confirme com o usuário) se a fonte é gravação crua não editada. Sinais: um
   único clipe longo, sem cortes visíveis, com pausas/hesitação/repetição de frases.
2. Se sim, rode os passos 1-5 abaixo **fora** do Palmier (transcrever → EDL → cortar →
   verificar) para gerar `master.mp4` + `edited-transcript.json`.
3. Só então importe `master.mp4` como mídia no projeto do Palmier Pro e monte a timeline final
   a partir dele — não do arquivo bruto original.

Se o vídeo já está claramente cortado/editado (múltiplos clipes na timeline, sem repetições),
pule direto para a edição no Palmier — não há corte para fazer.

## Requisitos (rodam na máquina do usuário, não neste container)

- `ffmpeg` + `ffprobe` no PATH
- Python 3.9+ com **um** backend de transcrição:
  - `pip install openai-whisper` (mais simples), ou
  - `pip install faster-whisper` (mais rápido em CPU)
- Nenhuma chave de API paga é necessária. (Se o usuário já tiver AssemblyAI, dá pra trocar o
  passo 1 por ela para mais qualidade — ver `references/sources.md`.)

## Passo a passo

1. **Transcrever** a gravação com timestamp por palavra:
   ```bash
   python scripts/transcribe.py raw/take1.mp4 --lang pt -o work/transcript.json
   ```

2. **Gerar o rascunho da EDL** (`cuts.json`) a partir da transcrição + detecção de silêncio:
   ```bash
   python scripts/detect_takes.py work/transcript.json raw/take1.mp4 -o work/cuts.json
   ```
   Isso agrupa palavras em linhas, marca como `cut` toda linha que é uma repetição de uma linha
   posterior mais similar (mantém a ÚLTIMA tentativa — a mesma regra usada no relato da XDA:
   "the LAST repetition is the keeper"), marca pausas longas como `cut`, e preenche o resto
   como `keep`.

3. **REVISAR `cuts.json` com o usuário antes de cortar.** Isso é um rascunho automático, não a
   decisão final — o pipeline do Fable 5 é justamente "taste in, pipeline out": a curadoria
   humana decide qual take é o bom, o script só cuida da mecânica. Mostre os segmentos `cut` com
   seus motivos e o texto, e deixe o usuário aprovar, remover ou ajustar limites antes do passo 4.

4. **Cortar** e remapear a transcrição:
   ```bash
   python scripts/cut.py work/cuts.json work/transcript.json \
     -o work/master.mp4 --transcript-out work/edited-transcript.json
   ```

5. **Verificar** antes de declarar pronto:
   ```bash
   python scripts/verify_cut.py work/cuts.json work/transcript.json work/master.mp4
   ```
   Checa drift de duração (corte mestre vs. soma dos segmentos `keep`) e "ghost speech"
   (qualquer palavra da transcrição original que atravessa uma borda de corte — sinal de que ela
   vai sair cortada no meio). Saída não-zero = algo para revisar antes de seguir.

6. **Revisar a transcrição ANTES de gerar legenda.** O Whisper erra termo técnico e nome
   próprio — "pre-sales engineer" pode sair como `presails engenieer`, e isso só aparece
   queimado na tela se ninguém checar antes:
   ```bash
   python scripts/flag_transcript.py work/edited-transcript.json -o work/caption-review.md
   ```
   Sinaliza palavra por palavra usando a confiança que o próprio Whisper calcula (campo
   `probability`, abaixo de `--threshold`, padrão 0.55) — e quando essa confiança não está
   disponível, cai para uma heurística de forma (caractere estranho, maiúscula isolada fora de
   uma sigla conhecida como MCP/API/IA). Mostre `work/caption-review.md` ao usuário: cada
   entrada tem a palavra, o timestamp e o contexto ao redor. Se algo estiver errado, corrija o
   campo `word` no índice indicado dentro de `work/edited-transcript.json` e rode de novo até o
   relatório sair limpo. Só gere a legenda (`/embedded-captions`) depois disso.

7. **Handoff**: `work/master.mp4` + `work/edited-transcript.json` (já revisado no passo 6) são
   o input para a próxima etapa visual (`/hyperframes`, `/remotion-create`, `/talking-head-recut`)
   e para legendas (`/embedded-captions`, usando `edited-transcript.json` como a transcrição
   palavra-a-palavra já sincronizada com o corte final).

## cuts.json — schema

```json
{
  "source": "raw/take1.mp4",
  "duration": 187.4,
  "segments": [
    {"start": 0.0,  "end": 4.2,   "action": "cut",  "reason": "false start"},
    {"start": 4.2,  "end": 9.8,   "action": "keep",  "reason": ""},
    {"start": 9.8,  "end": 11.1,  "action": "cut",  "reason": "silence/pause"},
    {"start": 11.1, "end": 15.0,  "action": "keep",  "reason": ""}
  ]
}
```
Edite este arquivo à mão livremente (mudar `action`, ajustar `start`/`end`, apagar/adicionar
segmentos) antes de rodar `cut.py` — é o ponto de controle humano do pipeline.

## Fallback de legenda "queimada" (sem passar por /embedded-captions)

Se for só uma prévia rápida e `ffmpeg drawtext`/fontconfig não estiver disponível na máquina do
usuário (problema relatado no artigo da XDA), dá para desenhar cada palavra como um frame de
imagem (fonte grande, contorno grosso, palavra ativa destacada) e sobrepor no vídeo usando
`edited-transcript.json` para o timing — mas isso é só um atalho de emergência para preview. Para
o resultado final, use a skill `/embedded-captions` (que já cobre o catálogo completo de estilos
de legenda) com `edited-transcript.json` como a transcrição de entrada.

## O que este script NÃO faz (por design)

- Não decide qual take é "o bom" — só detecta repetição por similaridade de texto; a palavra
  final é do usuário no passo 3.
- Não gera thumbnail, música, SFX, nem publica em lugar nenhum — isso é escopo de
  `/media-use` e das skills de composição já instaladas.
- Não corta com precisão sample-exact de áudio entre segmentos re-codificados; para produção
  fina, gere sempre o passo 5 (verify) antes de aprovar.
