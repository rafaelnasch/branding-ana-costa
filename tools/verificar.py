#!/usr/bin/env python3
"""Gate de aceite do repositório da marca Ana Paula Costa (público, GitHub Pages).

  python3 tools/verificar.py                  todos os HTML da raiz + textos do repositório
  python3 tools/verificar.py brand-book.html  só esses arquivos HTML (mais os textos)
  python3 tools/verificar.py --fragmentos     confere também _fragmentos/sNN-*.html isolados

Itens
  1  HTML: analisado com html5lib (algoritmo do navegador); um h1 por página; ids únicos;
     links internos (#id e pagina.html#id) com destino; arquivos locais (src, href, srcset,
     data-svg-de) existem; toda <img> tem alt e, de preferência, width e height.
  2  Contraste: todo .par (data-texto, data-fundo, data-razao, data-nivel) confere com o
     cálculo de luminância das diretrizes de acessibilidade web (tolerância de 0,02) e o
     nível declarado bate com a razão (AAA 7+, AA 4,5+, grande 3+, decorativo abaixo de 3,
     proibido abaixo de 1,5).
  3  Cor: todo HEX em CSS, atributo style e SVG inline pertence ao tokens.json
     (preto #000000 e branco #FFFFFF só nas versões oficiais monocromáticas).
  4  Texto: nenhum travessão (U+2014, U+2013) no texto visível nem em alt, title,
     aria-label e placeholder; nenhum marcador {{...}} esquecido.
  5  Dado interno: nenhum termo de tools/termos-proibidos.txt (arquivo local, fora do git)
     em HTML, Markdown, JSON, YAML, CSS ou JS do repositório. "GrowAI" só é aceito dentro
     do rodapé com data-credito ou na frase de crédito "criado pela GrowAI".
  6  Fragmentos: CSS em <style data-fragmento="sNN"> só com seletores .sNN- e até 80 linhas;
     cada seção com h2, h3 com id sNN-n e bloco "Em um minuto" (aviso).
  7  Pendências: todo data-p e todo "P n" citado existe em references/pendencias.md
     (aviso enquanto o arquivo não existir).
  8  Fatos e regras: nenhuma frase vetada (fato não comprovado, preço não lançado) em texto
     do repositório; legendas de exemplo (.srt) sem orientação de dose de suplemento.
Sai com 0 só quando nada falha. A conferência no navegador é tools/qa.py.
"""
import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

RAIZ = Path(__file__).resolve().parent.parent
TRAVESSOES = {"—": "U+2014", "–": "U+2013"}
VAZIOS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
ATRIBUTOS_TEXTO = ("alt", "title", "aria-label", "placeholder", "data-titulo", "content")
IGNORAR_PASTAS = {"_qa", ".git", "node_modules", "__pycache__", "dist-skill"}
TEXTOS = {".md", ".json", ".yaml", ".yml", ".css", ".js", ".txt", ".html", ".svg", ".py"}
LOCAIS = {"tools/termos-proibidos.txt", "tools/origens.local.json", "tools/verificar.py"}
CREDITO = re.compile(r"(criad[oa]|desenvolvid[oa]) pela GrowAI", re.I)


# ---------------------------------------------------------------- contraste
def _lin(c):
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminancia(h):
    h = h.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def razao(a, b):
    la, lb = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def nivel_de(r):
    if r >= 7:
        return {"AAA"}
    if r >= 4.5:
        return {"AA"}
    if r >= 3:
        return {"grande", "AA-grande"}
    if r >= 1.5:
        return {"decorativo"}
    return {"proibido", "decorativo"}


# ---------------------------------------------------------------- leitura
def hex_dos_tokens():
    texto = (RAIZ / "tokens.json").read_text(encoding="utf-8")
    return {h.upper() for h in re.findall(r"#[0-9A-Fa-f]{6}\b", texto)}


