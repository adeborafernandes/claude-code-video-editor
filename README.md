# claude-code-video-editor

Pipeline de edição de vídeo por código pra criador de conteúdo, pra usar com Claude Code — parte
instalada via [`skills`](https://skills.sh), parte escrita pra este repositório. Template: clone,
customize sua própria identidade, edite seus vídeos.

## Quickstart

```bash
git clone <url-deste-repo>
cd claude-code-video-editor
claude
```

Na primeira execução, o Claude vai identificar que `brand.md` ainda é um template não preenchido
e pedir pra rodar `/brand-setup` antes de qualquer coisa — uma entrevista curta (nome, tom de
voz, crenças, tipografia, plataforma) que reescreve `brand.md` com a sua identidade. Depois
disso, qualquer legenda/hook/título/overlay gerado já sai na sua voz, automaticamente — não
precisa repetir isso a cada vídeo. Ver `.agents/skills/brand-setup/SKILL.md`.

## Ferramentas incorporadas

- **[Remotion](https://www.remotion.dev/docs/ai/skills)** — criação de vídeo programática em React (`remotion-*`). Cobre criação de projeto, markup/animações, captions, mapas, render, preview no Studio, multimídia e upgrade de pacotes. *(instalada via `skills`)*
- **[HyperFrames](https://hyperframes.heygen.com/)** ([repo](https://github.com/heygen-com/hyperframes)) — criação de vídeo a partir de HTML/CSS/animações (GSAP, Lottie, Three.js etc.), sem build step, renderizado via Puppeteer + FFmpeg. Inclui workflows prontos para vídeo de produto, explicativos, recut de talking-head, changelog, slideshow, motion graphics e vídeo sincronizado com música, além da doutrina de movimento e transições da HyperFrames. *(instalada via `skills`)*
- **`clean-cut`** — corte editorial de gravação crua (transcrever → detectar retakes/silêncios → EDL revisável → cortar → verificar → revisar transcrição), 100% local (Whisper + ffmpeg). Escrita para este repo, inspirada no pipeline que a Anthropic usou para editar o vídeo de lançamento do Fable 5, na skill `/clean-cut` do [`claude-youtube-editor`](https://github.com/hassancs91/claude-youtube-editor) de Hasan Aboul Hasan, e no [relato da XDA](https://www.xda-developers.com/turned-my-terminal-into-a-video-editor-using-claude-code/) sobre editar vídeo dentro do Claude Code. Ver `.agents/skills/clean-cut/references/sources.md` para os detalhes e o que ficou de fora de propósito.
- **`brand-setup`** — entrevista que gera `brand.md`, o contrato de tom de voz/tipografia que toda skill de vídeo aqui lê antes de escrever texto na tela. Escrita para este repo — é o que torna o template customizável em vez de vir com uma identidade fixa embutida.
- **[Palmier Pro](https://www.palmier.io/)** ([repo](https://github.com/palmier-io/palmier-pro)) — editor de vídeo NLE nativo de macOS (timeline visual, trim, keyframes, color grading, geração de footage com Seedance/Kling/FLUX in-app), controlado por agentes via um servidor MCP local (`http://127.0.0.1:19789/mcp`, registrado em `.mcp.json` na raiz deste repo). **Só funciona rodando localmente num Mac Apple Silicon (macOS 26+) com o app aberto.** Ver `.agents/skills/palmier-pro/SKILL.md` para quando usar em vez das skills de código.

## Pipeline

```
brand-setup (uma vez, na primeira execução) ──► brand.md customizado
                                        │
gravação crua  ──clean-cut──►  master.mp4 + edited-transcript.json
                                        │
                                        ▼
                          revisar transcrição (flag_transcript.py)
                                        │
                   ┌────────────────────┴────────────────────┐
                   ▼                                          ▼
   /hyperframes, /remotion-create,           /embedded-captions, /captions-overlay
   /talking-head-recut   (visuais, headless)              (legendas)
                   └────────────────────┬────────────────────┘
                                        ▼
                     Palmier Pro (opcional, só local/macOS)   (timeline visual final,
                                                                 mix com IA in-app, export
                                                                 p/ Premiere/Resolve/FCP)
```

Todo texto que aparece na tela em qualquer etapa acima (legenda, hook, título, overlay) segue
`brand.md` — o contrato de tom de voz gerado pela entrevista do `/brand-setup`. `CLAUDE.md` faz
isso valer automaticamente em qualquer sessão neste repo, sem precisar invocar uma skill separada
— e bloqueia a edição até `brand.md` ser customizado, se ainda não foi.

## Estado do pipeline

### O que já dá pra fazer hoje

Customização de identidade na primeira execução (`brand-setup`), corte editorial (`clean-cut`),
legendas com posicionamento e tipografia definidos por `brand.md` (`embedded-captions`), motion
graphics/overlays/títulos (`hyperframes`, `remotion-*`), mixagem de áudio/SFX/música
(`hyperframes-audio`, `media-use`), transições (`motion-doctrine`, `cut-the-curve`,
`seam-craft`), revisão de transcrição antes de queimar legenda (`clean-cut/scripts/flag_transcript.py`,
ver abaixo), e montagem final numa timeline visual com export pra outros editores (Palmier Pro,
só local).

### Color grading — desligado por padrão

`media-use` sabe resolver color grade / LUT pra footage "dark, flat, boring, retro", e o Palmier
Pro tem color grading nativo na timeline — nenhuma skill aciona isso sozinha. Se quiser usar,
peça explicitamente; ver a seção "Color grading" em `.agents/skills/palmier-pro/SKILL.md`.

### Revisão de legenda antes de queimar

`clean-cut` tem um passo entre o corte e a legenda: `scripts/flag_transcript.py` roda em cima de
`edited-transcript.json` e sinaliza palavra por palavra usando a confiança que o próprio Whisper
já calcula (campo `probability` — abaixo de um limiar, a palavra é sinalizada). Sem esse campo,
cai para uma heurística de forma (caractere estranho, maiúscula isolada fora de sigla conhecida).
Gera um relatório com palavra + timestamp + contexto ao redor, pra revisar contra o áudio e
corrigir antes de qualquer legenda ser gerada — pensado exatamente pra pegar casos como um termo
técnico ("pre-sales engineer") saindo transcrito errado. Ver passo 6 em
`.agents/skills/clean-cut/SKILL.md`.

### Lacunas conhecidas — onde dá pra melhorar

1. **Filler word não é detectado.** O `/clean-cut` hoje só corta repetição de frase inteira e silêncio — "tipo", "né", "hum" no meio de uma frase boa não é pego. É um passo a mais de fácil de adicionar.
2. **Sem thumbnail/packaging.** Deixamos essa etapa de fora de propósito (era a parte paga do pipeline do Hasan, via Gemini). Hoje não tem nenhuma skill aqui que gere título + thumbnail otimizados pra CTR.
3. **Sem reframe/resize vertical formalizado no pipeline.** Existe parcialmente em `media-use`, mas não está costurado no fluxo `clean-cut → hyperframes`.
4. **`/clean-cut` só julga por similaridade de texto, não por qualidade de entrega.** Se duas falas são diferentes mas uma teve tom melhor, ele não percebe — a curadoria de "qual take soou melhor" ainda é 100% humana, no passo de revisão do `cuts.json`.

## Estrutura

- `.agents/skills/` — conteúdo canônico de cada skill (`SKILL.md` + assets/scripts/referências), incluindo `clean-cut` e `brand-setup`.
- `.claude/skills/` — symlinks para `.agents/skills/`, o formato que o Claude Code lê diretamente.
- `agent/skills/` — cópia em formato universal, para outros agentes (Cursor, Codex, etc.) que não seguem o layout do Claude Code.
- `skills-lock.json` — lockfile gerado pela CLI `skills`, referencia origem e versão das skills **instaladas** (Remotion, HyperFrames). `clean-cut`, `brand-setup` e `palmier-pro` não estão nele por serem escritas à mão neste repo, não puxadas de um pacote externo.
- `.mcp.json` — configuração de servidor MCP no formato do Claude Code; registra o Palmier Pro (só tem efeito localmente, com o app aberto).
- `brand.md` — contrato de tom de voz para texto dentro do vídeo (legendas, hooks, títulos, overlays). **Vem como template não preenchido** — gerado de verdade pela entrevista do `/brand-setup` na primeira execução.
- `CLAUDE.md` — bloqueia a edição de vídeo até `brand.md` ser customizado, e tem a sequência operacional completa (qual skill roda quando) para o Claude Code seguir sozinho.
- `plugin.json`, `mcp.json`, `skills/` — este repo empacotado como [Agent Plugin](https://agent-plugins.org/) portável (ver seção abaixo). Aditivo: não substitui nada do que já existia para o Claude Code.

## Agent Plugin

Além do layout específico do Claude Code, este repo também é um pacote conforme a
[especificação Agent Plugins 1.0.0](https://agent-plugins.org/specification) — o padrão aberto
mantido com Microsoft, GitHub, OpenAI, AWS, Cursor e Vercel pra empacotar skills + servidores MCP
num formato único que qualquer client compatível consegue consumir direto, sem o passo de
"gerar uma cópia universal por ferramenta" que a CLI `skills` faz hoje em `agent/skills/`.

- **`plugin.json`** — manifesto na raiz (`name: claude-code-video-editor`), obrigatório pela spec.
- **`skills/`** — o diretório que a spec espera pra descoberta de skills; symlinks pra
  `.agents/skills/`, mesmo padrão do `.claude/skills/`, só que num nome que qualquer client
  Agent Plugins sabe procurar sozinho.
- **`mcp.json`** (sem ponto, na raiz) — o Palmier Pro no formato da spec (`"type":
  "streamable-http"` em vez do `"type": "http"` do `.mcp.json` do Claude Code — são schemas
  parecidos mas não idênticos, por isso os dois arquivos coexistem).

Isso não muda nada de como o Claude Code já usa este repo — `.claude/skills/` e `.mcp.json`
continuam sendo o caminho que ele lê. O ganho é portabilidade: se um dia você abrir este repo
num client diferente que já fale Agent Plugins, as skills e o servidor MCP do Palmier já
funcionam sem precisar reinstalar nada.

## Uso — sequência do vídeo cru ao pronto

Isso roda **localmente**, com o Claude Code aberto dentro deste repositório (`ffmpeg`/`ffprobe`
+ um backend de Whisper instalados — ver requisitos em `.agents/skills/clean-cut/SKILL.md`).
Não precisa decorar a ordem — o `CLAUDE.md` já tem essa sequência escrita pro Claude seguir
sozinho — mas pra saber o que esperar:

0. **Primeira vez só:** o Claude nota que `brand.md` é um template e pede pra rodar
   `/brand-setup` — responda a entrevista uma vez, o resto do pipeline usa isso sozinho dali em
   diante.
1. **Grave o vídeo.** Fora do Claude Code — é só a matéria-prima.
2. **Peça pra editar**, de forma genérica mesmo: *"edita esse vídeo"* / *"corta esse vídeo aqui"*.
   Se for gravação crua, o Claude reconhece sozinho e roda `/clean-cut`: transcreve, detecta
   retakes/silêncio, te mostra o rascunho do corte pra você aprovar, corta, verifica, e te mostra
   as palavras suspeitas da legenda pra revisar — **duas pausas pra sua aprovação** nesse meio
   tempo. No final: `work/master.mp4` + `work/edited-transcript.json`.
3. **Peça a camada visual e/ou legenda**, se precisar: *"adiciona um título no início"* aciona
   `/hyperframes`; *"põe legenda"* aciona `/embedded-captions` já com o tom, a fonte e o
   posicionamento do `brand.md` aplicados sozinhos.
4. **Se quiser montar a timeline final visualmente ou exportar pra Premiere/Resolve/Final Cut**,
   abra o Palmier Pro antes de iniciar a sessão local e peça a montagem — só funciona localmente
   (ver `/palmier-pro`).

Comandos individuais, se quiser invocar uma skill direto em vez de pedir em linguagem natural:

- `/brand-setup` — entrevista de customização de identidade (rodar antes de tudo, na primeira vez).
- `/clean-cut` — corte editorial de uma gravação crua de talking-head.
- `/remotion-best-practices` — roteador para todas as skills do Remotion.
- `/hyperframes` — ponto de entrada obrigatório para qualquer criação/edição/render de vídeo com HyperFrames.
- `/palmier-pro` — quando usar o editor de timeline visual do Palmier Pro em vez das skills de código (só localmente, macOS).

## Atualizar skills

```bash
npx skills update
```

## Licença

MIT — ver [LICENSE](LICENSE).
