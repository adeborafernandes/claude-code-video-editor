# Safe zones por plataforma (vertical, 1080×1920)

Defaults pra usar em `/brand-setup` quando o usuário não tiver um print de referência do próprio
canal. Se tiver print, o print vence — cada UI de app muda com frequência (3-5x/ano), então uma
referência real e recente é mais confiável que qualquer tabela.

| Plataforma | Zona morta topo | Zona morta base | Zona morta direita | Faixa recomendada pra legenda |
|---|---|---|---|---|
| **TikTok** | ~130-150px (~7-8%) — busca, relógio/bateria | ~300-400px (~16-21%) — legenda nativa, @usuário, música | ~140-180px (~13-17%) — curtir/comentar/salvar | 62-78% da altura |
| **Instagram Reels** | ~200px (~10%) — nome da conta, seguir | ~310px (~16%) — legenda nativa, áudio | ~84px direita / ~270px esquerda em telas maiores | 55-75% da altura |
| **YouTube Shorts** | ~120px (~6%) | ~300px (~16%) — sem CTA/marca nessa faixa | mínimo, mas evitar os últimos ~10% | 55-75% da altura |
| **Universal (poste nas três sem reeditar)** | 150px | 400px (a mais restritiva, do TikTok) | 180px | ~62-73% — a interseção das três |

Regra prática: se o vídeo vai pra mais de uma plataforma sem reedição por formato, use a linha
"Universal" — ela é a interseção das três zonas mortas mais restritivas.

## YouTube padrão (16:9, não vertical)

Não tem o mesmo tipo de UI sobreposta que os formatos verticais. Zona de atenção aqui é outra:
os últimos ~15% inferior-direito ficam cobertos pelo player em hover (barra de progresso,
controles); evite texto essencial nesse canto se o vídeo for assistido em desktop.

## Como usar isso na entrevista do `/brand-setup`

1. Pergunte a plataforma principal do usuário.
2. Se ele tiver um print de um vídeo dele já publicado com legenda visível, peça — meça a
   posição da legenda no print (proporção da altura, não pixel absoluto, pra funcionar em
   qualquer resolução) e use isso em vez da tabela.
3. Sem print, use a linha da plataforma escolhida (ou "Universal" se postar em mais de uma).
4. Escreva o resultado em `brand.md` na seção "Posicionamento da legenda" como uma faixa
   percentual da altura do frame — é isso que `/embedded-captions` e `/hyperframes` conseguem
   aplicar independente da resolução final.