def termos_proibidos():
    arq = RAIZ / "tools" / "termos-proibidos.txt"
    regras = []
    if not arq.exists():
        return None
    for linha in arq.read_text(encoding="utf-8").splitlines():
        if not linha.strip() or linha.lstrip().startswith("#"):
            continue
        rx, _, motivo = linha.partition("\t")
        regras.append((re.compile(rx.strip(), re.I), motivo.strip() or rx.strip()))
    return regras


def pendencias_validas():
    arq = RAIZ / "references" / "pendencias.md"
    if not arq.exists():
        return None
    return set(re.findall(r"\bP\s?(\d+)\b", arq.read_text(encoding="utf-8")))


class Leitor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pilha = []
        self.ids = []
        self.hrefs = []
        self.locais = []
        self.imgs = []
        self.h1 = 0
        self.pares = []
        self.textos = []  # (linha, texto, no_credito, origem)
        self.em_bruto = 0
        self.secoes = {}
        self.sec = None

    def _credito(self):
        return any(c for _, c in self.pilha)

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        ln = self.getpos()[0]
        if "id" in a:
            self.ids.append((a["id"], ln))
        if tag == "h1":
            self.h1 += 1
        if tag == "a" and a.get("href"):
            self.hrefs.append((a["href"], ln))
        for chave in ("src", "data-svg-de", "poster"):
            if a.get(chave):
                self.locais.append((a[chave], ln))
        if tag in ("a", "link") and a.get("href"):
            self.locais.append((a["href"], ln))
        if a.get("srcset"):
            for parte in a["srcset"].split(","):
                if parte.strip():
                    self.locais.append((parte.strip().split()[0], ln))
        if tag == "img":
            self.imgs.append((a, ln))
        if "par" in a.get("class", "").split():
            self.pares.append((a, ln))
        if tag == "section" and re.fullmatch(r"s\d{2}", a.get("id", "")):
            self.sec = a["id"]
            self.secoes[self.sec] = {"h2": 0, "resumo": False, "h3": []}
        if self.sec:
            if tag == "h2":
                self.secoes[self.sec]["h2"] += 1
            if tag == "h3":
                self.secoes[self.sec]["h3"].append(a.get("id"))
            if "resumo" in a.get("class", "").split():
                self.secoes[self.sec]["resumo"] = True
        if tag in ("script", "style"):
            self.em_bruto += 1
        credito = "data-credito" in a
        for at in ATRIBUTOS_TEXTO:
            if a.get(at) and not (tag == "meta" and at == "content" and a.get("name") not in ("description",) and a.get("property") not in ("og:title", "og:description")):
                self.textos.append((ln, a[at], credito or self._credito(), "atributo %s" % at))
        if tag not in VAZIOS:
            self.pilha.append((tag, credito))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VAZIOS and self.pilha and self.pilha[-1][0] == tag:
            self.pilha.pop()

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.em_bruto = max(0, self.em_bruto - 1)
        if tag == "section":
            self.sec = None
        for i in range(len(self.pilha) - 1, -1, -1):
            if self.pilha[i][0] == tag:
                del self.pilha[i:]
                break

    def handle_data(self, data):
        if self.em_bruto or not data.strip():
            return
        self.textos.append((self.getpos()[0], data, self._credito(), "texto"))


