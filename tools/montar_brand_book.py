#!/usr/bin/env python3
"""Monta o brand-book.html da Ana Paula Costa a partir da casca e dos fragmentos.

  python3 tools/montar_brand_book.py               casca + _fragmentos/sNN-*.html -> brand-book.html
  python3 tools/montar_brand_book.py --exemplo     inclui _fragmentos/exemplo-secao.html (se a seção dele
                                                   ainda não existir como fragmento real)
  python3 tools/montar_brand_book.py --saida X     grava em outro arquivo

O que faz
  1. Lê tools/estrutura.json (partes e seções previstas) e os fragmentos em ordem numérica.
  2. Gera o sumário lateral (<!--INDICE-->), o mapa do manual (<!--MAPA-->) e uma abertura
     antes da primeira seção de cada parte.
  3. Injeta o número da seção (<p class="secao-num">) no cabeçalho e a âncora "#" nos h3.
  4. Troca <span data-svg="assets/...svg"> pelo SVG oficial inline, com as cores do arquivo
     convertidas em classes (c-tinta, c-ponto, c-descritor...) para seguir o modo da fase.
  5. Confere a estrutura (ids, partes, h3 com id sNN-n, links internos) e imprime o relatório.
Sai com 0 só sem erros. Depois rode tools/verificar.py e tools/qa.py.
"""
import argparse
import json
import re
import sys
from html import escape
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FRAG = RAIZ / "_fragmentos"
CLASSES_COR = {
    "#103A40": "c-tinta",
    "#C99A68": "c-ponto",
    "#2F6E60": "c-descritor",
    "#2B2724": "c-grafite",
    "#F2F0EB": "c-claro",
    "#63AF9C": "c-salvia",
}


def texto_puro(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html)).strip()


def svg_inline(caminho, rotulo=None, decorativo=False):
    arq = RAIZ / caminho
    if not arq.exists():
        raise FileNotFoundError(caminho)
    svg = arq.read_text(encoding="utf-8")
    svg = re.sub(r"<\?xml[^>]*>\s*", "", svg)
    svg = re.sub(r"<title>.*?</title>", "", svg, flags=re.S)
    svg = re.sub(r'\s(width|height|role|aria-label)="[^"]*"', "", svg, count=0)

    def cor(m):
        h = m.group(1).upper()
        return 'class="%s"' % CLASSES_COR.get(h, "c-tinta")

    svg = re.sub(r'fill="(#[0-9A-Fa-f]{6})"', cor, svg)
    if decorativo:
        attrs = ' class="svg-marca" aria-hidden="true" focusable="false"'
    else:
        attrs = ' class="svg-marca" role="img" aria-label="%s" focusable="false"' % escape(rotulo or arq.stem, quote=True)
    return re.sub(r"<svg\b", "<svg" + attrs, svg, count=1)


def expandir_svgs(html, erros, onde):
    """Troca <span|div ... data-svg="assets/x.svg" ...></span> pelo SVG oficial inline."""
    def troca(m):
        tag, attrs = m.group(1), m.group(2)
        mc = re.search(r'\sdata-svg="([^"]+)"', attrs)
        caminho = mc.group(1)
        decorativo = "data-decorativo" in attrs
        mr = re.search(r'data-rotulo="([^"]*)"', attrs)
        try:
            svg = svg_inline(caminho, mr.group(1) if mr else None, decorativo)
        except FileNotFoundError:
            erros.append("%s: SVG não encontrado: %s" % (onde, caminho))
            return m.group(0)
        novo = attrs.replace(mc.group(0), ' data-svg-de="%s"' % caminho)
        return "<%s%s>%s</%s>" % (tag, novo, svg, tag)

    return re.sub(r'<(span|div)(\s[^>]*?data-svg="[^"]+"[^>]*)>\s*</\1>', troca, html)


