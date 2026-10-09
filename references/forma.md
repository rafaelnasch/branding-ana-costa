# Forma: a Rota, ícones, grade, raios, sombras e movimento

Fonte: especificação Rota ap. v1.2 (seção 6), `tokens.json` (`forma_assinatura`, `espacamento_px`, `raio_px`, `sombras`, `movimento`) e manual, seções 14, 15 e 17. Arquivos em `assets/forma/`.

## A Rota

O gesto da descendente do p aberto em linha: **corre reta, mergulha uma vez, sobe e pousa no ponto.** Desenhada com a mesma pena do símbolo: plano fino, descida encorpada, ponta que afina antes do ponto.

Regras (TRAVADAS):

1. Toda rota termina num ponto. Linha sem ponto não é da marca.
2. Um mergulho por rota. Nunca onda contínua.
3. **Um ponto caramelo por peça, e o do logotipo conta.** Peça que já tem o logotipo ou o símbolo colorido usa os arquivos `-salvia` (ponto Sálvia Funda sobre claro; Sálvia Ana sobre escuro). O padrão de fundo nunca usa caramelo.
4. A pena não muda: não engrosse, não contorne, não estique a altura. Aumente ou diminua a rota inteira.
5. Sempre o arquivo. Não redesenhe com a ferramenta de linha do Canva.
6. Um divisor por tela, no máximo.

| Peça | Arquivo | Uso |
|---|---|---|
| Divisor, fundo claro | `rota-divisor.svg` · `rota-divisor-curto.svg` | Entre seções do site, capa de carrossel, plano alimentar |
| Divisor sem caramelo | `rota-divisor-salvia.svg` · `rota-divisor-curto-salvia.svg` | Peça que já tem o logotipo colorido; assinatura de e-mail |
| Divisor, fundo escuro | `rota-divisor-sobre-escuro.svg` | Traço Algodão sobre Mar Fundo |
| Seta de chamada | `rota-seta.svg` · `rota-seta-sobre-escuro.svg` | Dentro do botão principal: 40 px de largura para texto de 17 px; anda 3 px no passar do mouse. Uma por tela |
| Régua de fases | `regua-fases.svg` · `-modo-gestacao` · `-modo-40mais` | Gestação · Pós-parto · Amamentação · 40+ · Menopausa, com o ponto maior na fase atual. Substitui fita, balança e qualquer marca de medida. A partir de 700 px de largura; menor que isso, botões de fase (pílulas de 44 px de altura com ponto de 9 px na cor da fase) |
| Moldura em arco | `moldura-arco-mascara.svg` · `moldura-arco-contorno.svg` | Recorte padrão das fotos reais |
| Padrão de fundo | `padrao-fundo-claro.svg` · `padrao-fundo-escuro.svg` · módulos `padrao-modulo-*.svg` | Textura discreta de capas, papelaria e fundos de vídeo. Nunca atrás de texto longo |

Padrão claro: traço Sálvia Clara e ponto Sálvia Ana sobre Algodão. Padrão escuro: traço Mar Médio e ponto Sálvia Funda sobre Mar Fundo. No site: `background:url(assets/forma/padrao-modulo-claro.svg) 0 0/320px 96px`. No Canva: envie o `padrao-fundo-claro.svg` inteiro (1200 × 720) e amplie até cobrir; não gire nem mude a cor.

## A moldura em arco

Único recorte de foto da marca (o círculo é só do avatar). Topo com raio igual à metade da largura, base reta (arte de rede) ou com 14 px de raio (site). Proporção 400 × 520 (1 para 1,3), rosto no terço de cima com ar acima da cabeça. Atrás, de preferência, um arco Sálvia Ana maior (6% a mais de cada lado), como uma porta aberta; no modo 40+, arco Mar Médio sobre Mar Fundo. Nunca cortar testa ou cabelo.

## Ícones

**Destaques (8, em `assets/forma/icones-destaques/`):** grade de 48 × 48 com 4 unidades de respiro, a mesma pena do símbolo, sempre com um ponto em círculo exato, até 40 nós por traço. Capas: fundo Sálvia Ana, traço Mar Fundo, ponto Algodão, ícone ocupando 62% do quadro. PNG de 1080 × 1080 e 1080 × 1920 em `icones-destaques/png/`.

| Destaque | Desenho |
|---|---|
| Comece aqui | A rota parte do ponto e vira seta |
| Consulta | Tela de atendimento online com o ponto |
| Comunidade | Três pessoas, a do centro com o ponto |
| Gestação | Broto de duas folhas de pena, o ponto como botão no alto |
| Pós-parto | A rota desce fundo e volta à mesma altura, onde pousa o ponto |
| 40+ | Corre, mergulha uma vez e sobe por um trecho longo até um ponto mais alto |
| Receitas | Livro aberto, o ponto na página |
| Depoimentos | Duas aspas iguais e o ponto final separado |

Abaixo de 24 px o ponto some: use só o texto. Gestação e Comunidade dependem da aprovação da Ana (P8); se um ícone não for entendido a 64 px sem rótulo, ele sai do destaque.

**Interface:** traço de 1,8 px em grade de 24 × 24, pontas e cantos redondos, `currentColor`, sem ponto (o ponto aparece ao lado do item ativo, na cor do modo). Biblioteca de traço fino e cantos redondos (Lucide, por exemplo) ajustada para 1,8 px. A seta é sempre `rota-seta.svg`. Área de toque de pelo menos 44 × 44 px.

**Nunca:** folha, maçã, balança, fita métrica, silhueta, mão na barriga, pezinho de bebê, lótus, talher, âncora, leme, bússola.

## Grade e espaço

Todo espaço é múltiplo de 4 px: `--esp-1` a `--esp-10` = 4, 8, 12, 16, 24, 32, 48, 64, 96 e 128 px. Nada no meio. Arte de rede de 1080 px: margem lateral de 80 px.

## Raios e sombras

Raios: 8 px (`--raio-p`), 14 px (`--raio-m`), 24 px (`--raio-g`), pílula nos botões (`--raio-pilula`), arco nas fotos. Sombras sempre puxadas para o Mar Fundo, nunca preto puro: `--sombra-suave` e `--sombra-cartao`.

## Movimento

- Curva "maré": `cubic-bezier(.33,0,.15,1)` (`--mare`). Durações: 160 ms (rápido), 240 ms (base), 480 ms (entrada), 1200 ms (traço).
- **Assinatura:** o traço da Rota se desenha da esquerda para a direita em 1,2 s e o ponto pousa por último, com leve escala de 0,6 para 1 em 240 ms. Abre Reels e faz transições do site.
- No vídeo, a Rota nunca atrasa o gancho: entra por cima enquanto a Ana já fala (faixa de 0 a 0,2 s, traço de 0,2 a 1,4 s, ponto de 1,4 a 1,64 s, corte seco aos 3 s; em 30 quadros por segundo, quadros 6 a 49). Fechamento com a assinatura em no máximo 1 segundo.
- Código pronto para o site: a Rota é forma cheia, então se revela com `clip-path:inset(0 100% 0 0)` animado até `inset(0 0 0 0)` em `var(--t-traco) var(--mare)`, e o ponto entra com `opacity` e `scale(.6)` para 1 depois do traço. Manual, seção 17.
- Com "reduzir movimento" ligado no aparelho, o traço aparece pronto, sem animação.
- Nada de giro, brilho, cortina ou quique.