# ---------------------------------------------------------------- conferências
def conferir_html(arq, todos_ids, erros, avisos, cores, termos, pends):
    rel = arq.relative_to(RAIZ)
    html = arq.read_text(encoding="utf-8")
    fragmento = arq.parent.name == "_fragmentos"

    # 1. análise pelo algoritmo do navegador
    try:
        import html5lib

        parser = html5lib.HTMLParser(strict=False, namespaceHTMLElements=False)
        parser.parse(html if not fragmento else "<!doctype html><html><body>%s</body></html>" % html)
        for pos, cod, dados in parser.errors:
            if cod in ("unexpected-end-tag", "end-tag-too-early", "unexpected-start-tag", "duplicate-attribute",
                       "eof-in-tag", "unexpected-end-tag-before-html", "non-void-element-with-trailing-solidus"):
                erros.append("%s:%s HTML: %s %s" % (rel, pos[0], cod, dados.get("name", "") if isinstance(dados, dict) else ""))
    except ImportError:
        avisos.append("html5lib ausente: análise de HTML pulada (pip install html5lib)")

    p = Leitor()
    p.feed(html)
    if not fragmento and p.h1 != 1:
        erros.append("%s: %d h1 (esperado 1)" % (rel, p.h1))
    vistos = {}
    for i, ln in p.ids:
        vistos.setdefault(i, []).append(ln)
    for i, lns in vistos.items():
        if len(lns) > 1:
            erros.append("%s: id repetido %r nas linhas %s" % (rel, i, ", ".join(map(str, lns))))
    for href, ln in p.hrefs:
        u = urlparse(href)
        if u.scheme or href.startswith(("mailto:", "tel:", "//")):
            continue
        if href.startswith("#") and len(href) > 1 and not fragmento:
            if href[1:] not in vistos:
                erros.append("%s:%d link #%s sem destino" % (rel, ln, href[1:]))
        elif "#" in href and not href.startswith("#"):
            pag, ancora = href.split("#", 1)
            destino = (arq.parent / unquote(pag)).resolve()
            if destino.exists() and ancora and destino in todos_ids and ancora not in todos_ids[destino]:
                erros.append("%s:%d link %s: âncora inexistente em %s" % (rel, ln, href, pag))
    for caminho, ln in p.locais:
        u = urlparse(caminho)
        if u.scheme or caminho.startswith(("#", "mailto:", "tel:", "data:", "//")) or "{{" in caminho:
            continue
        alvo = (arq.parent / unquote(u.path)).resolve() if not fragmento else (RAIZ / unquote(u.path)).resolve()
        if u.path and not alvo.exists():
            erros.append("%s:%d arquivo local inexistente: %s" % (rel, ln, caminho))
    for a, ln in p.imgs:
        if "alt" not in a:
            erros.append("%s:%d <img> sem alt (%s)" % (rel, ln, a.get("src", "")[:60]))
        elif not a["alt"].strip() and a.get("aria-hidden") != "true" and a.get("role") != "presentation":
            avisos.append("%s:%d <img> com alt vazio sem aria-hidden: confirme que é decorativa" % (rel, ln))
        if not (a.get("width") and a.get("height")):
            avisos.append("%s:%d <img> sem width/height (a página pula ao carregar)" % (rel, ln))

    # 2. contraste
    for a, ln in p.pares:
        t, f, r, nv = a.get("data-texto", ""), a.get("data-fundo", ""), a.get("data-razao", ""), a.get("data-nivel", "")
        if not (re.fullmatch(r"#[0-9A-Fa-f]{6}", t) and re.fullmatch(r"#[0-9A-Fa-f]{6}", f)):
            erros.append("%s:%d .par sem data-texto/data-fundo em HEX" % (rel, ln))
            continue
        real = razao(t, f)
        try:
            dec = float(r.replace(",", "."))
            if abs(dec - real) > 0.02:
                erros.append("%s:%d contraste %s sobre %s declarado %s, calculado %.2f" % (rel, ln, t, f, r, real))
        except ValueError:
            erros.append("%s:%d .par sem data-razao numérica" % (rel, ln))
        if nv and nv not in nivel_de(real):
            erros.append("%s:%d contraste %s sobre %s = %.2f: nível declarado %r não confere (%s)"
                         % (rel, ln, t, f, real, nv, "/".join(sorted(nivel_de(real)))))
        for cor in (t, f):
            if cor.upper() not in cores:
                erros.append("%s:%d .par usa %s, fora dos tokens" % (rel, ln, cor))

    # 3. HEX fora dos tokens (CSS, style, SVG inline)
    trechos = [(m.start(1), m.group(1)) for m in re.finditer(r"<style\b[^>]*>(.*?)</style>", html, re.S)]
    trechos += [(m.start(1), m.group(1)) for m in re.finditer(r'\bstyle="([^"]*)"', html)]
    trechos += [(m.start(), m.group(0)) for m in re.finditer(r"<svg\b.*?</svg>", html, re.S)]
    trechos += [(m.start(1), m.group(1)) for m in re.finditer(r'\bdata-(?:texto|fundo|copiar)="([^"]*)"', html)]
    for base, trecho in trechos:
        for h in re.finditer(r"(?:#|%23)([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})\b", trecho):
            cor = "#" + h.group(1).upper()
            if len(cor) == 4:
                cor = "#" + "".join(c * 2 for c in cor[1:])
            if cor not in cores:
                ln = html.count("\n", 0, base + h.start()) + 1
                erros.append("%s:%d HEX fora dos tokens: %s" % (rel, ln, cor))

    # 4 e 5. texto visível
    for ln, txt, credito, origem in p.textos:
        for ch, nome in TRAVESSOES.items():
            if ch in txt:
                erros.append("%s:%d travessão %s (%s): %s" % (rel, ln, nome, origem, txt.strip()[:70]))
        if "{{" in txt and "}}" in txt:
            erros.append("%s:%d marcador esquecido (%s): %s" % (rel, ln, origem, txt.strip()[:70]))
        if termos:
            for rx, motivo in termos:
                for m in rx.finditer(txt):
                    if m.group(0).lower() == "growai" and (credito or CREDITO.search(txt)):
                        continue
                    erros.append("%s:%d dado interno (%s) em %s: %s" % (rel, ln, motivo, origem, txt.strip()[:80]))

    # 6. fragmentos
    for m in re.finditer(r'<style\b[^>]*data-fragmento="(s\d{2})"[^>]*>(.*?)</style>', html, re.S):
        frag, css = m.group(1), m.group(2)
        linhas = [l for l in css.strip().splitlines() if l.strip()]
        if len(linhas) > 80:
            erros.append("%s: CSS do fragmento %s com %d linhas (máximo 80)" % (rel, frag, len(linhas)))
        sem = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
        sem = re.sub(r"@media[^{]*\{", "", sem)
        for seletor in re.findall(r"([^{}]+)\{", sem):
            seletor = seletor.strip()
            if not seletor or seletor.startswith(("@", "from", "to")) or re.fullmatch(r"[\d.%,\s]+", seletor):
                continue
            for parte in seletor.split(","):
                if ("." + frag + "-") not in parte:
                    erros.append("%s: seletor sem prefixo .%s- no fragmento: %s" % (rel, frag, parte.strip()[:60]))
    for sid, d in p.secoes.items():
        if d["h2"] != 1:
            erros.append("%s: seção %s com %d h2 (esperado 1)" % (rel, sid, d["h2"]))
        for h in d["h3"]:
            if not h or not re.fullmatch(r"%s-\d+" % sid, h):
                erros.append("%s: seção %s com h3 de id %r (use %s-1, %s-2...)" % (rel, sid, h, sid, sid))
        if not d["resumo"]:
            avisos.append("%s: seção %s sem bloco 'Em um minuto'" % (rel, sid))

    # 7. pendências
    citadas = set(re.findall(r'data-p="(\d+)"', html)) | set(re.findall(r"\bPend[eê]ncia P\s?(\d+)\b", html))
    if pends is None:
        if citadas:
            avisos.append("%s: cita pendências %s, mas references/pendencias.md ainda não existe"
                          % (rel, ", ".join("P" + c for c in sorted(citadas, key=int))))
    else:
        for c in sorted(citadas - pends, key=int):
            erros.append("%s: pendência P%s não está em references/pendencias.md" % (rel, c))
    return vistos