def ler_estrutura():
    dados = json.loads((RAIZ / "tools" / "estrutura.json").read_text(encoding="utf-8"))
    parte_de, previstas = {}, {}
    for p in dados["partes"]:
        for sid, titulo in p["secoes"].items():
            parte_de[sid] = p
            previstas[sid] = titulo
    return dados["partes"], parte_de, previstas


def analisar(nome, html, erros):
    m = re.search(r'<section\b([^>]*)>', html)
    if not m:
        erros.append("%s: sem <section>" % nome)
        return None
    attrs = m.group(1)
    sid = (re.search(r'\bid="([^"]+)"', attrs) or [None, None])[1]
    if not sid or not re.fullmatch(r"s\d{2}", sid):
        erros.append("%s: <section> precisa de id sNN (achei %r)" % (nome, sid))
        return None
    if 'class="secao' not in attrs:
        erros.append("%s: <section> precisa da classe secao" % nome)
    if len(re.findall(r"<section\b", html)) != 1:
        erros.append("%s: um fragmento tem exatamente uma <section>" % nome)
    h2 = re.search(r"<h2\b[^>]*>(.*?)</h2>", html, re.S)
    titulo = (re.search(r'data-titulo="([^"]*)"', attrs) or [None, None])[1] or (texto_puro(h2.group(1)) if h2 else sid)
    if not h2:
        erros.append("%s: falta o <h2> da seção" % nome)
    busca = (re.search(r'data-busca="([^"]*)"', attrs) or [None, ""])[1]
    subs = []
    for mh in re.finditer(r"<h3\b([^>]*)>(.*?)</h3>", html, re.S):
        mid = re.search(r'\bid="([^"]+)"', mh.group(1))
        if not mid:
            erros.append("%s: h3 sem id (%s)" % (nome, texto_puro(mh.group(2))[:50]))
            continue
        if not re.fullmatch(r"%s-\d+" % sid, mid.group(1)):
            erros.append("%s: h3 com id %r (esperado %s-1, %s-2...)" % (nome, mid.group(1), sid, sid))
        subs.append((mid.group(1), texto_puro(mh.group(2))))
    return {"id": sid, "titulo": titulo, "busca": busca, "subs": subs}


def preparar_secao(info, html):
    sid = info["id"]
    n = sid[1:]
    # número da seção no cabeçalho (se o redator não escreveu)
    if 'class="secao-num"' not in html:
        cab = re.search(r'<header class="secao-cabeca">\s*', html)
        if cab:
            mr = re.search(r'<p class="rotulo">(.*?)</p>\s*', html[cab.end():], re.S)
            rot = ""
            if mr and mr.start() == 0:
                rot = mr.group(1).strip()
                html = html[:cab.end()] + html[cab.end() + mr.end():]
            num = '<p class="secao-num"><span class="secao-n">%s</span>%s</p>\n    ' % (
                n, ('<span class="secao-rotulo">%s</span>' % rot) if rot else "")
            html = html[:cab.end()] + num + html[cab.end():]
    # âncora # nos h3
    def ancora(m):
        attrs, conteudo = m.group(1), m.group(2)
        mid = re.search(r'\bid="([^"]+)"', attrs)
        if not mid or 'class="ancora"' in conteudo:
            return m.group(0)
        return '<h3%s>%s<a class="ancora" href="#%s" aria-label="Link para esta parte">#</a></h3>' % (attrs, conteudo, mid.group(1))

    html = re.sub(r"<h3\b([^>]*)>(.*?)</h3>", ancora, html, flags=re.S)
    if "data-titulo=" not in html.split(">", 1)[0] + ">":
        html = re.sub(r"<section\b", '<section data-titulo="%s"' % escape(info["titulo"], quote=True), html, count=1)
    return html


