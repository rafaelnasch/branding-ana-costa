---
name: branding-ana-costa
description: "Identidade da nutricionista Ana Paula Costa (gestação, pós-parto, 40+ e menopausa; atende online, a partir do Rio de Janeiro), sistema Rota ap. v1.2. Use em todo material: post, carrossel, story, Reels, TikTok, destaque, anúncio, site, página de venda, e-mail, WhatsApp, plano alimentar, PDF, cartão e vídeo. Gatilhos: ana costa, ana paula costa, nutri ana, padrão da ana, rota ap, bem nutrida, semana bem nutrida, comunidade bem nutrida, nutrição por fases, avaliação da fase. Traz: monograma ap. em traço de pena com o ponto de chegada; Sálvia Ana domina, Algodão para ler, Mar Fundo nos títulos, um único ponto Caramelo por peça (o do logotipo conta); modos por fase (gestação clara, pós-parto morna, 40+ profunda com Ouro Velho); Literata nos títulos e números, Atkinson Hyperlegible Next no texto; a Rota (corre, mergulha uma vez, pousa no ponto); fotos reais da Ana sozinha; voz acolhedora e firme, sem alimento vilão; regras do conselho (CRN visível, sem antes e depois, sem preço de consulta na divulgação)."
---

# /branding-ana-costa · A marca da Ana Paula Costa, Nutricionista

Sistema **Rota ap.** (nome de trabalho; nunca aparece em peça pública). O **a** e o **p** de Ana Paula escritos com a mesma pena: a descendente do p mergulha abaixo da linha, vira para a frente e aponta para o **ponto de chegada**. O mergulho é a virada de rota dela (aos 30, da Marinha Mercante para a Nutrição); o ponto é a chegada e o ponto final do jeito de falar, acolhedor e firme.

Ideia central (é copy): ***cada fase pede outro prato.***

Quatro regras de bolso: **o verde dela domina** (Sálvia Ana nas áreas grandes, Algodão para ler), **um ponto quente por peça** (o Caramelo, e o do logotipo conta), **a fase decide o modo** (gestação clara, pós-parto morna, 40+ profunda) e **o caminho, nunca o ponto de chegada do corpo** (processo, nunca quilos, prazo, cura ou antes e depois).