# Frases que já saíram do manual por não terem fonte ou por serem decisão comercial não lançada.
VETADAS = [
    (re.compile(r"oficial da Marinha", re.I), "posto de oficial não comprovado"),
    (re.compile(r"qualquer cidade do Brasil", re.I), "alcance do atendimento não confirmado"),
    (re.compile(r"vive as fases que atende", re.I), "vivência do 40+ que a Ana não tem"),
    (re.compile(r"R\$(\s|&nbsp;)*(49,90|39,90|478,80)"), "preço da Comunidade paga ainda não lançado (P12)"),
]
SRT_VETADAS = [(re.compile(r"\bdoses?\b", re.I), "orientação de dose em legenda de exemplo")]


def conferir_fatos(erros):
    """Item 8: frases vetadas em todos os textos e termos proibidos nas legendas .srt."""
    for arq in sorted(RAIZ.rglob("*")):
        if not arq.is_file():
            continue
        rel = arq.relative_to(RAIZ)
        if set(rel.parts) & IGNORAR_PASTAS or str(rel) in LOCAIS:
            continue
        suf = arq.suffix.lower()
        if suf not in TEXTOS and suf != ".srt":
            continue
        if arq.stat().st_size > 3_000_000:
            continue
        texto = arq.read_text(encoding="utf-8", errors="ignore")
        regras = VETADAS + (SRT_VETADAS if suf == ".srt" else [])
        for n, linha in enumerate(texto.splitlines(), 1):
            for rx, motivo in regras:
                if rx.search(linha):
                    erros.append("%s:%d %s: %s" % (rel, n, motivo, linha.strip()[:80]))