def abertura(parte, presentes):
    itens = "".join(
        '<li><a href="#%s"><span>%s</span>%s</a></li>' % (s["id"], s["id"][1:], escape(s["titulo"])) for s in presentes
    )
    return (
        '<div class="parte-abre" id="parte-%s" role="note" aria-label="Parte %s, %s">\n'
        '  <div class="parte-abre-dentro">\n'
        '    <div>\n'
        '      <p class="parte-n">Parte %s</p>\n'
        '      <p class="parte-titulo">%s</p>\n'
        '      <p class="parte-chamada">%s</p>\n'
        '      <div class="parte-rota"><span data-svg="assets/forma/rota-divisor-curto.svg" data-decorativo></span></div>\n'
        "    </div>\n"
        '    <ol class="parte-lista">%s</ol>\n'
        "  </div>\n"
        "</div>\n"
    ) % (parte["numero"].lower(), parte["numero"], escape(parte["titulo"]), parte["numero"],
         escape(parte["titulo"]), escape(parte["chamada"]), itens)


def indice_html(grupos):
    linhas = []
    for parte, secs in grupos:
        linhas.append('      <div class="indice-parte" data-parte="%s">' % parte["numero"])
        linhas.append('        <p class="indice-parte-rotulo"><b>%s</b>%s</p>' % (parte["numero"], escape(parte["titulo"])))
        linhas.append("        <ol>")
        for s in secs:
            k = " ".join(filter(None, [s["busca"], parte["titulo"]]))
            subs = ""
            if s["subs"]:
                subs = '<ol class="subs">' + "".join(
                    '<li><a href="#%s"><span>%s</span></a></li>' % (i, escape(t)) for i, t in s["subs"]
                ) + "</ol>"
            linhas.append(
                '          <li data-k="%s"><a href="#%s"><span class="n">%s</span><span>%s</span></a>%s</li>'
                % (escape(k, quote=True), s["id"], s["id"][1:], escape(s["titulo"]), subs)
            )
        linhas.append("        </ol>")
        linhas.append("      </div>")
    return "\n".join(linhas)


