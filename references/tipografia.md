# Tipografia

Fonte: `tokens.json` (`tipografia`) e manual, seções 12 e 13. As duas famílias são gratuitas, de licença aberta (OFL), e estão em `assets/fontes/` (`.ttf` para computador, `assets/fontes/web/*.woff2` para o site).

## As duas fontes

| Papel | Fonte | Arquivos | Regra |
|---|---|---|---|
| Nome, títulos, citações, a voz da Ana | **Literata** (variável: tamanho óptico e peso) | `Literata[opsz,wght].ttf`, `Literata-Italic[opsz,wght].ttf` | Títulos com tamanho óptico de 48 a 72 e peso de 560 a 600. **Só a partir de 24 px.** O itálico é a voz da Ana (citação, "Bem Nutrida", frase-mãe) |
| Texto, botões, rótulos, legendas, descritor | **Atkinson Hyperlegible Next** (desenhada para baixa visão: I, l e 1, O e 0 não se confundem) | `AtkinsonHyperlegibleNext[wght].ttf`, itálico e instâncias Regular, Medium, SemiBold, Bold | Pesos 400, 500, 600 e 700. Tudo abaixo de 24 px |

As instâncias `Literata-Display-Assinatura*.ttf` são as do logotipo: não use para compor o nome, que é sempre arquivo.

## Números: sempre na Literata (TRAVADA)

A Atkinson desenha o zero cortado (Ø) e não tem alternativa. "40+", o nome do segmento mais importante, sairia "4Ø+".

- **Web:** a família `Ana Numerais` (Literata limitada aos algarismos 0 a 9 por `unicode-range`) vem antes da Atkinson em `--fonte-texto` no `tokens.css`. Todo número sai com zero aberto, sem trabalho manual.
- **Rótulo de fase e destaque:** classe `.num-fase` (Literata 600, algarismos alinhados). Ex.: "40+", "Semana 1".
- **Canva, CapCut, editor de story e arte vetorizada:** componha "40+", datas e medidas em Literata; o "+" pode seguir na Atkinson. Confira a olho antes de exportar.

## Escala para telas

| Nível | Computador | Celular | Fonte e peso | Entrelinha |
|---|---|---|---|---|
| Display | 72 px | 44 px | Literata 580 | 1,06 |
| Título 1 | 52 px | 36 px | Literata 580 | 1,1 |
| Título 2 | 38 px | 29 px | Literata 580 | 1,15 |
| Título 3 | 26 px | 22 px | Literata 560 | 1,25 |
| Corpo | 18 px | 17 px | Atkinson 400 | 1,65 |
| Corpo no modo 40+ | 20 px | 19 px | Atkinson 400 | 1,65 |
| Botão | 17 px | 17 px | Atkinson 600, altura mínima de 48 px | |
| Rótulo | 14 px | 14 px | Atkinson 600, caixa alta, entreletra de 14% | |

Variáveis: `--texto-display`, `--texto-h1`, `--texto-h2`, `--texto-h3`, `--texto-corpo`, `--texto-botao`, `--texto-rotulo`, `--texto-legenda` (15 px), `--entrelinha-corpo`, `--tracking-rotulo`, `--peso-titulo` (580), `--opsz-titulo` (60). Coluna de leitura de até 44rem (cerca de 70 caracteres).

## Escala para redes (arte de 1080 px de largura)

| Elemento | Tamanho | Fonte |
|---|---|---|
| Título de post e carrossel | 88 px, até 3 linhas | Literata 580, entrelinha 1,08 |
| Título de story e capa de Reels | 92 px, até 3 linhas | Literata 580 |
| Subtítulo | 46 px | Atkinson 500 ou Literata itálico (frase da Ana) |
| Texto | 36 px (mínimo 32 px), até 5 linhas por cartão | Atkinson 400, entrelinha 1,35 |
| Rótulo e botão | 26 a 32 px | Atkinson 600, rótulo em caixa alta |
| Assinatura e CRN no rodapé | mínimo de 28 px | Atkinson |
| Legenda queimada no vídeo | 56 a 64 px | Atkinson 600 |

No story e no Reels, nada essencial nos 250 px de cima nem nos 380 px de baixo (480 px em anúncio). Detalhe em `canais-e-medidas.md`.

## Escala para impresso (1 pt = 0,35 mm)

| Nível | Tamanho | Fonte |
|---|---|---|
| Título de capa | 28 a 36 pt | Literata 580 |
| Título de página | 24 a 26 pt | Literata 580 |
| Subtítulo | 14 pt | Atkinson 600 (Literata só a partir de 18 pt) |
| Texto do plano alimentar e de materiais | 12 pt, entrelinha 1,5 | Atkinson 400 |
| Rótulo | 8,5 a 9 pt | Atkinson 600, caixa alta, entreletra de 14% |
| Rodapé, CRN e notas | 9 pt (mínimo) | Atkinson 400 |
| Cartão de visita 90 × 50 mm | 8,5 pt (mínimo 8) | Atkinson; o nome vem do arquivo do logotipo |

Margem mínima de 15 mm em folha A4. O plano alimentar é lido de perto e preso na geladeira: 12 pt é de propósito.

## Hierarquia

No máximo cinco níveis por peça, sempre nesta ordem: rótulo (o assunto), título (a ideia), chamada (uma frase), texto (ensina) e botão (o próximo passo). Um título por tela; o título tem pelo menos o dobro do tamanho do texto. Uma ideia por título; no máximo uma palavra em caixa alta por peça (como a Ana já faz: "basta ser CONSISTENTE"). Título sem travessão. Itálico da Literata só para a voz da Ana ou para "Bem Nutrida", nunca para ênfase genérica.

## Fallbacks

Site: `'Literata', Georgia, serif` e `'Ana Numerais', 'Atkinson Hyperlegible Next', system-ui, sans-serif`. E-mail (os aplicativos não carregam fonte): Literata com Georgia de reserva para o nome e Arial para o texto. As duas famílias também estão no Google Fonts (`Literata` e `Atkinson Hyperlegible Next`).
