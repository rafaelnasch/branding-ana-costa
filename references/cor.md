# Cor

Fonte: `tokens.json` (valores) e manual, seções 09 a 11. Toda cor de peça sai daqui; HEX fora desta lista não é da marca.

## As dez cores e as três derivadas

| Cor | HEX | Variável CSS | RGB | CMYK (FOGRA39) | Proporção | Uso |
|---|---|---|---|---|---|---|
| Sálvia Ana | `#63AF9C` | `--cor-salvia` | 99 175 156 | 62 9 44 2 | 28% | Cor-assinatura e superfície dominante: avatar, capas de destaque, faixas, blocos de cor, capa de post. Nunca para texto sobre claro. |
| Algodão | `#F2F0EB` | `--cor-algodao` | 242 240 235 | 6 5 9 0 | 26% | Fundo claro neutro (derivado do fundo dos ensaios dela, #ECE9E4). Leitura longa. |
| Bruma | `#D8ECE5` | `--cor-bruma` | 216 236 229 | 18 2 13 0 | 16% | Sálvia clareada: segunda superfície, modo Gestação, sub-marca Bem Nutrida. |
| Mar Fundo | `#103A40` | `--cor-mar` | 16 58 64 | 85 49 50 60 | 16% | Símbolo, nome, títulos e base escura. Verde-mar azulado (não é o verde-floresta). |
| Sálvia Funda | `#2F6E60` | `--cor-salvia-funda` | 47 110 96 | 77 31 58 29 | 6% | Verde de texto, botões e links sobre claro; descritor do logotipo. |
| Pedra | `#E4E0D8` | `--cor-pedra` | 228 224 216 | 13 11 16 0 | 4% | Cartões e fundos de apoio neutros. |
| Caramelo | `#C99A68` | `--cor-caramelo` | 201 154 104 | 19 39 61 8 | 2% | O ponto de chegada. Um ponto caramelo por peça, e o do logotipo conta. Nunca texto sobre claro. |
| Caramelo Tostado | `#8A5A2E` | `--cor-caramelo-tostado` | 138 90 46 | 33 58 82 33 | 1% | Texto quente, frase de apoio e links sobre claro. |
| Ouro Velho | `#C9B583` | `--cor-ouro-velho` | 201 181 131 | 22 24 52 5 | 0,5% | Acento do modo 40+ e menopausa, sempre sobre Mar Fundo. Dourado acinzentado, longe da mostarda. |
| Grafite Quente | `#2B2724` | `--cor-grafite` | 43 39 36 | 65 60 60 74 | 0,5% | Texto corrido longo. |

Derivadas, só para os usos indicados:

| Cor | HEX | Variável CSS | RGB | CMYK | Uso |
|---|---|---|---|---|---|
| Sálvia Clara | `#A9D3C6` | `--cor-salvia-clara` | 169 211 198 | 38 3 27 0 | Traço do padrão de fundo sobre Algodão ou Bruma. Só gráfico. |
| Mar Médio | `#2A5C63` | `--cor-mar-medio` | 42 92 99 | 79 41 45 36 | Traço do padrão de fundo sobre Mar Fundo. Só gráfico. |
| Mar Superfície | `#17464D` | `--cor-mar-superficie` | 23 70 77 | 84 47 47 51 | Cartões e caixas dentro do modo 40+ (sobre Mar Fundo). |

**Proporção de uso:** Sálvia Ana domina (cerca de 28%), Algodão para ler (26%), Bruma e Mar Fundo (16% cada), Sálvia Funda (6%), Pedra (4%), Caramelo (2%), Caramelo Tostado (1%), Ouro Velho e Grafite Quente (0,5% cada). O verde dela ocupa as áreas grandes; o quente é só um ponto.

## Um ponto quente por peça (TRAVADA)

O Caramelo é o ponto de chegada. **Um ponto caramelo por peça, e o do logotipo conta.** Se a peça já tem o logotipo ou o símbolo colorido, Rota, marcadores e pílulas usam ponto Sálvia Funda (fundo claro) ou Sálvia Ana (fundo escuro): arquivos `rota-divisor-salvia.svg` e `rota-divisor-curto-salvia.svg`. O padrão de fundo nunca usa caramelo. Pranchas de apresentação da marca não contam como peça.

## Contraste (fórmula de luminância das diretrizes de acessibilidade web)

Mínimo para texto: 4,5 para 1. Entre 3 e 4,5: só texto de 24 px ou mais (19 px em negrito) e elementos gráficos. Abaixo de 3: só decorativo.

| Par | Razão | Nível |
|---|---|---|
| Mar Fundo sobre Algodão | 10,84 | AAA |
| Grafite Quente sobre Algodão | 13,0 | AAA |
| Sálvia Funda sobre Algodão | 5,24 | AA |
| Caramelo Tostado sobre Algodão | 5,15 | AA |
| Mar Fundo sobre Bruma | 10,02 | AAA |
| Sálvia Funda sobre Bruma | 4,84 | AA |
| Mar Fundo sobre Sálvia Ana | 4,79 | AA |
| Mar Fundo sobre Pedra | 9,38 | AAA |
| Caramelo Tostado sobre Pedra | 4,45 | só texto grande (24 px ou mais, ou 19 px em negrito) e elementos gráficos |
| Algodão sobre Mar Fundo | 10,84 | AAA |
| Bruma sobre Mar Fundo | 10,02 | AAA |
| Sálvia Ana sobre Mar Fundo | 4,79 | AA |
| Caramelo sobre Mar Fundo | 4,88 | AA |
| Ouro Velho sobre Mar Fundo | 6,13 | AA |
| Algodão sobre Mar Superfície | 9,13 | AAA |
| Ouro Velho sobre Mar Superfície | 5,16 | AA |
| Algodão sobre Sálvia Funda | 5,24 | AA |
| Algodão sobre Sálvia Ana | 2,26 | só decorativo (nunca texto nem informação) |
| Caramelo sobre Algodão | 2,22 | só decorativo (nunca texto nem informação) |
| Caramelo sobre Sálvia Ana | 1,02 | só decorativo (nunca texto nem informação) |
| Algodão sobre Caramelo Tostado | 5,15 | AA |
| Mar Fundo sobre Ouro Velho | 6,13 | AA |
| Sálvia Funda sobre Mar Fundo | 2,07 | só decorativo (nunca texto nem informação) |

**Consequências práticas**

- Sobre Sálvia Ana, símbolo e texto saem em **Mar Fundo** e o ponto em **Algodão**. Nunca branco, nunca caramelo.
- **Proibido:** Caramelo sobre Sálvia Ana (1,02 para 1, o ponto some); Sálvia Ana ou Caramelo como texto sobre claro (cerca de 2,3 para 1); Sálvia Funda sobre Mar Fundo (2,1 para 1).
- Botão padrão: Sálvia Funda com texto Algodão (5,2 para 1). No modo 40+: **Ouro Velho com texto Mar Fundo** (6,1 para 1).
- Links sobre claro: Sálvia Funda ou Caramelo Tostado, sempre sublinhados.
- Texto corrido longo: Grafite Quente sobre Algodão (13 para 1).

## Modos por fase

O símbolo é sempre o mesmo. Mudam a temperatura e a cor do ponto. No site: `data-fase="gestacao" | "pos-parto" | "40-mais"` no contêiner; os componentes usam `--fundo`, `--superficie`, `--texto`, `--titulo`, `--acento`, `--ponto`.

| Modo | Fundo | Superfície | Texto e símbolo | Ponto e acento | Regra extra |
|---|---|---|---|---|---|
| Gestação · claro | Bruma | Algodão | Mar Fundo | Sálvia Funda | Luminoso e leve |
| Pós-parto e amamentação · morno (padrão) | Algodão | Pedra | Mar Fundo | Caramelo (acento Caramelo Tostado) | Acolhedor |
| 40+ e menopausa · profundo | Mar Fundo | Mar Superfície | Algodão | Ouro Velho | Corpo de texto 2 px maior em todas as peças; foto sem gestação; botão Ouro Velho com texto Mar Fundo |

Nas redes, o modo identifica a série sem precisar de título. Como escolher: a peça fala com uma mulher só; a fase dela decide o modo. Conteúdo de rotina para todas usa o modo pós-parto (padrão).

## Cor no papel

CMYK convertido pelo perfil ISO Coated v2 300% (FOGRA39, papel revestido), intenção colorimétrica relativa com compensação de ponto preto. Nenhuma cor passa de 260% de cobertura. Em papel não revestido, a gráfica converte os valores RGB com o perfil dela (por exemplo, PSO Uncoated v3, FOGRA52). O Pantone mais próximo é escolhido pela gráfica no leque físico, com prova impressa da Sálvia Ana e do Caramelo lado a lado (pendência P5). Sombras são sempre puxadas para o Mar Fundo (`rgba(16,58,64,...)`), nunca preto puro.

## Cor em dados e gráficos

Série principal Sálvia Funda, segunda série Mar Fundo, destaque único Caramelo (um ponto só), apoio Sálvia Clara. Nunca vermelho de alerta: "não" e "deixo" vão em Mar Fundo. Rótulo direto na série, sem legenda separada quando der.

## Por que não é a rota reprovada

A rota reprovada tinha papel amarelado, verde-floresta, terracota e Fraunces. Aqui a superfície dominante é a Sálvia Ana, o claro é o Algodão neutro (tirado do fundo dos ensaios dela), a base escura é verde-mar azulado, não há terracota e a serifa é a Literata. Proibido usar verde-limão, rosa-bebê dominante ou as paletas reprovadas.
