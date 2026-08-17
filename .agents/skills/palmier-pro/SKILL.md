---
name: palmier-pro
description: >
  Roteia edição para o Palmier Pro (palmier.io) — editor de vídeo NLE nativo de macOS, com
  timeline visual, controlado por agentes via MCP local. Use quando o usuário quiser editar
  numa timeline visual de verdade (trim, keyframes, color grading), misturar footage real com
  clipes gerados por IA (Seedance, Kling, Nano Banana Pro, FLUX etc.) no mesmo timeline, gravar
  um edit manual como "Skill" reaproveitável para vídeos recorrentes (anúncios, formatos
  padronizados), ou exportar para Premiere/DaVinci Resolve/Final Cut via XML. SÓ funciona
  quando o Claude Code está rodando LOCALMENTE num Mac com Apple Silicon (macOS 26 Tahoe+) e o
  app Palmier Pro aberto — não funciona neste container remoto/cloud. Para pipeline
  headless/reprodutível sem GUI (corte, motion graphics, composição por código), use
  `/clean-cut`, `/hyperframes` ou `/remotion-create` em vez disso.
---

# palmier-pro

[Palmier Pro](https://www.palmier.io/) é um editor de vídeo NLE nativo (Swift, GPLv3, open
source) construído para ser operado por agentes: expõe um servidor MCP local em
`http://127.0.0.1:19789/mcp` enquanto está rodando, e o agente inspeciona o projeto e edita a
timeline diretamente — trim, reorder, geração de footage — com o usuário revisando/desfazendo
tudo dentro do app.

Diferente do `clean-cut` e das skills `/hyperframes` / `/remotion-*` já neste repo (que são
100% código, headless, rodam em qualquer container), o Palmier Pro é um **app gráfico de
macOS**. A configuração MCP dele já está neste repo (`.mcp.json` na raiz), mas ela só tem efeito
quando:

1. O Claude Code está rodando **localmente**, num Mac com Apple Silicon (macOS 26 Tahoe ou
   superior) — não nesta sessão remota.
2. O app **Palmier Pro está aberto**, com um projeto carregado.

Rodando neste ambiente (cloud, sem GUI), o servidor MCP em `127.0.0.1:19789` não existe — as
ferramentas do Palmier simplesmente não aparecem. Isso é esperado, não um erro de configuração.

## Quando usar Palmier Pro em vez das skills de código

| Situação | Skill |
|---|---|
| Corte editorial de gravação crua (transcrever, remover retake/silêncio) | `/clean-cut` |
| Motion graphics, overlays, legendas, composição do zero — reprodutível, sem GUI | `/hyperframes` |
| Composição React programática | `/remotion-create` |
| Editar numa timeline visual de verdade, misturar footage real + clipes gerados por IA (Seedance/Kling/FLUX) lado a lado, keyframes/color grading manuais | **Palmier Pro** |
| Vídeo recorrente com o mesmo formato (ex: anúncio semanal) — gravar o edit uma vez como "Skill" do Palmier e reaplicar | **Palmier Pro** |
| Entregar para outro editor humano em Premiere/DaVinci/Final Cut | **Palmier Pro** (exporta XML) |

## Instalação (na máquina do usuário, macOS)

```bash
# baixar o app
open https://github.com/palmier-io/palmier-pro/releases/latest/download/PalmierPro.dmg
```

Depois de instalar e abrir o app uma vez (ele sobe o servidor MCP local em
`http://127.0.0.1:19789/mcp`), registre esse servidor no seu agente:

- **Rodando dentro deste repositório**, na maioria dos agentes o servidor já é detectado
  sozinho: `.mcp.json` (formato Claude Code) e `mcp.json` (formato [Agent
  Plugins](https://agent-plugins.org/), lido por Codex, Cursor e outros) já estão na raiz. Só
  abra o Palmier Pro antes de iniciar a sessão local — não precisa registrar nada.
- **Claude Code**, fora deste repo ou pra confirmar manualmente: `claude mcp add --transport http palmier-pro http://127.0.0.1:19789/mcp`
- **Outro agente** (Gemini CLI, Codex CLI, Antigravity...): consulte a documentação dele pra
  registrar um servidor MCP HTTP com a URL acima — o mecanismo muda por ferramenta, mas todas
  que suportam MCP têm um jeito de apontar pra uma URL local.

## Antes de usar as ferramentas de timeline do Palmier num projeto já aberto

Se o pedido for genérico ("edita esse vídeo") e o clipe carregado no projeto for gravação crua
não editada (um clipe longo, sem cortes, com pausas/repetições de fala) — **não** edite direto
pela timeline do Palmier. Rode `/clean-cut` nele primeiro para gerar `master.mp4` +
`edited-transcript.json`, e só então importe o resultado como mídia no projeto. Ver a seção
"Se o Palmier Pro já estiver aberto com o vídeo carregado" em `/clean-cut` para o passo a passo.
Se o clipe já está cortado/editado, siga direto pela timeline do Palmier.

## Color grading — opcional, sob pedido explícito

Cor e luz da imagem não fazem parte da sequência operacional padrão deste repo (ver
`CLAUDE.md`) — nenhuma skill aplica grading sozinha. Se o usuário pedir explicitamente:

1. **Não aplique color grading sem pedido explícito.** Diferente do corte/legenda/overlay, isso
   não é "mandatory first step" de nada — só entra quando pedido especificamente.
2. **Descubra as ferramentas reais antes de agir.** As ferramentas de color grading do Palmier
   Pro vêm do servidor MCP dele (`http://127.0.0.1:19789/mcp`), que só existe quando o app está
   aberto localmente — não há schema fixo documentado aqui. Rode `/mcp` na sessão local pra ver
   os nomes exatos das ferramentas de grading disponíveis antes de chamar qualquer uma.
3. **Peça direção antes de aplicar.** `brand.md` cobre tom de voz e tipografia, não cor de
   imagem — não existe preferência de "look" registrada por padrão. Pergunte o que a pessoa quer:
   um LUT específico, mais quente/frio, mais contraste, ou só corrigir exposição/white balance
   de um clipe malfeito.
4. **Comece pequeno.** Um clipe, um ajuste, comparar antes/depois dentro do próprio Palmier
   (que permite desfazer) antes de considerar aplicar num vídeo inteiro.
5. **Se o resultado for aprovado e virar prática recorrente**, documentar a preferência de
   "look" (LUT, paleta, contraste) em `brand.md` como uma nova seção.

## Handoff com o resto do pipeline

`clean-cut` (corte) → footage real limpo. `/hyperframes` ou `/remotion-*` (visuais gerados por
código) → clipes/overlays prontos. Ambos os resultados podem ser importados como mídia dentro de
um projeto do Palmier Pro para a montagem final numa timeline visual, mistura com geração de IA
in-app, e export para os outros NLEs — mas essa etapa final só roda localmente, com o app aberto.