**Abra PRIMEIRO:** o manual vivo em 8 partes, seções 01 a 25, [brand-book.html](https://rafaelnasch.github.io/branding-ana-costa/brand-book.html) (cada seção abre por âncora: `brand-book.html#sNN` ou `#sNN-N`, ex.: `#s20-3`). Pedidos prontos por público: [guia-de-uso.html](https://rafaelnasch.github.io/branding-ana-costa/guia-de-uso.html). Trechos para copiar (logotipo em código, assinaturas, bios, NAP, CRN, rodapé, avisos): [`lockup.html`](lockup.html). Modelos: [`kit-social.html`](https://rafaelnasch.github.io/branding-ana-costa/kit-social.html) e [`kit-video.html`](https://rafaelnasch.github.io/branding-ana-costa/kit-video.html). Valores: [`tokens.css`](tokens.css) e [`tokens.json`](tokens.json).

**Fontes desta skill.** Especificação Rota ap. v1.2 (outubro de 2026), capítulos de voz, conformidade e redes do manual, pesquisa de mercado e do perfil dela (outubro de 2026). O que depende da Ana aparece como **"em confirmação"** com a pendência **Pn** (lista em [`references/pendencias.md`](references/pendencias.md)). Nunca invente o dado.

**Como a skill está organizada.** Este arquivo traz o essencial. O detalhe mora em `references/` e só é aberto no passo que pede (mapa abaixo). Todo valor é conferido contra o `tokens.json`.

---

## A primeira pergunta: que peça, para qual fase, em qual canal, com qual convite?

Antes de cor, fonte ou formato, responda as quatro. Se o pedido não disser, **pergunte numa frase só** ou assuma o mais provável e diga o que assumiu.

1. **Que peça?** (post, carrossel, story, Reels, TikTok, capa, anúncio, página, e-mail, WhatsApp, plano alimentar, PDF, cartão, apresentação). Decide medida, zona segura e modelo.
2. **Para qual fase?** Gestação, pós-parto e amamentação, ou 40+ e menopausa (conteúdo de rotina para todas usa o modo pós-parto). Decide o modo de cor, a foto e as palavras.
3. **Em qual canal?** O **TikTok fala com a gestante**; o **Instagram fala com a mulher de 45+** e com a mãe no pós-parto. Decide quem a primeira frase nomeia.
4. **Qual único convite?** Grupo gratuito Comunidade Bem Nutrida, Semana Bem Nutrida (produto de entrada), guia do ferro, ou Avaliação da Fase (consulta online). **Uma peça, uma mulher, uma ideia, um convite.**

---

## Mapa: o que abrir em cada passo

| Passo | Referência | Kit ou arquivo |
|---|---|---|
| Cor, contraste, modo por fase, cor no papel | [`references/cor.md`](references/cor.md) | [`tokens.css`](tokens.css), [`tokens.json`](tokens.json) |
| Fonte, tamanho, escala de tela, rede e papel, números | [`references/tipografia.md`](references/tipografia.md) | `assets/fontes/` |
| Logotipo, versão, mínimo, sub-marca, avatar, favicon | [`references/marca.md`](references/marca.md) | [`lockup.html`](lockup.html) (grupos 02 a 04), `assets/marca/` |
| Rota, régua de fases, moldura em arco, padrão, ícones, grade, movimento | [`references/forma.md`](references/forma.md) | `assets/forma/` |
| Foto, ensaio, vídeo, legenda queimada, edição, exportação | [`references/fotografia-e-video.md`](references/fotografia-e-video.md) | `assets/fotos/catalogo.json`, `kit-video.html` |
| Copy, tom por canal, bordões, palavras, ganchos, séries | [`references/voz.md`](references/voz.md) | [`guia-de-uso.html`](guia-de-uso.html) |
| CRN, depoimento, preço, promoção, cardápio-exemplo, IA, anúncio, dados, filhos | [`references/conformidade.md`](references/conformidade.md) | [`lockup.html`](lockup.html) (grupos 08 e 09) |
| Medida e zona segura de cada rede, bios, destaques, linha editorial, calendário | [`references/canais-e-medidas.md`](references/canais-e-medidas.md) | `kit-social.html` |
| Assinatura de e-mail, WhatsApp, bios, NAP, rodapé legal | [`references/marca.md`](references/marca.md) | [`lockup.html`](lockup.html) (grupos 05 a 09), `assets/aplicacoes/assinatura-email.html` |
| Plano alimentar, cartão, papelaria | [`references/tipografia.md`](references/tipografia.md) | `assets/aplicacoes/plano-alimentar.html`, manual seção 22 |
| Algo depende da Ana | [`references/pendencias.md`](references/pendencias.md) | manual seção 25 |

---

## Onde a skill roda

- **Claude Code ou Codex com o repositório:** abra os arquivos locais; HTML de peça usa `tokens.css` e os SVG de `assets/marca/` e `assets/forma/` por caminho relativo.
- **claude.ai ou ChatGPT com o ZIP da skill:** o pacote traz `SKILL.md`, `references/`, `tokens.*`, `lockup.html`, a marca (SVG, PNG de até 1024 px, favicon) e a forma. Fotos, fontes e manual abrem pelo endereço público `https://rafaelnasch.github.io/branding-ana-costa/`.
- **Canva, CapCut e editores sem CSS:** use os PNG de 2048 px, as fontes `.ttf` de `assets/fontes/` e componha "40+", datas e medidas em Literata.

---

## As leis (TRAVADAS)

1. **O logotipo é arquivo.** Nunca digitar "Ana Paula Costa" ao lado do símbolo, nunca recompor o nome, nunca esticar, girar, contornar, sombrear ou pôr dentro de círculo desenhado.
2. **A versão segue o fundo.** Claro: `-cor`. Sálvia Ana: `-sobre-salvia` (traço Mar Fundo, ponto Algodão). Mar Fundo: `-sobre-escuro`. Uma cor: `-branco` ou `-preto`.
3. **Um ponto Caramelo por peça, e o do logotipo conta.** Com logotipo colorido, Rota e marcadores usam ponto Sálvia (arquivos `-salvia`). Caramelo sobre Sálvia Ana é proibido (1,02 para 1).
4. **A fase decide o modo.** Gestação: Bruma, ponto Sálvia Funda. Pós-parto (padrão): Algodão, ponto Caramelo. 40+: Mar Fundo, ponto e botão Ouro Velho com texto Mar Fundo, texto 2 px maior, foto sem gestação.
5. **Toda rota termina num ponto e mergulha uma vez.** Sempre o arquivo; nunca onda, nunca linha sem ponto. Um divisor por tela.
6. **Literata para dizer, Atkinson para ler.** Literata só a partir de 24 px; **todo número em Literata** (a Atkinson corta o zero: "40+" sairia "4Ø+").
7. **A mulher é sempre real.** Foto da Ana, sozinha, luz de janela, cor fiel. Nenhuma pessoa, corpo, consulta ou resultado gerado por inteligência artificial; sem mão na barriga; filhos nunca aparecem em peça da marca.
8. **Processo, nunca resultado.** CRN visível em peça profissional; zero antes e depois (inclusive da Ana); zero quilos, prazo, cura ou garantia de resultado; preço de consulta nunca na divulgação; consulta nunca em promoção ou sorteio.

---

## Cores (o essencial)

| Cor | HEX | Variável | Papel | Proporção |
|---|---|---|---|---|
| **Sálvia Ana** | `#63AF9C` | `--cor-salvia` | Cor-assinatura, superfície dominante, avatar, faixas. Nunca texto sobre claro | 28% |
| **Algodão** | `#F2F0EB` | `--cor-algodao` | Fundo claro, leitura | 26% |
| Bruma | `#D8ECE5` | `--cor-bruma` | Segunda superfície, modo Gestação, Bem Nutrida | 16% |
| **Mar Fundo** | `#103A40` | `--cor-mar` | Símbolo, nome, títulos, base escura | 16% |
| Sálvia Funda | `#2F6E60` | `--cor-salvia-funda` | Texto verde, botão, link, descritor | 6% |
| Pedra | `#E4E0D8` | `--cor-pedra` | Cartões e apoio | 4% |
| **Caramelo** | `#C99A68` | `--cor-caramelo` | O ponto. Um por peça | 2% |
| Caramelo Tostado | `#8A5A2E` | `--cor-caramelo-tostado` | Texto quente e links sobre claro | 1% |
| Ouro Velho | `#C9B583` | `--cor-ouro-velho` | Acento e botão do modo 40+, só sobre Mar Fundo | 0,5% |
| Grafite Quente | `#2B2724` | `--cor-grafite` | Texto corrido longo | 0,5% |

Derivadas, só gráficas: Sálvia Clara `#A9D3C6` (padrão sobre claro), Mar Médio `#2A5C63` (padrão sobre escuro), Mar Superfície `#17464D` (cartões no modo 40+).

Pares de texto: Mar Fundo sobre Algodão 10,8 · Grafite sobre Algodão 13,0 · Sálvia Funda sobre Algodão 5,2 · Mar Fundo sobre Sálvia Ana 4,8 · Algodão sobre Sálvia Funda (botão) 5,2 · Mar Fundo sobre Ouro Velho (botão 40+) 6,1 · Caramelo sobre Mar Fundo 4,9. Proibidos: Caramelo sobre Sálvia Ana (1,02), Sálvia Funda sobre Mar Fundo (2,1), Sálvia Ana ou Caramelo como texto sobre claro (2,3). Detalhe: `references/cor.md`.

**Modo no código:** `data-fase="gestacao" | "pos-parto" | "40-mais"` no contêiner; componentes usam `--fundo`, `--superficie`, `--texto`, `--titulo`, `--acento`, `--ponto`. Nunca HEX solto.

---

## Tipografia (o essencial)

- **Literata** (variável, tamanho óptico 48 a 72, peso 560 a 600): nome, títulos, citações; itálico = a voz da Ana e "Bem Nutrida". Só a partir de 24 px.
- **Atkinson Hyperlegible Next** (400 a 700): texto, botão, rótulo, legenda.
- Tela: display 72/44, título 52/36, 38/29, 26/22 px; corpo 18/17 px (20/19 no modo 40+), entrelinha 1,65; botão 17 px Atkinson 600 com 48 px de altura; rótulo 14 px em caixa alta, entreletra de 14%.
- Arte de 1080 px: título 88 (post) e 92 (story), texto 36 (mínimo 32), rodapé com CRN 28, legenda queimada 56 a 64.
- Papel: texto do plano alimentar 12 pt, nada abaixo de 9 pt; cartão 8,5 pt.
- Fontes: `assets/fontes/` (OFL). No site, o `tokens.css` já carrega as duas e a família `Ana Numerais`.

---

## A marca (o essencial)

| Versão | Mínimo digital | Mínimo impresso | Uso |
|---|---|---|---|
| Horizontal com descritor | 300 px | 65 mm | Documentos, plano alimentar, cartão, e-mail |
| Horizontal reduzida | 160 px | 35 mm | Topo do site, rodapés |
| Vertical (com "Gestação e saúde da mulher") | 210 px | 45 mm | Capas, apresentação, peça quadrada |
| Assinatura compacta | 230 px | 48 mm | Quando o símbolo já está na peça; vídeo |
| Sub-marcas Bem Nutrida | 260 px | 55 mm | Comunidade (fundo Bruma) e Semana (fundo Mar Fundo) |
| Símbolo | 32 px | 10 mm | Selo, carimbo, ícone |

Área de proteção: ½ x (meia altura do "a") em volta. Os PNG já trazem a margem. Avatares são quadrados opacos: a rede recorta o círculo. **Nas redes pessoais, a foto de perfil é o rosto da Ana**; o avatar com o símbolo vai no grupo, na comunidade e onde ela não aparece sozinha. Nunca juntar ao símbolo folha, maçã, fita métrica, balança, silhueta, bebê, âncora, leme ou bússola.

---

## Forma, fotografia e movimento (o essencial)

- **Rota:** `rota-divisor.svg`, `-salvia` (sem caramelo), `-sobre-escuro`, `-curto`; seta `rota-seta.svg` dentro do botão principal; régua de fases a partir de 700 px (menor: botões de fase).
- **Foto:** moldura em arco (topo com raio = metade da largura, base reta), de preferência sobre um arco Sálvia Ana. Texto sobre foto só em faixa sólida. Acervo de 16 fotos em `assets/fotos/catalogo.json`: sobra gestação, falta pós-parto e 40+ (use 04, 10, 14, 15 no pós-parto; 11, 12, 14, 16 no 40+).
- **Ícones dos destaques:** oito, com a pena do símbolo e um ponto cada; capa Sálvia Ana, traço Mar Fundo, ponto Algodão, ícone em 62% do quadro.
- **Movimento:** o traço se desenha da esquerda para a direita em 1,2 s (curva maré `cubic-bezier(.33,0,.15,1)`) e o ponto pousa por último em 240 ms. No vídeo, a Rota nunca atrasa o gancho. Com "reduzir movimento", tudo pronto.
- **Espaço** em múltiplos de 4 px; raios de 8, 14 e 24 px; pílula nos botões; sombras puxadas para o Mar Fundo.

---

## Voz (o essencial)

Acolhedora e firme, prática, bem-humorada (humor de casa, nunca de corpo), constante, real, responsável. Quatro princípios: **contexto antes de proibição, fase antes de regra, processo antes de promessa, uma pessoa de cada vez.**

- Frase curta, eu e você, pergunta no fim, uma palavra em caixa alta no máximo, **quase sem travessão (nunca em título)**, 💚 como assinatura (até três emojis), termo técnico traduzido na hora.
- Fórmula: **[Você, + quem ela é] + [a cena ou a dúvida] + [a virada].** "Você, gestante, vomita depois do ferro?" Em **anúncio pago**, vira "Para gestantes que...": a plataforma não aceita frase que presuma a condição de quem lê.
- Gancho de 2 segundos: fala de até 12 palavras, texto de tela de até 6, a Ana olhando para a câmera, nada de "oi, gente".
- Séries fixas: Levo ou Deixo, Peço ou Não Peço, Isso ou Aquilo, Casos de consultório, Exceções x Resultados, Coisas que eu falo sendo nutricionista.
- Três leves para uma de autoridade. Bordões só na forma registrada ("Não existe alimento vilão", "Você não precisa ser RADICAL, basta ser CONSISTENTE!").
- Evite: dieta, proibido, emagrecer X kg, detox, cura, garantido, único, exclusivo, melhor, especialista (sem título), antes e depois, é da idade, gordice, mãezinha, fit, promoção de consulta. Lista com o que usar no lugar: `references/voz.md`.
- Assinatura: em peça profissional, "Ana Paula Costa · Nutricionista · CRN-4 [número]"; em legenda e mensagem, "Ana 💚".

---

## Conformidade (TRAVADA)

Vale o Código de Ética do Nutricionista de 2018; o código novo já aprovado ainda vai entrar em vigor. **Onde os dois diferem, vale o mais rígido.**

1. CRN visível em tudo que é profissional (bio, rodapé do site, último cartão do carrossel, capa e fim de PDF, assinatura de e-mail, página de destino de anúncio).
2. Zero antes e depois, nem da Ana, nem com autorização. Zero print de exame, balança ou bioimpedância.
3. Depoimento só sobre a experiência (acolhimento, clareza, rotina), literal, autorizado por escrito, sem troca por desconto. Frase pública de outra mulher não é depoimento.
4. Preço da consulta nunca em post, story, anúncio, catálogo ou página; é dito no agendamento, em conversa privada. Produto digital e comunidade podem ter preço completo (valor, periodicidade, total do plano anual e como cancelar), sem "de/por" inventado.
5. Nada de promoção, desconto, sorteio, "indique e ganhe" ou data comercial para consulta. Escassez só verdadeira.
6. O que é vendido para muitas é **cardápio-exemplo**; plano alimentar individual só na consulta.
7. Prometa o caminho: ajuda, apoia, organiza, acompanha. Nunca cura, trata, elimina, emagrece X kg, desincha, detox, garantido, 100%, único, primeira, melhor. Garantias permitidas são de serviço: 7 dias da Semana Bem Nutrida (direito de arrependimento, sem condição) e Garantia do Plano que Cabe.
8. Inteligência artificial só para alimento ou objeto, sinalizada. Nunca pessoa, a Ana, corpo, consulta, resultado, embalagem de marca ou voz clonada.
9. Anúncio de saúde: público de 18 anos ou mais, sem presumir condição, sem atacar aparência, sem prazo, sem cura, sem caneta emagrecedora ou remédio. A página de destino passa pelo mesmo crivo.
10. Formulário pede só nome, WhatsApp, e-mail, fase e período; duas caixas de consentimento separadas e desmarcadas; nada de saúde no site, no pixel ou no endereço da página.
11. Sem marca de alimento ou suplemento, cupom, "recebidos" ou publi.
12. Filhos: nunca aparecem em peça da marca (rosto, corpo ou nome); podem ser citados no texto, sem identificação. A Ana não atende crianças.

Frases prontas (avisos, rodapé, caixas do formulário, garantias): [`lockup.html`](lockup.html), grupo 09. Tabela de errado e certo e checklist: `references/conformidade.md`.

---

## Canais e medidas (o essencial)

| Peça | Medida | Regra |
|---|---|---|
| Post e carrossel | 1080 × 1350 | Margem de 80 px; a grade mostra 3:4 (corta cerca de 34 px de cada lado); último cartão com convite, assinatura e CRN |
| Story, Reels, TikTok, Shorts, status | 1080 × 1920 | Área útil x 60 a 940, y 250 a 1540 (base 480 px livre em anúncio) |
| Capa de Reels e TikTok | 1080 × 1920 | Título dentro de x 80 a 1000, y 420 a 1500 |
| Capa de destaque | 1080 × 1920 | Ícone no círculo central de 640 × 640, até 400 px de largura |
| Foto de perfil | 1080 × 1080 (aparece com 110 px) | Rosto da Ana, fundo sólido, a mesma em todas as redes |
| Miniatura do YouTube | 1280 × 720 | Rosto grande, até 4 palavras, canto inferior direito livre |
| Banner do YouTube | 2560 × 1440 | Tudo no centro de 1546 × 423 |
| Capa do LinkedIn | 1584 × 396 | Primeiro quarto inferior esquerdo livre |
| Pin | 1000 × 1500 | Nada essencial nos últimos 120 px |
| E-mail | 600 px de largura | Uma coluna, texto de 17 a 18 px, um botão, rodapé com CRN e saída da lista |

Usuário em todas as redes: `@ana_costarodrigues`. Hashtags: #vidanutrida e #bemnutrida, mais 3 a 5 de tema. Calendário: Reels de autoridade na madrugada de segunda (00h30), repost nos stories de madrugada. Bios, destaques e calendário completos: `references/canais-e-medidas.md`.

---

## Checklist de aprovação de peça

- [ ] Fase, canal e um único convite definidos; a primeira frase nomeia a mulher.
- [ ] Logotipo do arquivo oficial, na versão do fundo, acima do mínimo, com área de proteção.
- [ ] Um ponto Caramelo só (contando o do logotipo); cores só do `tokens.json`; contraste de texto de 4,5 para 1 ou mais.
- [ ] Literata a partir de 24 px; números em Literata; texto em Atkinson; tamanhos mínimos da mídia.
- [ ] Foto real da Ana sozinha, em arco ou com faixa sólida; sem IA de pessoa; sem filtro de beleza.
- [ ] Dentro da zona segura; camada de zona segura oculta na exportação.
- [ ] CRN e "Nutricionista" na peça profissional (até P1: "CRN-4 em confirmação", e a peça não vai a público).
- [ ] Nenhum antes e depois, quilo, prazo, cura, garantia de resultado, preço de consulta, promoção, superlativo, marca patrocinada.
- [ ] Sem travessão em título; nenhuma sigla sem explicação; pt-BR claro.
- [ ] Anúncio: 18+, "para quem", sem aparência, página de destino conferida.

---

## Armadilhas (vão te morder)

- **"40+" com zero cortado.** Em Canva e CapCut a Atkinson não troca o zero sozinha: digite o número em Literata.
- **Caramelo sobre Sálvia.** O ponto some (1,02 para 1). Sobre Sálvia Ana o ponto é Algodão (arquivo `-sobre-salvia`).
- **Dois pontos quentes.** Logotipo colorido + Rota caramelo = dois. Use a Rota `-salvia`.
- **Botão verde no modo 40+.** Sálvia Funda sobre Mar Fundo some (2,1 para 1): no 40+ o botão é Ouro Velho com texto Mar Fundo.
- **Avatar transparente.** O WhatsApp pinta de preto. Os PNG oficiais já são opacos.
- **Foto de gestação no modo 40+ ou no pós-parto.** O acervo é quase todo da gravidez; siga a tabela de fotos por público.
- **"Você, gestante" no anúncio.** Reprovado pela plataforma. No anúncio é "Para gestantes que...".
- **Valor da consulta "só no story".** Não pode em nenhum conteúdo público.
- **Ícones antigos dos destaques.** Os oito finais estão em `assets/forma/icones-destaques/`; descrições antigas (balão, tigela, três pontos) não valem.
- **Texto "em confirmação" esquecido.** Nada vai a público com marcador aberto.

---

## Pendências com a Ana (não resolva por conta própria)

P1 número do CRN-4 · P2 WhatsApp oficial · P3 autorização das fotos · P4 nome da assinatura · P5 prova de cor impressa · P6 domínio do site · P7 teste de leitura do símbolo · P8 ícones de Gestação e Comunidade · P9 e-mail profissional e horário de atendimento · P10 dados de quem vende · P11 cadastro no e-Nutricionista · P12 preço e regras da Comunidade paga · P13 nomes e condições da esteira (Nutrição por Fases, Avaliação da Fase, Acompanhamento da Fase 90 dias, 24 horas, 30 dias de suporte, Garantia do Plano que Cabe) · P14 parcelamento com ou sem juros · P15 conferência do código de ética novo · P16 fé e família no conteúdo. O que fazer enquanto cada uma não fecha: [`references/pendencias.md`](references/pendencias.md). Também dependem dela: depoimentos autorizados, frases reais do pós-parto e o guia Ferro Sem Sofrimento em PDF.

---

## Mapa de arquivos

O inventário completo, com o que cada arquivo é, está no `README.md`. Em resumo: `SKILL.md`, `references/` (9 arquivos), `agents/openai.yaml`, `tokens.css`, `tokens.json`, `index.html`, `brand-book.html`, `guia-de-uso.html`, `lockup.html`, `kit-social.html`, `kit-video.html`, `assets/marca/`, `assets/forma/`, `assets/fontes/`, `assets/fotos/`, `assets/aplicacoes/`, `tools/`.
