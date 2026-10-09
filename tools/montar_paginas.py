#!/usr/bin/env python3
"""Monta as páginas de apoio (index.html, lockup.html, guia-de-uso.html, kit-video.html) a partir dos modelos.

  python3 tools/montar_paginas.py            monta as quatro páginas
  python3 tools/montar_paginas.py --conferir só compara (sai com 1 se alguma página está desatualizada)

Os modelos ficam em tools/modelos/<pagina>.modelo.html. Diretivas (comentários HTML):

  <!--CODIGO:caminho-->          conteúdo do arquivo, escapado, para mostrar dentro de <pre>
  <!--VIVO:caminho-->            conteúdo do arquivo, como está (prévia renderizada)
  <!--DATAURI:caminho-->         data URI em base64 do arquivo (SVG ou PNG)
  <!--RECOLOR:caminho|#A=#B,#C=#D-->  SVG inline decorativo com as cores de preenchimento trocadas
                                 (só cores do tokens.json; o arquivo oficial não muda)

Rode depois de tools/sync_marca.py: o logotipo em código sai sempre da versão mais nova.
Os caminhos são relativos à raiz do repositório. Idempotente: só grava o que mudou.
"""
import argparse
import base64
import html
import mimetypes
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MODELOS = RAIZ / "tools" / "modelos"
PAGINAS = {"lockup.html": "lockup.modelo.html", "guia-de-uso.html": "guia-de-uso.modelo.html",
           "index.html": "index.modelo.html", "kit-video.html": "kit-video.modelo.html"}
DIRETIVA = re.compile(r"<!--(CODIGO|VIVO|DATAURI|RECOLOR):([^>]+?)-->")


def ler(caminho):
    arq = RAIZ / caminho.strip()
    if not arq.is_file():
        raise FileNotFoundError(caminho)
    return arq


def limpo(texto):
    texto = re.sub(r"<\?xml[^>]*>\s*", "", texto)
    return texto.strip("\n") + ("" if texto.endswith("\n") else "")


def recolor(arg):
    caminho, _, trocas = arg.partition("|")
    svg = limpo(ler(caminho).read_text(encoding="utf-8"))
    for par in filter(None, trocas.split(",")):
        de, para = par.split("=")
        svg = re.sub(r'fill="%s"' % re.escape(de.strip()), 'fill="%s"' % para.strip(), svg, flags=re.I)
    svg = re.sub(r"<title>.*?</title>", "", svg, flags=re.S)
    svg = re.sub(r'\s(role|aria-label)="[^"]*"', "", svg)
    return re.sub(r"<svg\b", '<svg aria-hidden="true" focusable="false"', svg, count=1)


def expandir(texto):
    def troca(m):
        tipo, arg = m.group(1), m.group(2)
        if tipo == "RECOLOR":
            return recolor(arg)
        arq = ler(arg)
        if tipo == "DATAURI":
            mime = mimetypes.guess_type(arq.name)[0] or "application/octet-stream"
            return "data:%s;base64,%s" % (mime, base64.b64encode(arq.read_bytes()).decode("ascii"))
        conteudo = limpo(arq.read_text(encoding="utf-8")).rstrip("\n")
        if tipo == "CODIGO":
            return html.escape(conteudo, quote=False)
        # prévia: links de caminho absoluto do site da Ana (ainda sem domínio) não saem da página
        # e as imagens do endereço público do manual abrem pelo caminho local (funciona antes de publicar)
        conteudo = conteudo.replace("https://rafaelnasch.github.io/branding-ana-costa/", "")
        return re.sub(r'href="/[^"]*"', 'href="#conteudo"', conteudo)

    return DIRETIVA.sub(troca, texto)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--conferir", action="store_true")
    args = ap.parse_args()
    desatualizadas = []
    for pagina, modelo in PAGINAS.items():
        arq_modelo = MODELOS / modelo
        if not arq_modelo.exists():
            print("  sem modelo: %s" % modelo)
            continue
        try:
            novo = expandir(arq_modelo.read_text(encoding="utf-8"))
        except FileNotFoundError as e:
            print("ERRO: %s cita arquivo que não existe: %s" % (modelo, e))
            return 2
        destino = RAIZ / pagina
        atual = destino.read_text(encoding="utf-8") if destino.exists() else None
        if atual == novo:
            print("  igual      %s" % pagina)
            continue
        desatualizadas.append(pagina)
        if not args.conferir:
            destino.write_text(novo, encoding="utf-8")
        print("  %s %s (%d KB)" % ("desatual. " if args.conferir else "gravado   ", pagina, len(novo.encode()) // 1024))
    return 1 if (args.conferir and desatualizadas) else 0


if __name__ == "__main__":
    sys.exit(main())