def conferir_textos(erros, termos):
    """Termos proibidos e travessões fora do HTML (Markdown, JSON, YAML, CSS, JS, Python)."""
    if not termos:
        return
    for arq in sorted(RAIZ.rglob("*")):
        if not arq.is_file() or arq.suffix.lower() not in TEXTOS or arq.suffix.lower() == ".html":
            continue
        rel = arq.relative_to(RAIZ)
        if set(rel.parts) & IGNORAR_PASTAS or str(rel) in LOCAIS:
            continue
        if arq.stat().st_size > 2_000_000:
            continue
        texto = arq.read_text(encoding="utf-8", errors="ignore")
        for n, linha in enumerate(texto.splitlines(), 1):
            for rx, motivo in termos:
                for m in rx.finditer(linha):
                    if m.group(0).lower() == "growai" and CREDITO.search(linha):
                        continue
                    erros.append("%s:%d dado interno (%s): %s" % (rel, n, motivo, linha.strip()[:80]))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("arquivos", nargs="*")
    ap.add_argument("--fragmentos", action="store_true")
    args = ap.parse_args()

    erros, avisos = [], []
    cores = hex_dos_tokens()
    cores_oficiais = cores | {"#000000", "#FFFFFF"}
    termos = termos_proibidos()
    if termos is None:
        avisos.append("tools/termos-proibidos.txt ausente: o item 5 (dado interno) não foi conferido")
    pends = pendencias_validas()

    if args.arquivos:
        paginas = [(Path(a) if Path(a).is_absolute() else (Path.cwd() / a)).resolve() for a in args.arquivos]
        paginas = [p if p.exists() else (RAIZ / a) for p, a in zip(paginas, args.arquivos)]
    else:
        paginas = sorted(p for p in RAIZ.glob("*.html") if not p.name.startswith("_"))
    if args.fragmentos:
        paginas += sorted((RAIZ / "_fragmentos").glob("s[0-9][0-9]-*.html"))

    todos_ids = {}
    for pg in paginas:
        txt = pg.read_text(encoding="utf-8")
        todos_ids[pg.resolve()] = set(re.findall(r'\bid="([^"]+)"', txt))
    for pg in paginas:
        conferir_html(pg, todos_ids, erros, avisos, cores_oficiais if pg.name.startswith(("logo", "lockup")) else cores, termos, pends)
    conferir_textos(erros, termos)
    conferir_fatos(erros)

    print("Verificação do repositório da marca Ana Paula Costa")
    print("  páginas: %s" % ", ".join(str(p.relative_to(RAIZ)) for p in paginas) if paginas else "  páginas: nenhuma")
    for a in avisos:
        print("  AVISO  %s" % a)
    for e in erros:
        print("  ERRO   %s" % e)
    print("Resultado: %s (%d erros, %d avisos)" % ("aprovado" if not erros else "reprovado", len(erros), len(avisos)))
    return 0 if not erros else 1


if __name__ == "__main__":
    sys.exit(main())
