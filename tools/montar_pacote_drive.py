#!/usr/bin/env python3
"""Monta o pacote da marca para o Google Drive da Ana (pastas numeradas, prontas para subir).

  python3 tools/montar_pacote_drive.py                 monta tudo no destino padrão
  python3 tools/montar_pacote_drive.py --destino DIR   monta em outra pasta
  python3 tools/montar_pacote_drive.py --sem-pdf       pula os PDF (logotipo, plano alimentar e manual)

Destino padrão: a chave "pacote_drive" de tools/origens.local.json (fora do git), a variável
ANA_PACOTE_DRIVE ou, na falta das duas, a pasta irmã "pacote-drive" da marca-final. O pacote
fica FORA do repositório público.

Pastas
  01 Logo                    SVG, PNG (512, 1024 e 2048 px) e PDF vetorial de cada versão
  02 Fontes                  Literata e Atkinson Hyperlegible Next (.ttf, licença aberta) e como instalar
  03 Cores                   paleta em .ase (Adobe), .gpl, .txt e .png; tokens.css e tokens.json
  04 Redes sociais           PNG dos modelos do kit de redes (assets/redes/), capas de destaque e avatares
  05 Vídeo                   abertura, encerramento e lower third (MP4 e MOV com transparência), ajuste
                             de cor (.cube), camadas de zona segura e modelos de legenda
  06 Fotos tratadas          as 16 fotos do acervo em JPG de resolução cheia, com o mesmo tratamento do manual
  07 Papelaria e materiais   plano alimentar (HTML e PDF A4), assinatura de e-mail, Rota, moldura, padrão e ícones
  08 Brandbook               manual em PDF A4 (impressão do brand-book.html pelo Chromium) e o link do manual
  LEIA-ME.txt

Idempotente: monta numa pasta temporária ao lado e só então troca a antiga pela nova.
Antes, rode tools/sync_marca.py (marca), tools/exportar_redes.py (PNG das redes), tools/kit_video.py
e tools/kit_producao.py (vídeo e produção). O que faltar entra como aviso no fim.
"""
import argparse
import functools
import http.server
import json
import os
import shutil
import socketserver
import sys
import threading
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "tools"))
PAGES = "https://rafaelnasch.github.io/branding-ana-costa/"
VERSAO = "versão 1.2 · outubro de 2026"
avisos = []


def local(chave, variavel):
    if os.environ.get(variavel):
        return Path(os.environ[variavel])
    arq = RAIZ / "tools" / "origens.local.json"
    if arq.exists():
        valor = json.loads(arq.read_text(encoding="utf-8")).get(chave)
        if valor:
            return Path(valor)
    return None


def destino_padrao():
    d = local("pacote_drive", "ANA_PACOTE_DRIVE")
    if d:
        return d
    mf = local("marca_final", "ANA_MARCA_FINAL")
    return mf.parent / "pacote-drive" if mf else None


def copiar(origem, destino):
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(origem, destino)


def copiar_glob(padrao, pasta, aviso_se_vazio=None):
    n = 0
    for f in sorted(RAIZ.glob(padrao)):
        if f.is_file() and f.name != ".DS_Store" and not f.name.endswith(".origem"):
            copiar(f, pasta / f.name)
            n += 1
    if not n and aviso_se_vazio:
        avisos.append(aviso_se_vazio)
    return n


def texto(destino, conteudo):
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(conteudo.strip() + "\n", encoding="utf-8")


