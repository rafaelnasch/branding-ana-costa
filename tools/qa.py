#!/usr/bin/env python3
"""Conferência no navegador (Playwright + Chromium do cache local) e capturas para olhar.

  python3 tools/qa.py                         brand-book.html: largura em 320/390/430/1440, erros de
                                              console, imagens quebradas, capturas em 390 e 1440
  python3 tools/qa.py pagina.html             outra página do repositório
  python3 tools/qa.py --secao s09             captura só a seção (elemento #s09) em 390 e 1440
  python3 tools/qa.py --fases                 capa e primeira tela do conteúdo nos três modos (1440)
  python3 tools/qa.py --inteira               captura da página inteira (pesada) em 390 e 1440
  python3 tools/qa.py --pdf                   gera _qa/<pagina>.pdf em A4 como o botão Imprimir
  python3 tools/qa.py --gaveta                captura o sumário aberto no celular (390)

As capturas vão para _qa/ (fora do git). Abra-as e OLHE: validação automática não prova
qualidade visual. Sai com 1 se alguma largura gerar rolagem horizontal, se houver erro de
console ou imagem quebrada.
"""
import argparse
import functools
import glob
import http.server
import os
import socketserver
import sys
import threading
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "_qa"
LARGURAS = (320, 390, 430, 1440)


def chromium():
    cands = sorted(glob.glob(os.path.expanduser(
        "~/Library/Caches/ms-playwright/chromium-1228/chrome-mac*/*.app/Contents/MacOS/*")))
    cands = [c for c in cands if os.access(c, os.X_OK)]
    return cands[0] if cands else None


