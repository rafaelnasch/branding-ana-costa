# branding-ana-costa

**A identidade visual da nutricionista Ana Paula Costa (gestação, pós-parto, 40+ e menopausa; atendimento online a partir do Rio de Janeiro), empacotada como uma Skill (Claude e ChatGPT/Codex, no padrão aberto Agent Skills) e um kit de produção.** Sistema Rota ap. v1.2, outubro de 2026. Versão 1, com dados que ainda dependem da Ana (pendências `P1` a `P16`).

Instale uma vez e peça o material em português. O assistente passa a produzir post, carrossel, story, Reels, TikTok, capa de destaque, anúncio, página, e-mail, WhatsApp, plano alimentar, PDF, cartão e vídeo **já no padrão da Ana**: o monograma ap. sempre em arquivo oficial, a Sálvia Ana dominando, um único ponto Caramelo por peça, o modo de cor da fase certa, Literata nos títulos e nos números, Atkinson Hyperlegible Next no texto, a Rota que mergulha uma vez e pousa no ponto, foto real da Ana, a voz acolhedora e firme e as regras do conselho de nutrição. Sem você precisar explicar nada disso de novo.

> "No padrão da Ana, faz um carrossel 4:5 para a mulher de 45+ sobre proteína no café da manhã, com convite para o grupo."
> "Escreve o roteiro de um TikTok de 15 segundos para a gestante que passa mal com o ferro."
> "Revisa esta legenda contra as regras do conselho e me dá a versão segura."

