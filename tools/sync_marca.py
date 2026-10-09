#!/usr/bin/env python3
"""Copia a marca final da Ana Paula Costa para este repositório (idempotente).

A marca-final pode estar sendo refinada em paralelo. Por isso nenhum asset da marca é
editado à mão aqui: rode este script e ele traz a versão mais nova.

  python3 tools/sync_marca.py              copia o que mudou e mostra o resumo
  python3 tools/sync_marca.py --conferir   só compara (sai com 1 se algo está desatualizado)
  python3 tools/sync_marca.py --origem DIR usa outra pasta marca-final

O que vai para onde
  logo/svg/*.svg                         -> assets/marca/svg/
  logo/png/*.png (menos favicon e og)    -> assets/marca/png/
  logo/png/favicon-*.png + favicon.svg   -> assets/marca/favicon/
  logo/png/og-image-*.png                -> assets/marca/og/
  forma-assinatura/** (svg e png)        -> assets/forma/**
  fontes/*.ttf + OFL-*.txt               -> assets/fontes/
  fontes variáveis                       -> assets/fontes/web/*.woff2 (subconjunto latino, mantém eixos)
  apresentacao.png, mockups.png          -> assets/referencia/
  tokens.json                            -> tokens.json
  tokens.css                             -> tokens.css (caminhos de fonte e da Rota reescritos para assets/)

Só grava quando o conteúdo muda (comparação por SHA-256), então rodar duas vezes seguidas
não altera nada. Arquivo que sumiu da origem é listado como "órfão" e não é apagado
(use --limpar para remover os órfãos das pastas geridas).
"""
import argparse
import hashlib
import io
import re
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ORIGEM_PADRAO = None  # definido por origem_local()


def origem_local(chave, variavel):
    """Pasta de origem: variável de ambiente, depois tools/origens.local.json (fora do git)."""
    import json as _json
    import os as _os

    if _os.environ.get(variavel):
        return Path(_os.environ[variavel])
    arq = Path(__file__).resolve().parent / "origens.local.json"
    if arq.exists():
        valor = _json.loads(arq.read_text(encoding="utf-8")).get(chave)
        if valor:
            return Path(valor)
    return None


ORIGEM_PADRAO = origem_local("marca_final", "ANA_MARCA_FINAL")
# Fontes variáveis que viram woff2 para a web (o resto fica só em .ttf para desktop)
WEB = {
    "Literata[opsz,wght].ttf": "literata-var.woff2",
    "Literata-Italic[opsz,wght].ttf": "literata-italic-var.woff2",
    "AtkinsonHyperlegibleNext[wght].ttf": "atkinson-next-var.woff2",
    "AtkinsonHyperlegibleNext-Italic[wght].ttf": "atkinson-next-italic-var.woff2",
}
# Latim básico e estendido usado no português, pontuação, setas e símbolos comuns
UNICODES = (
    "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0300-0301,U+0303,"
    "U+2000-206F,U+2070-209F,U+20AC,U+2122,U+2190-2199,U+2212,U+2215,U+2248,U+2260,U+2264-2265"
)


def sha(dados):
    return hashlib.sha256(dados).hexdigest()


class Sync:
    def __init__(self, conferir):
        self.conferir = conferir
        self.novos, self.alterados, self.iguais = [], [], 0
        self.destinos = set()

    def gravar(self, destino, dados):
        destino = Path(destino)
        self.destinos.add(destino.resolve())
        if destino.exists() and sha(destino.read_bytes()) == sha(dados):
            self.iguais += 1
            return
        (self.alterados if destino.exists() else self.novos).append(destino.relative_to(RAIZ))
        if not self.conferir:
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_bytes(dados)

    def copiar(self, origem, destino):
        self.gravar(destino, Path(origem).read_bytes())


def woff2(ttf):
    """Gera woff2 com subconjunto latino, mantendo eixos variáveis e recursos tipográficos."""
    from fontTools import subset
    from fontTools.ttLib import TTFont

    opcoes = subset.Options()
    opcoes.flavor = "woff2"
    opcoes.layout_features = ["*"]
    opcoes.name_IDs = ["*"]
    opcoes.name_languages = ["*"]
    opcoes.notdef_outline = True
    opcoes.glyph_names = False
    opcoes.hinting = False
    fonte = TTFont(str(ttf))
    sub = subset.Subsetter(opcoes)
    sub.populate(unicodes=subset.parse_unicodes(UNICODES))
    sub.subset(fonte)
    buf = io.BytesIO()
    fonte.flavor = "woff2"
    fonte.save(buf)
    return buf.getvalue()


