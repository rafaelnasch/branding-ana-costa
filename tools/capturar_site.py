#!/usr/bin/env python3
"""Captura as telas do site real da Ana para o manual (seção de aplicações).

  python3 tools/capturar_site.py               captura as páginas prontas em 1440 e 390 px
  python3 tools/capturar_site.py --origem DIR  usa outra pasta do site (padrão: ../ana-costa-site/site
                                               ou a chave "site" de tools/origens.local.json)

O que faz
  1. Serve a pasta do site num servidor local e abre cada página no Chromium (Playwright).
  2. Esconde a faixa "Prévia em aprovação" (ela some quando o site vai ao ar).
  3. Só grava a página que está pronta: o título principal precisa estar em Literata e o
     corpo do texto em Atkinson. Página sem estilo é pulada e listada no relatório.
  4. Grava a primeira tela em assets/aplicacoes/site/<pagina>-1440.webp (1440 × 900) e
     <pagina>-390.webp (390 × 844, densidade 2). Só regrava quando a imagem muda.
Rode de novo sempre que o site mudar. Sai com 1 se nenhuma página estiver pronta.
"""
import argparse
import functools
import glob
import hashlib
import http.server
import io
import json
import os
import socketserver
import sys
import threading
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "assets" / "aplicacoes" / "site"
PAGINAS = ("index", "atendimentos", "semana-bem-nutrida", "comunidade", "sobre")
TELAS = ((1440, 900, 1), (390, 844, 2))


def origem_padrao():
    if os.environ.get("ANA_SITE"):
        return Path(os.environ["ANA_SITE"])
    arq = RAIZ / "tools" / "origens.local.json"
    if arq.exists():
        valor = json.loads(arq.read_text(encoding="utf-8")).get("site")
        if valor:
            return Path(valor)
    return RAIZ.parent / "ana-costa-site" / "site"


def chromium():
    cands = sorted(glob.glob(os.path.expanduser(
        "~/Library/Caches/ms-playwright/chromium-*/chrome-mac*/*.app/Contents/MacOS/*")))
    cands = [c for c in cands if os.access(c, os.X_OK)]
    return cands[-1] if cands else None


class Silencioso(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


PRONTA = """() => {
  document.querySelectorAll('body *').forEach(el => {
    if (el.children.length < 4 && /Prévia em aprovação/.test(el.textContent || '') &&
        el.getBoundingClientRect().top < 60 && el.getBoundingClientRect().height < 80) {
      let alvo = el;
      while (alvo.parentElement && alvo.parentElement !== document.body &&
             alvo.parentElement.getBoundingClientRect().height < 80) alvo = alvo.parentElement;
      alvo.style.display = 'none';
    }
  });
  const h1 = document.querySelector('h1');
  const fonte = h1 ? getComputedStyle(h1).fontFamily : '';
  const corpo = getComputedStyle(document.body).fontFamily;
  return {literata: /Literata/i.test(fonte), cabecalho: /Atkinson/i.test(corpo)};
}"""


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--origem", default=None)
    args = ap.parse_args()
    origem = Path(args.origem) if args.origem else origem_padrao()
    if not origem.exists():
        print("Pasta do site não encontrada: %s" % origem)
        return 1
    from PIL import Image
    from playwright.sync_api import sync_playwright

    DESTINO.mkdir(parents=True, exist_ok=True)
    handler = functools.partial(Silencioso, directory=str(origem))
    srv = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:%d/" % srv.server_address[1]
    gravadas, iguais, puladas = [], [], []
    exe = chromium()
    with sync_playwright() as pw:
        nav = pw.chromium.launch(executable_path=exe) if exe else pw.chromium.launch()
        for pagina in PAGINAS:
            if not (origem / (pagina + ".html")).exists():
                puladas.append("%s (não existe)" % pagina)
                continue
            for w, h, dens in TELAS:
                ctx = nav.new_context(viewport={"width": w, "height": h}, device_scale_factor=dens,
                                      reduced_motion="reduce")
                pg = ctx.new_page()
                pg.goto(base + pagina + ".html", wait_until="networkidle")
                pg.evaluate("document.fonts.ready")
                pg.wait_for_timeout(500)
                estado = pg.evaluate(PRONTA)
                if not (estado["literata"] and estado["cabecalho"]):
                    puladas.append("%s %d px (sem estilo)" % (pagina, w))
                    ctx.close()
                    continue
                pg.wait_for_timeout(250)
                png = pg.screenshot()
                ctx.close()
                buf = io.BytesIO()
                Image.open(io.BytesIO(png)).convert("RGB").save(buf, "WEBP", quality=84, method=6)
                dados = buf.getvalue()
                arq = DESTINO / ("%s-%d.webp" % (pagina, w))
                nome = arq.relative_to(RAIZ)
                if arq.exists() and hashlib.sha256(arq.read_bytes()).digest() == hashlib.sha256(dados).digest():
                    iguais.append(str(nome))
                else:
                    arq.write_bytes(dados)
                    gravadas.append("%s (%d KB)" % (nome, len(dados) // 1024))
        nav.close()
    srv.shutdown()
    print("Capturas do site da Ana (%s)" % origem.name)
    for g in gravadas:
        print("  gravada  %s" % g)
    for i in iguais:
        print("  igual    %s" % i)
    for p in puladas:
        print("  pulada   %s" % p)
    return 0 if (gravadas or iguais) else 1


if __name__ == "__main__":
    sys.exit(main())
