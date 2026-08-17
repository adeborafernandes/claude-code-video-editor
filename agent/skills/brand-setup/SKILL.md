---
name: brand-setup
description: >
  MANDATORY FIRST RUN: entrevista o usuário e gera `brand.md` — o contrato de tom de voz e
  tipografia que toda skill de vídeo deste repo lê antes de escrever texto na tela. Use
  automaticamente antes de rodar `/clean-cut`, `/hyperframes`, `/embedded-captions`,
  `/remotion-*`, `/talking-head-recut` ou qualquer edição no Palmier Pro se `brand.md` ainda
  tiver o aviso "⚠️ TEMPLATE — NÃO CUSTOMIZADO" no topo. Também use quando o usuário pedir
  explicitamente para "configurar minha marca", "definir meu tom de voz", "customizar minha
  identidade" ou "trocar minha fonte/legenda". Sem isso, nenhuma legenda/hook/título gerado
  tem voz definida — é o único passo que não pode ser pulado nem em pedidos genéricos.
---

# brand-setup

Este repo é um template open source: o `brand.md` que vem no clone é um placeholder, não a voz
de ninguém. Antes de editar qualquer vídeo pela primeira vez, alguém precisa customizar a
própria identidade — é isso que esta skill faz, numa entrevista curta.

## Quando rodar

- **Automaticamente**, antes da primeira ação de qualquer outra skill de vídeo neste repo, se
  `brand.md` ainda tiver o aviso `⚠️ TEMPLATE — NÃO CUSTOMIZADO` no topo (ver `CLAUDE.md`, que
  faz esse gate valer sem precisar que o usuário peça).
- **Sob pedido**, quando o usuário quiser mudar algo já configurado (trocar fonte, ajustar tom,
  adicionar uma crença nova).

## A entrevista

Pergunte em blocos pequenos — não jogue as 10 perguntas de uma vez. Se o usuário não souber
responder algo, ofereça 2-3 opções concretas em vez de deixar em aberto; um brand.md com
respostas genéricas ("tom profissional") vale menos que um com exemplos reais.

1. **Identidade** — nome/marca, o que você faz, o que diferencia você de quem fala do mesmo
   assunto, quem é o público.
2. **Crenças** — 2 a 3 posicionamentos fixos que guiam o conteúdo, independente da tendência do
   momento. Peça pra formular como frase quotável (ex: *"X não é etapa final, é parte do
   processo desde o início"*).
3. **Tom de voz** — como soa (peça 3-5 adjetivos) e como NÃO soa (o que a pessoa odeia em
   conteúdo de outros criadores do mesmo nicho — geralmente é mais fácil responder isso primeiro
   e inferir o "como soa" por oposição).
4. **Jeito de explicar** — usa analogia? exemplo real? dado? Peça 1-2 exemplos reais já usados,
   se houver.
5. **O que nunca entra** — frases/formato que a pessoa recusaria usar (gatilho de escassez,
   hype, jargão vazio, drama de abertura, etc.) — de novo, exemplos concretos > regra abstrata.
6. **Tipografia na tela** — fonte preferida (se não souber, sugira 2-3 fontes comuns e
   contrastantes: uma serifada, uma sans, uma mono) e se quer contorno/stroke atrás do texto.
7. **Plataforma e posicionamento de legenda** — TikTok, Reels, Shorts ou YouTube define a safe
   zone. Se o usuário tiver um print de um vídeo dele já publicado com legenda, peça — é a
   forma mais rápida de acertar a faixa vertical certa (ver `references/safe-zones.md`). Sem
   print, use os defaults documentados lá pra a plataforma escolhida.
8. **Banco de temas** (opcional) — assuntos que a pessoa cobre com frequência ou tem repertório
   próprio. Pode ficar vazio e crescer com o tempo.

## Gerar o arquivo

Copie `references/brand.template.md` para `brand.md` na raiz do repo, preenchendo cada
`{{PLACEHOLDER}}` com as respostas da entrevista — não deixe nenhum `{{...}}` sem substituir.
Remova o aviso de template do topo do arquivo final.

Depois de gerar, mostre o `brand.md` completo pro usuário e pergunte se está no tom certo antes
de considerar a etapa concluída — é mais barato ajustar aqui do que descobrir errado numa
legenda já renderizada.

## Depois do setup

Com `brand.md` customizado, o usuário pode seguir a sequência normal do pipeline — ver
`CLAUDE.md` na raiz. Esta skill pode ser rodada de novo a qualquer momento pra atualizar a
identidade; nesse caso, edite `brand.md` diretamente em vez de regenerar do zero (preserva
ajustes manuais que o usuário tenha feito depois da primeira geração).