# ------------------------------------------------------------------ navegador (PDF)
class Silencioso(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def servidor():
    socketserver.ThreadingTCPServer.daemon_threads = True
    socketserver.ThreadingTCPServer.request_queue_size = 128
    srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), functools.partial(Silencioso, directory=str(RAIZ)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, "http://127.0.0.1:%d/" % srv.server_address[1]


class Navegador:
    def __enter__(self):
        from playwright.sync_api import sync_playwright
        try:
            from qa import chromium
            exe = chromium()
        except Exception:
            exe = None
        self.pw = sync_playwright().start()
        self.nav = self.pw.chromium.launch(executable_path=exe) if exe else self.pw.chromium.launch()
        self.srv, self.base = servidor()
        return self

    def __exit__(self, *a):
        self.nav.close()
        self.pw.stop()
        self.srv.shutdown()

    def pagina(self, largura=1240):
        ctx = self.nav.new_context(viewport={"width": largura, "height": 900}, reduced_motion="reduce")
        return ctx, ctx.new_page()

    def pdf_svg(self, svg, destino, margem=0.5):
        """PDF vetorial do SVG, do tamanho do desenho mais a área de proteção (½ x = 25 unidades)."""
        import re
        t = svg.read_text(encoding="utf-8")
        vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', t).group(1).split()]
        escala = 4  # 1 unidade do SVG = 4 px no PDF (o símbolo sai com cerca de 534 px de largura)
        pad = 50 * margem * escala
        w, h = vb[2] * escala + 2 * pad, vb[3] * escala + 2 * pad
        t = re.sub(r'\swidth="[^"]*"', "", t, count=1)
        t = re.sub(r'\sheight="[^"]*"', "", t, count=1)
        t = t.replace("<svg ", '<svg width="%.2f" height="%.2f" ' % (vb[2] * escala, vb[3] * escala), 1)
        ctx, pg = self.pagina()
        pg.set_content('<!doctype html><html><head><style>@page{margin:0}html,body{margin:0;background:transparent}'
                       'body{padding:%.2fpx}svg{display:block}</style></head><body>%s</body></html>' % (pad, t))
        pg.pdf(path=str(destino), width="%.2fpx" % w, height="%.2fpx" % (h + 1), print_background=True,
               page_ranges="1")
        ctx.close()

    def _abrir_impressao(self, caminho, largura):
        ctx, pg = self.pagina(largura)
        pg.goto(self.base + caminho, wait_until="networkidle")
        pg.evaluate("document.fonts.ready")
        pg.evaluate("""() => { document.querySelectorAll('img[loading="lazy"]').forEach(i => i.loading = 'eager'); }""")
        pg.wait_for_timeout(1500)
        pg.wait_for_load_state("networkidle")
        pg.emulate_media(media="print")
        return ctx, pg

    def pdf_pagina(self, caminho, destino, largura=1240):
        ctx, pg = self._abrir_impressao(caminho, largura)
        try:
            pg.pdf(path=str(destino), format="A4", print_background=True, prefer_css_page_size=True)
            ctx.close()
            return
        except Exception as e:
            ctx.close()
            if caminho != "brand-book.html":
                raise
            avisos.append("08 Brandbook: o Chromium não imprimiu o manual inteiro de uma vez (%s); "
                          "saiu por partes e foi unido" % str(e)[:60])
        self._pdf_por_partes(caminho, destino, largura)

    def _pdf_por_partes(self, caminho, destino, largura):
        """O manual inteiro passa do limite de impressão do Chromium: imprime parte a parte e une."""
        ctx, pg = self._abrir_impressao(caminho, largura)
        filhos = pg.evaluate("[...document.querySelector('main').children].map(c => c.className)")
        ctx.close()
        grupos, atual = [], []
        for i, classe in enumerate(filhos):
            if "parte-abre" in classe and atual and any("secao" in filhos[j] for j in atual):
                grupos.append(atual)
                atual = []
            atual.append(i)
        grupos.append(atual)
        partes = []
        for n, grupo in enumerate(grupos):
            ctx, pg = self._abrir_impressao(caminho, largura)
            pg.evaluate("""([manter, primeiro]) => {
                [...document.querySelector('main').children].forEach((c, i) => { if (!manter.includes(i)) c.remove(); });
                if (!primeiro) { const capa = document.querySelector('header.capa'); if (capa) capa.remove(); }
            }""", [grupo, n == 0])
            parte = destino.with_name("%s.parte%02d.pdf" % (destino.stem, n))
            pg.pdf(path=str(parte), format="A4", print_background=True, prefer_css_page_size=True)
            ctx.close()
            partes.append(parte)
        try:
            from pypdf import PdfWriter
        except ImportError:
            avisos.append("08 Brandbook: pypdf ausente; o manual ficou em %d PDF separados" % len(partes))
            return
        w = PdfWriter()
        for parte in partes:
            w.append(str(parte))
        with open(destino, "wb") as f:
            w.write(f)
        for parte in partes:
            parte.unlink()


# ------------------------------------------------------------------ pastas
def p01_logo(alvo, nav):
    pasta = alvo / "01 Logo"
    copiar_glob("assets/marca/svg/*.svg", pasta / "SVG")
    copiar_glob("assets/marca/png/*.png", pasta / "PNG")
    copiar_glob("assets/marca/favicon/*", pasta / "Favicon")
    copiar_glob("assets/marca/og/*.png", pasta / "Prévia de link")
    if nav:
        (pasta / "PDF").mkdir(parents=True, exist_ok=True)
        for svg in sorted((RAIZ / "assets/marca/svg").glob("*.svg")):
            if svg.name.startswith("avatar"):
                continue
            nav.pdf_svg(svg, pasta / "PDF" / (svg.stem + ".pdf"))
    texto(pasta / "Qual arquivo usar.txt", """
QUAL ARQUIVO USAR · Ana Paula Costa · Nutricionista

O nome do arquivo diz o fundo:
  -cor            fundos claros (Algodão, Bruma, Pedra, branco)
  -sobre-salvia   fundo Sálvia Ana (o mais da marca): traço Mar Fundo, ponto Algodão
  -sobre-escuro   fundo Mar Fundo
  -branco         sobre foto escura e calma ou vídeo
  -preto          impressão a uma cor, carimbo

SVG  site e tudo que vai ser ampliado.
PNG  Canva, editores de vídeo, apresentações (512, 1024 e 2048 px; já trazem a área de proteção).
PDF  gráfica (vetorial, com a área de proteção de meia altura do "a" em volta).

Tamanhos mínimos (largura):
  horizontal com "Nutricionista"   300 px na tela · 65 mm impresso
  horizontal reduzida              160 px · 35 mm
  vertical                         210 px · 45 mm
  assinatura compacta              230 px · 48 mm
  sub-marcas Bem Nutrida           260 px · 55 mm
  símbolo                          32 px · 10 mm

Nunca: digitar o nome ao lado do símbolo, esticar, girar, contornar, sombrear, pôr dentro de
círculo desenhado ou usar caramelo sobre Sálvia Ana. Avatares são quadrados: a rede recorta o círculo.
Manual completo: %sbrand-book.html#s05
""" % PAGES)


def p02_fontes(alvo):
    pasta = alvo / "02 Fontes"
    copiar_glob("assets/fontes/*.ttf", pasta)
    copiar_glob("assets/fontes/OFL-*.txt", pasta / "Licenças")
    texto(pasta / "Como instalar.txt", """
FONTES DA MARCA · licença aberta (SIL Open Font License), uso livre

Literata                     títulos, nome, citações e TODOS os números (a partir de 24 px)
Atkinson Hyperlegible Next   texto, botões, rótulos e legendas

Instalar no computador: dê dois cliques em cada .ttf e clique em Instalar (Mac: Instalar Fonte).
Comece pelos variáveis: Literata[opsz,wght].ttf, Literata-Italic[opsz,wght].ttf,
AtkinsonHyperlegibleNext[wght].ttf e o itálico. As instâncias Regular, Medium, SemiBold e Bold
servem a programas que não leem fonte variável.

Canva: Marca, Kit de marca, Fontes, Enviar fonte (ou use as duas, que já existem no Canva).
CapCut e editores de vídeo: instale no computador e reabra o programa.

Atenção: a Atkinson desenha o zero cortado. Digite "40+", datas e medidas em Literata.
Os arquivos Literata-Display-Assinatura são os do logotipo: não use para escrever o nome.
""")


def p03_cores(alvo):
    pasta = alvo / "03 Cores"
    copiar_glob("assets/producao/paleta/*", pasta, "03 Cores: paleta do kit de produção ausente (rode tools/kit_producao.py)")
    copiar(RAIZ / "tokens.css", pasta / "Para o site" / "tokens.css")
    copiar(RAIZ / "tokens.json", pasta / "Para o site" / "tokens.json")
    dados = json.loads((RAIZ / "tokens.json").read_text(encoding="utf-8"))
    linhas = ["CORES DA MARCA · Ana Paula Costa · Nutricionista", "",
              "Nome                 HEX       RGB            CMYK (FOGRA39, papel revestido)  Proporção", ""]
    for grupo in ("cores", "cores_derivadas"):
        for c in dados[grupo].values():
            linhas.append("%-20s %-9s %-14s %-32s %s" % (c["nome"], c["hex"], " ".join(map(str, c["rgb"])),
                                                        " ".join(map(str, c["cmyk_fogra39"])), c.get("proporcao_sugerida", "só gráfico")))
    linhas += ["", "Regras: Sálvia Ana domina; um ponto Caramelo por peça (o do logotipo conta); Caramelo sobre",
               "Sálvia Ana é proibido; Sálvia Ana e Caramelo nunca como texto sobre fundo claro.",
               "Papel não revestido: a gráfica converte do RGB com o perfil dela. Peça prova de cor antes da primeira tiragem.",
               "Manual: %sbrand-book.html#s09" % PAGES]
    texto(pasta / "Cores com códigos.txt", "\n".join(linhas))


def p04_redes(alvo):
    pasta = alvo / "04 Redes sociais"
    n = copiar_glob("assets/redes/*.png", pasta / "Modelos do kit",
                    "04 Redes sociais: nenhum PNG em assets/redes/ (rode tools/exportar_redes.py)")
    copiar_glob("assets/forma/icones-destaques/png/*.png", pasta / "Capas de destaque")
    for f in ("avatar-instagram-1080.png", "avatar-instagram-mar-1080.png", "avatar-instagram-pequeno-1080.png"):
        if (RAIZ / "assets/marca/png" / f).exists():
            copiar(RAIZ / "assets/marca/png" / f, pasta / "Avatar" / f)
    texto(pasta / "LEIA-ME.txt", """
REDES SOCIAIS

PARA EDITAR, ABRA O KIT PELO ENDEREÇO PUBLICADO (funciona no celular, sem instalar nada):
%skit-social.html
Aberto direto do computador, com duplo clique, o kit não funciona.

Modelos do kit (%d PNG): cada arquivo diz o modelo, a fase e a medida
(ex.: ana-costa_citacao_pos-parto_1080x1350.png). O carrossel sai numerado na ordem de postar
(ana-costa_carrossel-01_..., -02, -03...); no kit, "Baixar carrossel inteiro" entrega um ZIP pronto.

Fontes para montar no Canva ou no CapCut: pasta 02 Fontes (ou o bloco "Antes de começar: instale as fontes" no kit).

Capas de destaque: 1080 x 1920 para o destaque e 1080 x 1080 para o círculo.
Avatar com o símbolo: para o grupo e a comunidade. Nas redes da Ana, a foto de perfil é o rosto dela.

Antes de publicar: CRN no lugar de "CRN-4 em confirmação", um ponto caramelo por peça,
nada de antes e depois, preço de consulta, promessa de resultado ou alimento vilão.
""" % (PAGES, n))


def p05_video(alvo):
    pasta = alvo / "05 Vídeo"
    origem = RAIZ / "assets/video"
    if origem.is_dir() and any(origem.rglob("*.mp4")):
        for f in sorted(origem.rglob("*")):
            if f.is_file() and f.name != ".DS_Store":
                copiar(f, pasta / "Abertura, lower third e encerramento" / f.relative_to(origem))
    else:
        avisos.append("05 Vídeo: assets/video/ sem vídeos (rode tools/kit_video.py)")
    for sub, nome in (("cor", "Ajuste de cor"), ("zona-segura", "Zona segura"), ("legenda", "Legenda")):
        copiar_glob("assets/producao/%s/*" % sub, pasta / nome, "05 Vídeo: assets/producao/%s ausente" % sub)
    if (RAIZ / "assets/producao/README.md").exists():
        copiar(RAIZ / "assets/producao/README.md", pasta / "Como usar no editor.md")
    copiar_glob("assets/marca/png/assinatura-compacta-*-2048.png", pasta / "Assinatura para sobrepor")
    copiar_glob("assets/marca/png/simbolo-*-2048.png", pasta / "Assinatura para sobrepor")
    texto(pasta / "LEIA-ME.txt", """
VÍDEO · padrão de edição

Formato: 1080 x 1920 (vertical) ou 1920 x 1080, 30 quadros por segundo, MP4 H.264, áudio AAC.
Nome: AAAA-MM-DD_rede_quadro_tema.mp4
Área útil do vertical: x de 60 a 940, y de 250 a 1540 (base livre de 480 px em anúncio).
Gancho nos 2 primeiros segundos, sem "oi, gente". Corte seco. Música de 18 a 24 dB abaixo da voz.
Legenda queimada: Atkinson Hyperlegible Next SemiBold 60 px, até 2 linhas de 32 caracteres,
texto Algodão sobre caixa Mar Fundo a 85%%, uma palavra-chave em Sálvia Ana. Sem emoji.
Cor: um único ajuste (arquivo .cube em Ajuste de cor). Sem filtro de beleza.
Os vídeos com fundo transparente (.mov, ProRes 4444) vão por cima da gravação.
Manual: %sbrand-book.html#s16-6
""" % PAGES)


def p06_fotos(alvo):
    pasta = alvo / "06 Fotos tratadas"
    pasta.mkdir(parents=True, exist_ok=True)
    try:
        import fotos
    except Exception as e:  # sem Pillow ou sem o script de fotos
        avisos.append("06 Fotos: não deu para carregar tools/fotos.py (%s)" % e)
        return
    catalogo = json.loads((RAIZ / "assets/fotos/catalogo.json").read_text(encoding="utf-8"))
    por_id = {f["id"]: f for f in catalogo["fotos"]}
    linhas = ["FOTOS TRATADAS · acervo da Ana Paula Costa", "",
              "Tratamento: cor sRGB, contraste +3%, saturação -3%, nitidez suave. Sem recorte, sem retoque,",
              "sem metadados. Só a Ana, sozinha. Uso comercial depende da autorização da Ana (pendência P3).", ""]
    from PIL import Image
    for f in fotos.FOTOS:
        nome = f["id"] + ".jpg"
        org = (fotos.ORIGEM / f["origem"]) if fotos.ORIGEM else None
        if org and org.exists():
            im = fotos.tratar(org)
            fonte = "resolução cheia"
        else:
            im = fotos.srgb(Image.open(RAIZ / "assets/fotos/1600" / (f["id"] + ".webp")))
            fonte = "1600 px (original fora desta máquina)"
            avisos.append("06 Fotos: %s saiu da versão de 1600 px" % f["id"])
        im.convert("RGB").save(pasta / nome, "JPEG", quality=92, optimize=True, progressive=True)
        c = por_id.get(f["id"], f)
        linhas += ["%s  (%d x %d, %s)" % (nome, im.width, im.height, fonte),
                   "  fase: %s" % c.get("fase", ""), "  uso: %s" % c.get("uso", ""),
                   "  texto alternativo: %s" % c.get("alt", ""), ""]
    texto(pasta / "Catálogo das fotos.txt", "\n".join(linhas))


def p07_papelaria(alvo, nav):
    pasta = alvo / "07 Papelaria e materiais"
    for nome in ("plano-alimentar.html", "assinatura-email.html"):
        if (RAIZ / "assets/aplicacoes" / nome).exists():
            copiar(RAIZ / "assets/aplicacoes" / nome, pasta / "Modelos HTML" / nome)
    if nav and (RAIZ / "assets/aplicacoes/plano-alimentar.html").exists():
        nav.pdf_pagina("assets/aplicacoes/plano-alimentar.html", pasta / "Plano alimentar (modelo A4).pdf", 900)
    copiar_glob("assets/forma/*.svg", pasta / "Rota, moldura e padrão")
    copiar_glob("assets/forma/icones-destaques/*.svg", pasta / "Ícones")
    texto(pasta / "LEIA-ME.txt", """
PAPELARIA E MATERIAIS

Plano alimentar: modelo A4 (fundo Algodão, refeições com marcador Sálvia Funda, recado da Ana em
Bruma, CRN no rodapé). O cardápio do modelo é ilustrativo. Plano individual só sai da consulta;
material para muitas é cardápio-exemplo.
Assinatura de e-mail: abra o HTML no navegador, selecione do símbolo até a Rota, copie e cole
nas configurações de assinatura do e-mail. Troque "CRN-4 em confirmação" e o WhatsApp antes.
Cartão de visita 90 x 50 mm: frente Sálvia Ana com o símbolo (36 mm), verso Algodão com o
logotipo horizontal (65 mm); arquivo com 3 mm de sangria; papel 300 g fosco. Use os PDF de 01 Logo.
Rota: toda rota termina num ponto e mergulha uma vez. Com o logotipo colorido na peça, use os
arquivos -salvia (um ponto caramelo por peça, e o do logotipo conta).

Nada vai para a gráfica sem o número do CRN-4 (P1), o WhatsApp oficial (P2) e a prova de cor (P5).
Manual: %sbrand-book.html#s22
""" % PAGES)


def p08_brandbook(alvo, nav):
    pasta = alvo / "08 Brandbook"
    pasta.mkdir(parents=True, exist_ok=True)
    if nav:
        nav.pdf_pagina("brand-book.html", pasta / "Manual da marca Ana Paula Costa (A4).pdf")
    (pasta / "Manual da marca (abrir no navegador).url").write_text(
        "[InternetShortcut]\nURL=%sbrand-book.html\n" % PAGES, encoding="utf-8")
    texto(pasta / "Links.txt", """
Manual da marca (sempre a versão mais nova):  %sbrand-book.html
Entrada com todos os materiais:                %s
Guia de uso (pedidos prontos por público):     %sguia-de-uso.html
Trechos para copiar (assinaturas, bios, CRN):  %slockup.html
Kit de redes:                                  %skit-social.html

O PDF desta pasta é uma fotografia do manual na data em que o pacote foi montado (%s).
""" % (PAGES, PAGES, PAGES, PAGES, PAGES, VERSAO))


def leia_me(alvo):
    texto(alvo / "LEIA-ME.txt", """
MARCA ANA PAULA COSTA · NUTRICIONISTA
Sistema Rota ap. · %s

Cada fase pede outro prato.

O QUE TEM AQUI
01 Logo                     o logotipo em todas as versões: SVG, PNG e PDF para gráfica
02 Fontes                   Literata e Atkinson Hyperlegible Next, com o passo a passo para instalar
03 Cores                    a paleta para Adobe, Canva e afins, e os códigos HEX, RGB e CMYK
04 Redes sociais            os modelos de post, carrossel, story, capas de destaque e avatar
05 Vídeo                    abertura, lower third, encerramento, ajuste de cor, zona segura e legenda
06 Fotos tratadas           o acervo de fotos da Ana, em JPG
07 Papelaria e materiais    plano alimentar, assinatura de e-mail, Rota, padrão e ícones
08 Brandbook                o manual completo em PDF A4 e o link da versão online

POR ONDE COMEÇAR
Quem produz conteúdo: 08 Brandbook (partes VI e VII) e 04 Redes sociais.
Quem edita vídeo: 05 Vídeo (leia o LEIA-ME de lá).
Gráfica: 01 Logo/PDF e 03 Cores.

TRÊS REGRAS QUE NÃO MUDAM
1. O logotipo é sempre o arquivo. Nunca digite o nome ao lado do símbolo.
2. Um ponto caramelo por peça, e o do logotipo conta.
3. Nenhuma peça vai a público sem o número do CRN-4 no lugar de "CRN-4 em confirmação".

Manual online, sempre atualizado: %sbrand-book.html
""" % (VERSAO, PAGES))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--destino")
    ap.add_argument("--sem-pdf", action="store_true")
    args = ap.parse_args()
    destino = Path(args.destino) if args.destino else destino_padrao()
    if not destino:
        print("ERRO: defina o destino com --destino, ANA_PACOTE_DRIVE ou tools/origens.local.json")
        return 2
    destino = destino.resolve()
    if RAIZ in destino.parents or destino == RAIZ:
        print("ERRO: o pacote não pode ficar dentro do repositório público")
        return 2
    temp = destino.with_name(destino.name + ".montando")
    if temp.exists():
        shutil.rmtree(temp)
    temp.mkdir(parents=True)

    def montar(nav):
        p01_logo(temp, nav)
        p02_fontes(temp)
        p03_cores(temp)
        p04_redes(temp)
        p05_video(temp)
        p06_fotos(temp)
        p07_papelaria(temp, nav)
        p08_brandbook(temp, nav)
        leia_me(temp)

    if args.sem_pdf:
        avisos.append("PDF pulados (--sem-pdf)")
        montar(None)
    else:
        try:
            with Navegador() as nav:
                montar(nav)
        except ImportError:
            avisos.append("Playwright ausente: PDF não gerados (pip install playwright)")
            montar(None)

    if destino.exists():
        shutil.rmtree(destino)
    temp.rename(destino)
    total, n = 0, 0
    print("Pacote do Drive: %s" % destino)
    for pasta in sorted(p for p in destino.iterdir() if p.is_dir()):
        arqs = [f for f in pasta.rglob("*") if f.is_file()]
        tam = sum(f.stat().st_size for f in arqs)
        total += tam
        n += len(arqs)
        print("  %-28s %4d arquivos  %7.1f MB" % (pasta.name, len(arqs), tam / 1048576))
    print("  total: %d arquivos, %.1f MB" % (n, total / 1048576))
    for a in avisos:
        print("  AVISO  %s" % a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