def tokens_css(texto):
    """Reescreve caminhos do tokens.css da marca-final para a estrutura deste repositório."""
    for ttf, w2 in WEB.items():
        texto = texto.replace(
            "url('fontes/%s') format('truetype')" % ttf,
            "url('assets/fontes/web/%s') format('woff2'),url('assets/fontes/%s') format('truetype')" % (w2, ttf),
        )
    texto = re.sub(r"url\((['\"]?)fontes/", r"url(\1assets/fontes/", texto)
    texto = re.sub(r"url\((['\"]?)forma-assinatura/", r"url(\1assets/forma/", texto)
    cabeca = (
        "/* Gerado por tools/sync_marca.py a partir da marca-final. Não edite aqui: "
        "edite na origem e rode o script. */\n"
    )
    return cabeca + texto if not texto.startswith("/* Gerado") else texto


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--origem", default=str(ORIGEM_PADRAO) if ORIGEM_PADRAO else None)
    ap.add_argument("--conferir", action="store_true", help="só compara, não grava")
    ap.add_argument("--limpar", action="store_true", help="apaga órfãos nas pastas geridas")
    args = ap.parse_args()
    if not args.origem:
        print("ERRO: defina a pasta de origem com --origem, com a variável de ambiente ou em tools/origens.local.json")
        return 2

    org = Path(args.origem)
    if not (org / "logo" / "svg").is_dir():
        print("ERRO: origem sem logo/svg: %s" % org)
        return 2
    s = Sync(args.conferir)
    A = RAIZ / "assets"

    for f in sorted((org / "logo" / "svg").glob("*.svg")):
        destino = A / "marca" / ("favicon" if f.name == "favicon.svg" else "svg") / f.name
        s.copiar(f, destino)
    for f in sorted((org / "logo" / "png").glob("*.png")):
        if f.name.startswith("favicon"):
            pasta = "favicon"
        elif f.name.startswith("og-"):
            pasta = "og"
        else:
            pasta = "png"
        s.copiar(f, A / "marca" / pasta / f.name)

    forma = org / "forma-assinatura"
    for f in sorted(forma.rglob("*")):
        if f.is_file() and f.suffix.lower() in (".svg", ".png") and not f.name.startswith("."):
            s.copiar(f, A / "forma" / f.relative_to(forma))

    fontes = org / "fontes"
    for f in sorted(fontes.iterdir()):
        if f.suffix.lower() == ".ttf" or (f.name.startswith("OFL") and f.suffix == ".txt"):
            s.copiar(f, A / "fontes" / f.name)
    for ttf, w2 in WEB.items():
        arq = fontes / ttf
        if not arq.exists():
            print("AVISO: fonte variável ausente na origem: %s" % ttf)
            continue
        destino = A / "fontes" / "web" / w2
        carimbo = A / "fontes" / "web" / (w2 + ".origem")
        assinatura = sha(arq.read_bytes()).encode()
        # só regenera o woff2 quando o ttf de origem mudou (woff2 não é byte a byte determinístico
        # entre versões do fontTools)
        if destino.exists() and carimbo.exists() and carimbo.read_bytes() == assinatura:
            s.destinos.update({destino.resolve(), carimbo.resolve()})
            s.iguais += 2
            continue
        s.gravar(destino, woff2(arq))
        s.gravar(carimbo, assinatura)

    for nome in ("apresentacao.png", "mockups.png"):
        if (org / nome).exists():
            s.copiar(org / nome, A / "referencia" / nome)

    s.copiar(org / "tokens.json", RAIZ / "tokens.json")
    s.gravar(RAIZ / "tokens.css", tokens_css((org / "tokens.css").read_text(encoding="utf-8")).encode("utf-8"))

    # órfãos: arquivos nas pastas geridas que a origem não tem mais
    orfaos = []
    for pasta in (A / "marca", A / "forma", A / "fontes", A / "referencia"):
        if pasta.exists():
            for f in pasta.rglob("*"):
                if f.is_file() and f.resolve() not in s.destinos and f.name != ".DS_Store":
                    orfaos.append(f)

    acao = "Conferência" if args.conferir else "Sincronização"
    print("%s da marca-final (%s)" % (acao, org.name))
    print("  iguais: %d · novos: %d · alterados: %d · órfãos: %d"
          % (s.iguais, len(s.novos), len(s.alterados), len(orfaos)))
    for rotulo, lista in (("novo", s.novos), ("alterado", s.alterados)):
        for p in lista[:60]:
            print("  %-9s %s" % (rotulo, p))
        if len(lista) > 60:
            print("  ... e mais %d" % (len(lista) - 60))
    for f in orfaos:
        print("  órfão    %s" % f.relative_to(RAIZ))
        if args.limpar and not args.conferir:
            f.unlink()
    if args.conferir and (s.novos or s.alterados):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