**Ver no navegador:** [rafaelnasch.github.io/branding-ana-costa](https://rafaelnasch.github.io/branding-ana-costa/) (abre em qualquer aparelho, sem instalar nada). Manual: [brand-book.html](https://rafaelnasch.github.io/branding-ana-costa/brand-book.html). Pedidos prontos: [guia de uso](https://rafaelnasch.github.io/branding-ana-costa/guia-de-uso.html). Trechos para copiar: [lockup](https://rafaelnasch.github.io/branding-ana-costa/lockup.html).

---

## O que vem na caixa

| Arquivo | O que é |
|---|---|
| `SKILL.md` | O essencial para o agente operar sem improvisar (menos de 250 linhas): a primeira pergunta (peça, fase, canal, convite), o mapa de qual referência abrir em cada passo, as oito leis, cores, modos por fase, tipografia, marca, forma, voz, conformidade, medidas por canal, checklist, armadilhas e pendências. |
| `references/` | O detalhe, aberto só quando o passo pede (9 arquivos): `cor.md`, `tipografia.md`, `marca.md`, `forma.md`, `fotografia-e-video.md`, `voz.md`, `conformidade.md`, `canais-e-medidas.md`, `pendencias.md`. Os valores de cor saem do `tokens.json`. |
| `agents/openai.yaml` | Metadados de exibição para Codex e ChatGPT (nome "Ana Paula Costa · Rota ap.", descrição curta, ícone e cor). O Claude ignora. |
| `index.html` | **Abra primeiro.** A entrada: manual, kit de redes, kit de vídeo, guia, trechos e arquivos. |
| `brand-book.html` | O manual vivo em 8 partes (seções 01 a 25), com busca, seletor de fase (Gestação, Pós-parto, 40+), peças em tamanho real e impressão A4. Cada seção abre por âncora (`#s20`, `#s20-3`). |
| `guia-de-uso.html` | 29 pedidos prontos em 6 públicos (social media, editor de vídeo, designer, a própria Ana, desenvolvedor, agente de inteligência artificial), cada um com o arquivo a abrir e o que conferir antes de entregar. |
| `lockup.html` | Trechos prontos para copiar em nove grupos: cabeçalho do site, logotipo em SVG e em data URI, avatar, favicon e prévia de link, assinatura de e-mail em HTML, textos do WhatsApp, bios, NAP e CRN, rodapé legal e avisos do conselho. |
| `kit-social.html` | Editor dos modelos de rede em tamanho real, com zona segura e exportação em PNG: feed 4:5 e 3:4, carrossel (com ZIP numerado na ordem), anúncio 4:5 e 9:16, stories, stories dos 8 destaques, Semana Bem Nutrida, capa de live e de encontro (9:16 e 16:9), Reels, status, YouTube, catálogo do WhatsApp, LinkedIn, Pinterest, cabeçalho de e-mail e foto de perfil em 1080, 800, 720, 640 e 400 px. Os PNG padrão ficam em `assets/redes/`. |
| `kit-video.html` | Kit de vídeo: abertura, lower third e encerramento animados, legenda queimada, ajuste de cor, zona segura e paleta para editores. Os arquivos ficam em `assets/video/` e `assets/producao/`. |
| `tokens.css` · `tokens.json` | Os valores do sistema: cores (HEX, RGB, CMYK FOGRA39), contraste calculado, modos por fase, tipografia, escalas, espaço, raios, sombras, movimento e a Rota. Gerados da marca final por `tools/sync_marca.py`. |
| `assets/marca/` | Logotipo em SVG (5 esquemas de cada versão) e PNG de 512, 1024 e 2048 px; sub-marcas Bem Nutrida; avatares; favicon; prévia de link. |
| `assets/forma/` | A Rota (divisores, seta), régua de fases, moldura em arco, padrão de fundo e os oito ícones dos destaques (SVG e PNG). |
| `assets/fontes/` | Literata e Atkinson Hyperlegible Next (licença aberta), em `.ttf` e `.woff2`. |
| `assets/fotos/` | O `catalogo.json` das 16 fotos do acervo da Ana (fase, uso, texto alternativo). As fotos em WebP de 1600 e 640 px ficam fora do repositório público até a autorização de uso (P3): no endereço publicado aparece a moldura "autorização em confirmação". |
| `assets/aplicacoes/` | Modelos de assinatura de e-mail e plano alimentar A4; capturas do site. |
| `assets/paginas/` | Estilo e script das páginas de apoio (entrada, guia, trechos). |
| `_fragmentos/` | A fonte do manual: a casca (`00-casca.html`) e uma seção por arquivo (`s01` a `s25`). O `brand-book.html` é montado a partir deles por `tools/montar_brand_book.py`; edite aqui, nunca no manual montado. |
| `tools/` | Scripts de montagem e conferência (ver Comandos). |

## Instalar

O nome da pasta tem que ser exatamente `branding-ana-costa`, com o `SKILL.md` dentro. A mesma pasta serve ao Claude e ao ChatGPT/Codex.

### Claude Code (terminal, VS Code, app de desktop)

```bash
git clone https://github.com/rafaelnasch/branding-ana-costa.git ~/.claude/skills/branding-ana-costa
```

Abra uma sessão nova e digite `/branding-ana-costa`, ou peça "faz no padrão da Ana". Para atualizar: `cd ~/.claude/skills/branding-ana-costa && git pull`.

### Codex (CLI, extensão de IDE e app de desktop)

```bash
git clone https://github.com/rafaelnasch/branding-ana-costa.git ~/.agents/skills/branding-ana-costa
```

Versões anteriores leem `~/.codex/skills/` (mesmo comando, trocando a pasta).

### claude.ai (navegador e celular) e ChatGPT

1. Gere o pacote com `python3 tools/empacotar_skill.py` (ou baixe o `branding-ana-costa.zip` publicado em Releases).
2. No claude.ai, vá em **Configurações, Capacidades, Skills** e envie o ZIP. No ChatGPT, envie o mesmo ZIP onde o app oferecer Skills.

> Use o ZIP do pacote, **não** o "Code, Download ZIP" do GitHub: aquele traz o repositório inteiro (com vídeos e fotos, mais de 100 MB) e a pasta com o nome errado.

O pacote leva `SKILL.md`, `references/`, `agents/openai.yaml`, tokens, `lockup.html`, `guia-de-uso.html`, a marca (SVG, PNG de até 1024 px, favicon, prévia de link), a forma, as fontes, os modelos de e-mail e plano alimentar, a paleta e a legenda do kit de produção. **Fotos, vídeos e o manual não viajam no ZIP:** dentro do pacote, os caminhos para eles viram endereços públicos do Pages (`https://rafaelnasch.github.io/branding-ana-costa/...`).

### Limites atendidos (conferidos em 09/10/2026)

| Limite | Regra | Esta skill |
|---|---|---|
| `name` | minúsculas, números e hífen, igual ao nome da pasta | `branding-ana-costa` |
| `description` | até 1.024 caracteres; caso de uso e gatilhos no começo | 1.015 caracteres |
| `SKILL.md` | menos de 500 linhas; detalhe em `references/` | 223 linhas; 9 referências |
| Links relativos | todo link de `SKILL.md` e `references/` aponta para arquivo do pacote | 0 quebrados |
| ZIP | abaixo de 10 MB, sem fotos nem vídeos | 4,0 MB, 221 arquivos; o maior tem 0,93 MB (ajuste de cor `.cube`) |

## O primeiro teste

Abra uma conversa nova e peça:

> "No padrão da Ana, faz um post 1080 por 1350 para a gestante sobre ferro e enjoo."

Está funcionando se vier: modo Gestação (fundo Bruma, ponto Sálvia Funda), título em Literata nomeando a leitora ("Você, gestante, ..."), foto real da Ana em arco ou nenhuma foto, um único ponto quente, o logotipo oficial, "Ana Paula Costa · Nutricionista" e "CRN-4 em confirmação" no rodapé, o aviso "não pare nenhum suplemento sem falar com quem te acompanha", nenhuma dose, nenhum travessão. Se vier um post genérico, a skill não carregou: confira se a pasta se chama `branding-ana-costa` e tem o `SKILL.md`.

## Usar

Diga, ou deixe o assistente perguntar numa frase só: **que peça**, **para qual fase** (gestação, pós-parto ou 40+), **em qual canal** (o TikTok fala com a gestante; o Instagram, com a mulher de 45+ e a mãe no pós-parto) e **qual único convite** (grupo gratuito, Semana Bem Nutrida, guia do ferro ou Avaliação da Fase).

O manual, o guia e os trechos abrem com duplo clique. O kit de redes exporta PNG melhor servido por HTTP: rode `python3 -m http.server 8000` na raiz e abra `http://localhost:8000/`, ou use o endereço público. Dado que a Ana ainda não confirmou sai como "em confirmação" com a pendência `Pn`: troque pelo dado real antes de publicar.

## Comandos

Todos rodam da raiz do repositório com `python3` (os que renderizam precisam de Playwright com Chromium; os de imagem, de Pillow).

| Para | Comando |
|---|---|
| Trazer a versão mais nova da marca (logotipo, forma, fontes, tokens) | `python3 tools/sync_marca.py` · só comparar: `--conferir` |
| Tratar as fotos do acervo | `python3 tools/fotos.py` |
| Montar o manual a partir dos fragmentos | `python3 tools/montar_brand_book.py` |
| Montar a entrada, o guia, os trechos e o kit de vídeo (logotipo em código sempre da versão nova) | `python3 tools/montar_paginas.py` · só comparar: `--conferir` |
| PNG padrão do kit de redes | `python3 tools/exportar_redes.py` |
| Vídeos do kit (abertura, lower third, encerramento) | `python3 tools/kit_video.py` |
| Kit de produção (ajuste de cor, zona segura, legenda, paleta) | `python3 tools/kit_producao.py` |
| Gate de aceite dos HTML (estrutura, links, contraste, cores, travessões, dado interno) | `python3 tools/verificar.py` |
| Conferência no navegador (320, 390, 430 e 1440 px, capturas, PDF) | `python3 tools/qa.py pagina.html` · `--pdf` |
| Pacote da skill para claude.ai e ChatGPT | `python3 tools/empacotar_skill.py` → `dist-skill/branding-ana-costa.zip` (fora do git) |
| Pacote para o Google Drive da Ana | `python3 tools/montar_pacote_drive.py` → pasta `pacote-drive/` fora do repositório, com `01 Logo` (SVG, PNG e PDF vetorial), `02 Fontes`, `03 Cores`, `04 Redes sociais`, `05 Vídeo`, `06 Fotos tratadas` (JPG em resolução cheia), `07 Papelaria e materiais`, `08 Brandbook` (PDF A4 e link) e `LEIA-ME.txt` |

Os caminhos das pastas de origem (marca final e pesquisa) ficam em `tools/origens.local.json` ou em variáveis de ambiente, fora do git.

## Conformidade

Nutricionista: CRN visível em tudo que é profissional; nenhum antes e depois, nem da própria Ana; nada de promessa de quilos, prazo, cura ou resultado garantido; preço de consulta fora de qualquer divulgação; consulta nunca em promoção ou sorteio; depoimento só sobre a experiência, literal e autorizado; cardápio-exemplo para muitas, plano individual só na consulta; inteligência artificial só para alimento ou objeto, sinalizada; anúncio de saúde para maiores de 18 anos, sem presumir a condição de quem lê; formulário com o mínimo de dados e consentimento separado. Onde o código de ética vigente e o novo diferem, vale o mais rígido. Frases-modelo no `lockup.html` (grupo 09) e em `references/conformidade.md`. Este material é um guia do dia a dia e não substitui orientação jurídica.

## Pendências com a Ana

São 16 (`P1` a `P16`): número do CRN-4, WhatsApp oficial, autorização das fotos, nome da assinatura, prova de cor impressa, domínio do site, teste de leitura do símbolo, ícones de Gestação e Comunidade, e-mail profissional e horário de atendimento, dados de quem vende, cadastro no e-Nutricionista, preço e regras da Comunidade paga, nomes e condições da esteira, parcelamento com ou sem juros, conferência do código de ética novo e a decisão sobre fé e família no conteúdo. O que fazer enquanto cada uma não fecha está em `references/pendencias.md` e na seção 25 do manual. **Nenhuma peça vai a público sem o número do CRN-4.**

## Publicação

Repositório público, servido pelo GitHub Pages em [rafaelnasch.github.io/branding-ana-costa](https://rafaelnasch.github.io/branding-ana-costa/) (o arquivo `.nojekyll` faz o Pages servir os `.md` e as pastas como estão).

**Nunca entram aqui:** dado de paciente, valor de consulta, conversa privada, telefone pessoal, foto com os filhos ou outras pessoas, pessoa gerada por inteligência artificial, material interno de quem mantém o repositório ou caminho de pasta local. A lista local de termos proibidos (`tools/termos-proibidos.txt`) e os caminhos de origem ficam fora do git. Navegadores: Chrome, Edge ou Safari recentes.

---

Marca, logotipo e fotografias são da **Ana Paula Costa**. Fontes Literata e Atkinson Hyperlegible Next sob licença aberta (SIL Open Font License). Sistema criado pela GrowAI. Rota ap. v1.2 · outubro de 2026.