def mapa_html(grupos):
    cartoes = []
    for parte, secs in grupos:
        itens = "".join('<li><a href="#%s"><span>%s</span>%s</a></li>' % (s["id"], s["id"][1:], escape(s["titulo"])) for s in secs)
        cartoes.append(
            '<div class="mapa-parte"><p class="mapa-parte-n">Parte %s</p><h3>%s</h3><ol>%s</ol></div>'
            % (parte["numero"], escape(parte["titulo"]), itens)
        )
    return (
        '<section class="mapa" id="mapa" aria-labelledby="mapa-titulo">\n'
        '  <div class="mapa-cabeca"><h2 id="mapa-titulo">O que tem neste manual</h2>'
        "<p>Cada seção abre pelo endereço da página com #sNN (por exemplo, #s09). "
        "Use a busca do sumário ou a tecla / para achar um assunto.</p></div>\n"
        '  <div class="mapa-grade">%s</div>\n'
        "</section>\n"
    ) % "".join(cartoes)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--exemplo", action="store_true")
    ap.add_argument("--saida", default=str(RAIZ / "brand-book.html"))
    args = ap.parse_args()

    erros, avisos = [], []
    partes, parte_de, previstas = ler_estrutura()
    casca = (FRAG / "00-casca.html").read_text(encoding="utf-8")
    for marca in ("<!--SECOES-->", "<!--INDICE-->", "<!--MAPA-->"):
        if casca.count(marca) != 1:
            print("ERRO: a casca precisa ter exatamente um %s" % marca)
            return 1

    arquivos = sorted(FRAG.glob("s[0-9][0-9]-*.html"))
    fragmentos = []
    for arq in arquivos:
        html = arq.read_text(encoding="utf-8").strip()
        info = analisar(arq.name, html, erros)
        if not info:
            continue
        if not arq.name.startswith(info["id"] + "-"):
            erros.append("%s: o nome do arquivo deve começar com o id da seção (%s-)" % (arq.name, info["id"]))
        fragmentos.append((arq.name, info, html))
    if args.exemplo:
        ex = FRAG / "exemplo-secao.html"
        if ex.exists():
            html = ex.read_text(encoding="utf-8").strip()
            info = analisar(ex.name, html, erros)
            if info and info["id"] not in {f[1]["id"] for f in fragmentos}:
                fragmentos.append((ex.name, info, html))
            elif info:
                avisos.append("exemplo-secao.html ignorado: %s já existe como fragmento real" % info["id"])
        else:
            avisos.append("--exemplo pedido, mas _fragmentos/exemplo-secao.html não existe")
    fragmentos.sort(key=lambda f: f[1]["id"])

    vistos = {}
    for nome, info, _ in fragmentos:
        if info["id"] in vistos:
            erros.append("seção %s repetida em %s e %s" % (info["id"], vistos[info["id"]], nome))
        vistos[info["id"]] = nome
        if info["id"] not in parte_de:
            erros.append("%s: seção %s não está em tools/estrutura.json" % (nome, info["id"]))
    faltam = [sid for sid in previstas if sid not in vistos]
    if faltam:
        avisos.append("seções previstas sem fragmento (%d): %s" % (len(faltam), ", ".join(faltam)))

    # agrupa por parte, na ordem da estrutura
    grupos = []
    for p in partes:
        secs = [f[1] for f in fragmentos if f[1]["id"] in p["secoes"]]
        if secs:
            grupos.append((p, secs))

    corpo, parte_atual = [], None
    for nome, info, html in fragmentos:
        p = parte_de.get(info["id"])
        if p and p is not parte_atual:
            parte_atual = p
            presentes = next(s for pp, s in grupos if pp is p)
            corpo.append(abertura(p, presentes))
        corpo.append("<!-- fragmento %s -->\n%s\n" % (nome, preparar_secao(info, html)))

    html = (casca.replace("<!--INDICE-->", indice_html(grupos))
                 .replace("<!--MAPA-->", mapa_html(grupos) if grupos else "")
                 .replace("<!--SECOES-->", "\n".join(corpo)))
    versao = json.loads((RAIZ / "tokens.json").read_text(encoding="utf-8")).get("versao", "")
    num, _, data = versao.partition(" · ")
    html = html.replace("{{VERSAO}}", num.strip() or "1").replace("{{DATA}}", data.strip() or "")
    if "{{" in re.sub(r"<script\b.*?</script>", "", html, flags=re.S):
        erros.append("marcador {{...}} não resolvido no manual")
    html = expandir_svgs(html, erros, "montagem")

    # conferências de estrutura
    sem_script = re.sub(r"<script\b.*?</script>", "", html, flags=re.S)
    ids = re.findall(r'\bid="([^"]+)"', re.sub(r"<svg\b.*?</svg>", "", sem_script, flags=re.S))
    for i in sorted(set(ids)):
        if ids.count(i) > 1:
            erros.append("id repetido: %s (%d vezes)" % (i, ids.count(i)))
    for alvo in set(re.findall(r'href="#([^"]+)"', sem_script)):
        if alvo not in ids:
            erros.append("link interno sem destino: #%s" % alvo)
    if html.count("<h1") != 1:
        erros.append("o manual tem %d h1 (esperado 1, o da capa)" % html.count("<h1"))
    for nome, info, frag in fragmentos:
        if 'class="resumo"' not in frag:
            avisos.append("%s sem bloco 'Em um minuto' (.resumo)" % info["id"])

    saida = Path(args.saida)
    saida.write_text(html, encoding="utf-8")
    print("Montagem do manual da Ana Paula Costa")
    print("  saída: %s (%d KB)" % (saida.relative_to(RAIZ) if saida.is_relative_to(RAIZ) else saida, len(html.encode()) // 1024))
    print("  seções: %d de %d previstas · partes com conteúdo: %d" % (len(fragmentos), len(previstas), len(grupos)))
    for a in avisos:
        print("  AVISO  %s" % a)
    for e in erros:
        print("  ERRO   %s" % e)
    print("Resultado: %s (%d erros, %d avisos)" % ("aprovado" if not erros else "reprovado", len(erros), len(avisos)))
    return 0 if not erros else 1


if __name__ == "__main__":
    sys.exit(main())
