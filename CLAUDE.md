# CLAUDE.md — claude-code-video-editor

Este repo edita vídeo por código: corte editorial local a partir de gravação crua (`clean-cut`),
composição visual e legendas (HyperFrames, Remotion), e montagem final opcional numa timeline
visual (Palmier Pro).

## Dependência ausente (`ffmpeg`, Whisper, Node) — instrua, não apenas falhe

Se um comando falhar por `ffmpeg`/`ffprobe`, backend de Whisper (`openai-whisper` /
`faster-whisper`) ou Node.js ausente, não pare no erro cru. Detecte o sistema operacional
(`uname` — Darwin = macOS, Linux, ou pergunte se for ambíguo/Windows) e guie a instalação com o
gerenciador de pacotes certo: `brew` no macOS, `winget` ou WSL2 no Windows, `apt`/`dnf` no Linux
— os comandos exatos estão em `README.md` → "Requisitos". Depois de instalar, repita o comando
que falhou. Lembre também: **Palmier Pro só existe pra macOS (Apple Silicon)** — em Windows/Linux
não ofereça essa etapa, o pipeline termina no render de `/hyperframes`/`/remotion-create`.

## Primeira vez rodando este projeto — customize a identidade antes de editar qualquer vídeo

`brand.md` vem como um **template não preenchido** — é assim que este repo sai do clone, de
propósito, pra qualquer pessoa que baixar customizar a própria voz antes de gerar qualquer texto
de vídeo. Antes de rodar `/clean-cut`, `/hyperframes`, `/embedded-captions`, `/remotion-*`,
`/talking-head-recut` ou qualquer edição no Palmier Pro, **verifique se `brand.md` ainda tem o
aviso `⚠️ TEMPLATE — NÃO CUSTOMIZADO` no topo**:

- Se tiver → **pare** e rode `/brand-setup` primeiro. Ela entrevista o usuário (nome, tom de
  voz, crenças, tipografia, plataforma) e reescreve `brand.md` com a identidade real. Só depois
  disso siga com a edição.
- Se não tiver (já foi customizado) → siga normalmente a partir do passo 1 abaixo.

Isso não é opcional nem pulável só porque o pedido foi genérico ("edita esse vídeo") — sem
`brand.md` customizado, qualquer legenda/hook/título gerado não tem voz nenhuma definida.

## Tom de voz — leitura obrigatória

`brand.md` é o contrato de tom de voz do canal. **Leia `brand.md` antes de escrever qualquer
texto que vai aparecer na tela ou ser falado no vídeo** — legenda (`/embedded-captions`),
hook/título/overlay (`/hyperframes`, `/remotion-*`, `/talking-head-recut`), texto de thumbnail
(pacote final), ou texto dentro de um projeto do Palmier Pro. Vale independente de qual skill de
vídeo estiver rodando — não é uma skill separada que precisa ser invocada, é contexto do projeto.

## Sequência operacional — sempre que o pedido for editar/cortar/preparar um vídeo

Siga esta ordem, pulando só o que não se aplica. Não pule etapas por causa de um pedido genérico
("edita esse vídeo") — a genericidade do pedido não muda o que o vídeo precisa.

0. **`brand.md` já foi customizado?** Ver seção acima. Se não, rode `/brand-setup` antes de
   qualquer outra coisa.

1. **É gravação crua ou já está cortada?** Sinais de crua: um clipe só, sem cortes visíveis,
   nome tipo `VID_YYYYMMDD_HHMMSS...` (padrão de câmera/celular), pausas ou repetição de fala —
   mesmo que já esteja carregada num projeto do Palmier Pro.
   - Crua → passo 2.
   - Já cortada/editada → pule pro passo 3.

2. **`/clean-cut`** (obrigatório antes de qualquer visual ou legenda):
   1. `transcribe.py` → `work/transcript.json`
   2. `detect_takes.py` → `work/cuts.json` (rascunho)
   3. **revisão humana do `cuts.json`** — pergunte, não decida sozinho qual take é o bom
   4. `cut.py` → `work/master.mp4` + `work/edited-transcript.json`
   5. `verify_cut.py` — se falhar (drift ou ghost speech), ajuste `cuts.json` e repita o passo 4
   6. `flag_transcript.py` → `work/caption-review.md`
   7. **revisão humana das palavras sinalizadas** — corrija `edited-transcript.json` se precisar

3. **Camada visual**, se o pedido envolver overlay/motion graphics/título/screencast:
   `/hyperframes`, `/remotion-create` ou `/talking-head-recut`, usando `master.mp4` como fonte.

4. **Legenda**, se o pedido envolver isso: `/embedded-captions` ou `/captions-overlay`, usando
   `edited-transcript.json` (já revisado no passo 2.7) — `brand.md` entra sozinho aqui, não
   precisa pedir.

   Passos 3 e 4 não dependem um do outro — podem rodar em qualquer ordem.

5. **Montagem final opcional**, só quando o Claude Code está rodando localmente num Mac com o
   Palmier Pro aberto (`/palmier-pro`): importar `master.mp4` + os renders dos passos 3/4 como
   mídia, montar a timeline, exportar via XML se for entregar pra outro editor. Color grading só
   entra se pedido explicitamente — ver a seção "Color grading" da skill.

Ver `README.md` para a visão geral do pipeline e o estado atual (o que funciona, o que fica de
fora, o que falta), e `.agents/skills/` para o conteúdo de cada skill.