class Silencioso(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def servidor():
    handler = functools.partial(Silencioso, directory=str(RAIZ))
    # várias conexões ao mesmo tempo: o manual pede dezenas de imagens de uma vez
    socketserver.ThreadingTCPServer.daemon_threads = True
    socketserver.ThreadingTCPServer.request_queue_size = 128
    srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, "http://127.0.0.1:%d/" % srv.server_address[1]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pagina", nargs="?", default="brand-book.html")
    ap.add_argument("--secao", action="append", default=[])
    ap.add_argument("--fases", action="store_true")
    ap.add_argument("--inteira", action="store_true")
    ap.add_argument("--pdf", action="store_true")
    ap.add_argument("--gaveta", action="store_true")
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright

    SAIDA.mkdir(exist_ok=True)
    nome = Path(args.pagina).stem
    srv, base = servidor()
    url = base + args.pagina
    falhas = []
    exe = chromium()
    with sync_playwright() as pw:
        nav = pw.chromium.launch(executable_path=exe) if exe else pw.chromium.launch()

        def abrir(w, h=900, fase=None, movimento="reduce"):
            ctx = nav.new_context(viewport={"width": w, "height": h}, device_scale_factor=2 if w < 800 else 1,
                                  reduced_motion=movimento)
            pg = ctx.new_page()
            erros = []
            pg.on("console", lambda m: erros.append(m.text) if m.type == "error" else None)
            pg.on("pageerror", lambda e: erros.append(str(e)))
            pg.goto(url + ("?fase=%s" % fase if fase else ""), wait_until="networkidle")
            pg.evaluate("document.fonts.ready")
            pg.evaluate("""() => { document.querySelectorAll('img[loading="lazy"]').forEach(i => i.loading = 'eager'); }""")
            pg.wait_for_timeout(250)
            return ctx, pg, erros

        for w in LARGURAS:
            ctx, pg, erros = abrir(w)
            dados = pg.evaluate("""() => {
                const d = document.documentElement;
                const largos = [];
                document.querySelectorAll('body *').forEach(el => {
                  const r = el.getBoundingClientRect();
                  if (r.width && r.right > d.clientWidth + 1) {
                    let p = el.parentElement, recortado = false;
                    while (p) { const s = getComputedStyle(p); if (['auto','scroll','hidden','clip'].includes(s.overflowX)) { recortado = true; break; } p = p.parentElement; }
                    if (!recortado && getComputedStyle(el).position !== 'fixed') largos.push((el.className && el.className.baseVal === undefined ? el.className : el.tagName) + ' ' + Math.round(r.right));
                  }
                });
                const quebradas = [...document.images].filter(i => i.complete && i.naturalWidth === 0).map(i => i.getAttribute('src'));
                return {sw: d.scrollWidth, cw: d.clientWidth, largos: largos.slice(0, 8), quebradas};
            }""")
            ok = dados["sw"] <= dados["cw"]
            print("  %4d px  largura do documento %d  %s" % (w, dados["sw"], "ok" if ok else "ROLAGEM HORIZONTAL"))
            if not ok:
                falhas.append("rolagem horizontal em %d px: %s" % (w, ", ".join(dados["largos"])))
            for q in dados["quebradas"]:
                falhas.append("imagem quebrada em %d px: %s" % (w, q))
            for e in erros:
                falhas.append("console em %d px: %s" % (w, e[:160]))
            if w == 1440 and nome == "brand-book":
                # capa sobre Sálvia (pós-parto): símbolo, nome e descritor em Mar Fundo, ponto Algodão
                cores = pg.evaluate("""() => {
                  const s = document.querySelector('.capa-logo .svg-marca'); if (!s) return null;
                  const f = sel => { const e = s.querySelector(sel); return e ? getComputedStyle(e).fill : null; };
                  const r = document.querySelector('[data-fase="pos-parto"] .cartao .rotulo, .cartao .rotulo');
                  return {tinta: f('.c-tinta'), descritor: f('.c-descritor'), ponto: f('.c-ponto'), rotulo: r ? getComputedStyle(r).color : null};
                }""")
                if cores:
                    if cores["tinta"] != "rgb(16, 58, 64)" or (cores["descritor"] and cores["descritor"] != "rgb(16, 58, 64)"):
                        falhas.append("logotipo da capa fora do esquema sobre-salvia: %s" % cores)
                    if cores["ponto"] != "rgb(242, 240, 235)":
                        falhas.append("ponto do logotipo da capa não é Algodão: %s" % cores["ponto"])
                    if cores["rotulo"] and cores["rotulo"] == "rgb(138, 90, 46)":
                        falhas.append("rótulo de 14 px em Caramelo Tostado sobre Pedra (4,45 para 1) no pós-parto")
            if w in (390, 1440):
                pg.screenshot(path=str(SAIDA / ("%s-%d-capa.png" % (nome, w))))
                if args.inteira:
                    pg.screenshot(path=str(SAIDA / ("%s-%d-inteira.png" % (nome, w))), full_page=True)
                for s in args.secao:
                    el = pg.locator("#" + s)
                    if el.count():
                        el.scroll_into_view_if_needed()
                        pg.wait_for_timeout(200)
                        el.screenshot(path=str(SAIDA / ("%s-%d-%s.png" % (nome, w, s))))
                    else:
                        falhas.append("seção #%s não encontrada" % s)
                # primeira tela depois da capa (sumário lateral + mapa)
                pg.evaluate("(document.getElementById('conteudo') || document.querySelector('main') || document.body).scrollIntoView()")
                pg.wait_for_timeout(250)
                pg.screenshot(path=str(SAIDA / ("%s-%d-conteudo.png" % (nome, w))))
            if w == 390 and args.gaveta:
                pg.evaluate("window.scrollTo(0, document.querySelector('section.secao') ? document.querySelector('section.secao').offsetTop + 50 : 0)")
                pg.wait_for_timeout(200)
                pg.click("[data-gaveta-abrir]")
                pg.wait_for_timeout(500)
                pg.screenshot(path=str(SAIDA / ("%s-390-gaveta.png" % nome)))
            ctx.close()

        if args.fases:
            for f in ("gestacao", "pos-parto", "40-mais"):
                ctx, pg, erros = abrir(1440, fase=f)
                pg.screenshot(path=str(SAIDA / ("%s-1440-fase-%s.png" % (nome, f))))
                alvo = args.secao[0] if args.secao else None
                if alvo and pg.locator("#" + alvo).count():
                    pg.locator("#" + alvo).screenshot(path=str(SAIDA / ("%s-1440-fase-%s-%s.png" % (nome, f, alvo))))
                ctx.close()

        if args.pdf:
            # O PDF sai pelo chromium_headless_shell do Playwright: o Chromium completo em modo
            # headless falha ("Printing failed") em documentos longos como o manual (mais de 200 páginas).
            try:
                nav_pdf = pw.chromium.launch()
            except Exception:
                nav_pdf = nav
            ctx = nav_pdf.new_context(viewport={"width": 1240, "height": 900}, reduced_motion="reduce")
            pg = ctx.new_page()
            pg.goto(url, wait_until="networkidle")
            pg.evaluate("document.fonts.ready")
            pg.evaluate("""() => { document.querySelectorAll('img[loading="lazy"]').forEach(i => i.loading = 'eager'); }""")
            pg.wait_for_timeout(400)
            pg.emulate_media(media="print")
            pg.pdf(path=str(SAIDA / ("%s.pdf" % nome)), format="A4", print_background=True, prefer_css_page_size=True)
            ctx.close()
            if nav_pdf is not nav:
                nav_pdf.close()
            print("  PDF: %s" % (SAIDA / ("%s.pdf" % nome)).relative_to(RAIZ))
        nav.close()
    srv.shutdown()

    print("Capturas em %s/" % SAIDA.relative_to(RAIZ))
    for f in falhas:
        print("  FALHA  %s" % f)
    print("Resultado: %s" % ("aprovado" if not falhas else "reprovado (%d)" % len(falhas)))
    return 0 if not falhas else 1


if __name__ == "__main__":
    sys.exit(main())
