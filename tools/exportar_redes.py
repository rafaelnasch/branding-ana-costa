#!/usr/bin/env python3
"""Gera os PNG padrão de cada modelo do kit-social.html em assets/redes/.

Abre o kit num Chromium sem janela (Playwright), servindo o repositório por HTTP local,
e usa a mesma rotina de exportação do botão "Baixar PNG" (modern-screenshot). Cada
modelo sai com o texto de exemplo, no modo da fase padrão e na resolução da rede.
As capas de destaque saem nas 8 versões e a foto de perfil nas 2.

  python3 tools/exportar_redes.py            gera tudo e grava assets/redes/manifesto.json
  python3 tools/exportar_redes.py --testar   também testa o botão de download e a página em 320 e 390 px

Precisa de: pip install playwright && playwright install chromium (e internet para o CDN).
"""
import argparse
import base64
import functools
import http.server
import json
import struct
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "assets" / "redes"


def servidor():
    class Silencioso(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass

    handler = functools.partial(Silencioso, directory=str(RAIZ))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def dimensoes_png(dados):
    if dados[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("não é PNG")
    return struct.unpack(">II", dados[16:24])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--testar", action="store_true")
    args = ap.parse_args()
    srv = servidor()
    base = f"http://127.0.0.1:{srv.server_address[1]}/kit-social.html?limpo=1"
    SAIDA.mkdir(parents=True, exist_ok=True)
    erros, manifesto = [], []
    with sync_playwright() as p:
        nav = p.chromium.launch()
        pag = nav.new_page(viewport={"width": 1440, "height": 1000}, device_scale_factor=1)
        avisos = []
        pag.on("console", lambda m: avisos.append(m.text) if m.type in ("error", "warning") else None)
        pag.on("pageerror", lambda e: avisos.append(str(e)))
        pag.goto(base, wait_until="networkidle")
        pag.evaluate("() => window.KitSocial.pronto")
        modelos = pag.evaluate("() => window.KitSocial.lista()")
        com_foto = []
        for m in modelos:
            versoes = m["variantes"] or [None]
            # foto de perfil: também nos tamanhos de cada rede (YouTube 800, TikTok 720, WhatsApp 640, LinkedIn 400)
            tamanhos = [t[0] for t in (m.get("tamanhos") or [[m["w"]]])]
            for vr in versoes:
                for tam in tamanhos:
                    if tam != m["w"] and not (vr and vr["id"] == "rosto"):
                        continue
                    mult = tam / m["w"]
                    opc = {"variante": vr["id"]} if vr else {}
                    if mult != 1:
                        opc["mult"] = mult
                    r = pag.evaluate("([id, o]) => window.KitSocial.gerar(id, o)", [m["id"], opc])
                    dados = base64.b64decode(r["png"].split(",", 1)[1])
                    w, h = dimensoes_png(dados)
                    esperado = (round(m["w"] * mult), round(m["h"] * mult))
                    if (w, h) != esperado:
                        erros.append(f"{r['arquivo']}: saiu {w}x{h}, esperado {esperado[0]}x{esperado[1]}")
                    if r["estouro"]:
                        erros.append(f"{r['arquivo']}: {r['estouro']} bloco(s) de texto sem caber")
                    (SAIDA / r["arquivo"]).write_bytes(dados)
                    if r.get("foto"):
                        com_foto.append(r["arquivo"])
                    nome = m["nome"] + (f" · {vr['nome']}" if vr else "") + (f" · {w} px" if mult != 1 else "")
                    manifesto.append({"arquivo": r["arquivo"], "nome": nome, "modelo": m["id"], "largura": w, "altura": h,
                                      "foto": bool(r.get("foto"))})
                    print(f"  {r['arquivo']}  {w}x{h}  {len(dados)//1024} KB" + ("  (com foto)" if r.get("foto") else ""))

        if args.testar:
            # 1. botão de download de verdade
            pag.evaluate("() => window.KitSocial.selecionar('citacao', {})")
            with pag.expect_download() as info:
                pag.click("#ks-exportar")
            d = info.value
            caminho = Path(d.path())
            w, h = dimensoes_png(caminho.read_bytes())
            print(f"  download pelo botão: {d.suggested_filename} {w}x{h}")
            if (w, h) != (1080, 1350):
                erros.append(f"download pelo botão saiu {w}x{h}")
            # dobro
            pag.select_option("#ks-mult", "2")
            with pag.expect_download() as info:
                pag.click("#ks-exportar")
            w, h = dimensoes_png(Path(info.value.path()).read_bytes())
            print(f"  download em dobro: {info.value.suggested_filename} {w}x{h}")
            if (w, h) != (2160, 2700):
                erros.append(f"download em dobro saiu {w}x{h}")
            # 2. sem rolagem horizontal no celular
            for largura in (320, 375, 390, 430):
                cel = nav.new_page(viewport={"width": largura, "height": 800}, device_scale_factor=2)
                cel.goto(base, wait_until="networkidle")
                cel.evaluate("() => window.KitSocial.pronto")
                for mid in ("citacao", "banner", "story-cta"):
                    cel.evaluate(f"() => window.KitSocial.selecionar('{mid}', {{}})")
                    sw = cel.evaluate("() => document.documentElement.scrollWidth")
                    if sw > largura:
                        erros.append(f"rolagem horizontal em {largura}px no modelo {mid}: {sw}px")
                cel.screenshot(path=str(RAIZ / "_qa" / f"kit-social-{largura}.png"), full_page=False)
                cel.close()
        nav.close()
    srv.shutdown()
    # arquivos de versões antigas (nomes que mudaram) saem da pasta
    gerados = {x["arquivo"] for x in manifesto}
    for velho in SAIDA.glob("ana-costa_*.png"):
        if velho.name not in gerados:
            velho.unlink()
            print(f"  removido (nome antigo): {velho.name}")
    # Fotos da Ana (só ela, sem os filhos) entram no repositório: são da própria marca.
    (SAIDA / ".gitignore").unlink(missing_ok=True)
    (SAIDA / "manifesto.json").write_text(json.dumps({"gerado_por": "tools/exportar_redes.py", "arquivos": manifesto}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    graves = [a for a in avisos if "404" not in a]  # 404 esperado: links opcionais (lockup, guia) conferidos por HEAD
    if graves:
        print("Avisos do navegador:", *graves[:10], sep="\n  ")
    if erros:
        print("ERROS:", *erros, sep="\n  ")
        sys.exit(1)
    print(f"{len(manifesto)} arquivos em {SAIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
