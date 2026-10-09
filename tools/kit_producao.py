#!/usr/bin/env python3
"""Pacote de produção: ajuste de cor (LUT), zona segura, legenda e paleta para editores.

  python3 tools/kit_producao.py            gera tudo em assets/producao/
  python3 tools/kit_producao.py --so lut   só uma parte (lut | zona | legenda | paleta)

O que sai
  cor/      Ana-Paula-Costa-Luz-de-Janela.cube (LUT 3D de 33 pontos) + prévia antes e depois
  zona-segura/  camadas PNG transparentes 1080 × 1920 para pôr por cima do vídeo e ocultar antes de exportar
  legenda/  exemplo .srt, estilo em JSON e PNG de referência (limpo e com medidas)
  paleta/   .ase (Adobe), .gpl (GIMP, Inkscape, Krita), .txt com códigos e PNG de amostras

As cores vêm de tokens.json (rode antes tools/sync_marca.py). A prévia da LUT é aplicada
pelo próprio ffmpeg (filtro lut3d) para provar que o arquivo .cube abre nos editores.
"""
import argparse
import glob
import json
import os
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "assets" / "producao"
FONTES = RAIZ / "assets" / "fontes"
FOTOS = RAIZ / "assets" / "fotos" / "1600"
TOKENS = json.loads((RAIZ / "tokens.json").read_text(encoding="utf-8"))
C = {k: v["hex"] for k, v in TOKENS["cores"].items()}
C.update({k: v["hex"] for k, v in TOKENS["cores_derivadas"].items()})

LUT_NOME = "Ana-Paula-Costa-Luz-de-Janela"
# fotos só da Ana, sozinha (regra do acervo): janela, blusa caramelo e evento (modo 40+)
FOTOS_PREVIA = [
    ("ana-04-janela-sorrindo", "Luz de janela"),
    ("ana-14-retrato-blusa-caramelo", "Blusa caramelo"),
    ("ana-11-evento-mao-no-queixo", "Evento, fundo escuro"),
]


def chromium():
    cands = sorted(glob.glob(os.path.expanduser(
        "~/Library/Caches/ms-playwright/chromium-*/chrome-mac*/*.app/Contents/MacOS/*")))
    cands = [c for c in cands if os.access(c, os.X_OK)]
    return cands[-1] if cands else None


def css_base():
    f = FONTES.as_uri()
    return f"""
@font-face{{font-family:'Literata';src:url('{f}/Literata[opsz,wght].ttf');font-weight:200 900}}
@font-face{{font-family:'Literata';src:url('{f}/Literata-Italic[opsz,wght].ttf');font-weight:200 900;font-style:italic}}
@font-face{{font-family:'Ana Numerais';src:url('{f}/Literata[opsz,wght].ttf');font-weight:200 900;unicode-range:U+0030-0039}}
@font-face{{font-family:'Atkinson Hyperlegible Next';src:url('{f}/AtkinsonHyperlegibleNext[wght].ttf');font-weight:200 800}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{background:transparent}}
body{{font-family:'Ana Numerais','Atkinson Hyperlegible Next',sans-serif;color:{C['grafite']}}}
.t{{font-family:'Literata',serif;font-weight:580;font-variation-settings:'opsz' 60;color:{C['mar']};letter-spacing:-.005em}}
.r{{font-weight:600;text-transform:uppercase;letter-spacing:.14em}}
"""


class Render:
    def __init__(self):
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        self.br = self._pw.chromium.launch(executable_path=chromium())
        self.tmp = Path(tempfile.mkdtemp())

    def png(self, corpo, w, h, saida, transparente=False):
        html = self.tmp / "p.html"
        altura = f"height:{h}px;" if h else ""
        html.write_text(f"<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'><style>{css_base()}"
                        f"html,body{{width:{w}px;{altura}overflow:hidden}}</style></head><body>{corpo}</body></html>",
                        encoding="utf-8")
        pg = self.br.new_page(viewport={"width": w, "height": h or 800})
        pg.goto(html.as_uri())
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(150)
        if h is None:  # altura do conteúdo
            alto = pg.evaluate("document.body.scrollHeight")
            pg.set_viewport_size({"width": w, "height": alto})
            pg.wait_for_timeout(50)
        Path(saida).parent.mkdir(parents=True, exist_ok=True)
        pg.screenshot(path=str(saida), omit_background=transparente, type="png")
        pg.close()

    def fechar(self):
        self.br.close()
        self._pw.stop()
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)


def otimizar_png(caminho):
    from PIL import Image
    im = Image.open(caminho)
    im.save(caminho, optimize=True)


# ---------------------------------------------------------------- LUT

def lut_cor(r, g, b):
    """Ajuste da marca: temperatura levemente quente, contraste suave, pretos sem esmagar.
    Branco continua branco (o aquecimento some nas pontas) e a pele continua dela."""
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    # curva em S suave na luminância
    s = y + 0.22 * y * (1 - y) * (2 * y - 1)
    # pretos levantados e altas luzes que não estouram
    s = 0.022 + 0.968 * s
    d = s - y
    r, g, b = r + d, g + d, b + d
    # aquecimento só nos tons médios (peso 0 no preto e no branco)
    w = 4 * y * (1 - y)
    r += 0.020 * w
    g += 0.005 * w
    b -= 0.026 * w
    # saturação um toque abaixo, para o aquecimento não deixar a pele laranja
    y2 = 0.2126 * r + 0.7152 * g + 0.0722 * b
    sat = 0.96
    r, g, b = (y2 + (c - y2) * sat for c in (r, g, b))
    return tuple(min(1.0, max(0.0, c)) for c in (r, g, b))


def gerar_lut():
    pasta = SAIDA / "cor"
    pasta.mkdir(parents=True, exist_ok=True)
    n = 33
    linhas = [f'TITLE "{LUT_NOME}"',
              "# Ana Paula Costa - Nutricionista - ajuste de cor da marca (v1)",
              "# Temperatura levemente quente, contraste suave, pretos sem esmagar. Rec.709 / sRGB.",
              "# Aplicar depois da correcao basica (exposicao e balanco de branco), intensidade de 60 a 100 por cento.",
              f"LUT_3D_SIZE {n}", "DOMAIN_MIN 0.0 0.0 0.0", "DOMAIN_MAX 1.0 1.0 1.0", ""]
    for bi in range(n):
        for gi in range(n):
            for ri in range(n):
                r, g, b = lut_cor(ri / (n - 1), gi / (n - 1), bi / (n - 1))
                linhas.append(f"{r:.6f} {g:.6f} {b:.6f}")
    cube = pasta / f"{LUT_NOME}.cube"
    cube.write_text("\n".join(linhas) + "\n", encoding="ascii")
    return cube


def previa_lut(rd, cube):
    from PIL import Image
    pasta = SAIDA / "cor"
    tmp = rd.tmp
    pares = []
    for nome, rotulo in FOTOS_PREVIA:
        src = FOTOS / f"{nome}.webp"
        antes = tmp / f"{nome}-antes.png"
        depois = tmp / f"{nome}-depois.png"
        Image.open(src).convert("RGB").save(antes)
        r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(antes), "-vf", f"lut3d=file='{cube}':interp=tetrahedral",
                            "-frames:v", "1", str(depois)])
        if r.returncode:
            sys.exit("ffmpeg não aplicou a LUT")
        pares.append((antes.as_uri(), depois.as_uri(), rotulo))
    linhas = "".join(f"""
      <div class="linha"><p class="r rot">{rot}</p>
        <figure><img src="{a}"><figcaption>Antes</figcaption></figure>
        <figure><img src="{d}"><figcaption>Depois</figcaption></figure></div>""" for a, d, rot in pares)
    corpo = f"""<style>
      body{{background:{C['algodao']};padding:64px 72px}}
      h1{{font-size:54px;line-height:1.08;margin-bottom:12px}}
      .sub{{font-size:22px;line-height:1.5;max-width:1150px;margin-bottom:40px}}
      .grade{{display:grid;grid-template-columns:repeat(3,1fr);gap:36px}}
      .linha{{display:grid;grid-template-columns:1fr 1fr;gap:10px;align-content:start}}
      .rot{{grid-column:1/-1;font-size:15px;color:{C['salvia-funda']};margin-bottom:4px}}
      figure{{position:relative}} img{{display:block;width:100%;aspect-ratio:2/3;object-fit:cover;border-radius:14px}}
      figcaption{{position:absolute;left:10px;bottom:10px;background:{C['mar']};color:{C['algodao']};font-weight:600;font-size:16px;padding:5px 12px;border-radius:999px}}
      .pe{{margin-top:36px;font-size:17px;color:{C['salvia-funda']}}}
    </style>
    <h1 class="t">Ajuste de cor da marca: antes e depois</h1>
    <p class="sub">Arquivo <b>{LUT_NOME}.cube</b>. Temperatura levemente quente, contraste suave e pretos sem esmagar. A camisa continua branca, a pele continua dela e a planta continua verde.</p>
    <div class="grade">{linhas}</div>
    <p class="pe">Fotos reais do acervo da Ana, sem retoque. Aplicado com intensidade de 100%.</p>"""
    saida = pasta / "previa-antes-depois.png"
    rd.png(corpo, 1800, None, saida)
    im = Image.open(saida).convert("RGB")
    im.save(pasta / "previa-antes-depois.jpg", quality=86, optimize=True, progressive=True)
    saida.unlink()


# ---------------------------------------------------------------- zona segura

def zona(rd):
    pasta = SAIDA / "zona-segura"
    mar, alg, sal = C["mar"], C["algodao"], C["salvia"]
    faixa = "rgba(16,58,64,.55)"
    rot = f"position:absolute;font-weight:600;font-size:24px;color:{alg};letter-spacing:.02em"

    def base(extra, anuncio=False, rotulos=True, faixas=True):
        partes = []
        if faixas:
            partes.append(f"""
            <div style="position:absolute;left:0;top:0;width:1080px;height:250px;background:{faixa}"></div>
            <div style="position:absolute;left:0;top:1540px;width:1080px;height:380px;background:{faixa}"></div>
            <div style="position:absolute;left:940px;top:250px;width:140px;height:1290px;background:{faixa}"></div>
            <div style="position:absolute;left:0;top:250px;width:60px;height:1290px;background:rgba(16,58,64,.28)"></div>""")
        partes.append(f"""<div style="position:absolute;left:60px;top:250px;width:880px;height:1290px;border:4px dashed {sal}"></div>""")
        if anuncio:
            partes.append(f"""<div style="position:absolute;left:0;top:1440px;width:1080px;border-top:4px dotted {alg}"></div>""")
        if rotulos:
            partes.append(f"""
            <p class="r" style="{rot};left:60px;top:44px;font-size:26px">Zona segura · ocultar antes de exportar</p>
            <p style="{rot};left:60px;top:150px">1 · Topo: 250 px livres (perfil, barra e fechar)</p>
            <p style="{rot};left:60px;top:1580px">2 · Base: 380 px livres (legenda do post, música, resposta)</p>
            <p style="{rot};left:60px;top:1630px;font-weight:400">Área útil: x de 60 a 940 · y de 250 a 1540</p>
            <p style="{rot};left:958px;top:280px;writing-mode:vertical-rl;font-size:22px">3 · Direita: 140 px (botões da rede)</p>""")
            if anuncio:
                partes.append(f"""<p style="{rot};left:560px;top:1400px;font-size:20px">Anúncio: base de 480 px (y 1440)</p>""")
        partes.append(extra)
        return "".join(partes)

    guias = f"""
      <div style="position:absolute;left:60px;top:640px;width:880px;border-top:2px solid rgba(242,240,235,.85)"></div>
      <p style="position:absolute;left:72px;top:604px;font-weight:600;font-size:20px;color:{alg};background:rgba(16,58,64,.82);padding:4px 10px;border-radius:6px">Olhos da Ana (y ≈ 640)</p>
      <div style="position:absolute;left:60px;top:1500px;width:880px;border-top:3px solid {sal}"></div>
      <p style="position:absolute;left:72px;top:1462px;font-weight:600;font-size:20px;color:{alg};background:rgba(16,58,64,.82);padding:4px 10px;border-radius:6px">Base da legenda queimada (y 1500)</p>
      <div style="position:absolute;left:60px;top:1080px;width:540px;height:180px;border:2px dashed rgba(242,240,235,.9);border-radius:24px"></div>
      <p style="position:absolute;left:76px;top:1094px;font-weight:600;font-size:20px;color:{alg};background:rgba(16,58,64,.82);padding:4px 10px;border-radius:6px">Lower third (base em y 1260)</p>
      <div style="position:absolute;left:0;top:250px;width:1080px;height:170px;border-bottom:2px dashed rgba(242,240,235,.9)"></div>
      <p style="position:absolute;left:76px;top:268px;font-weight:600;font-size:20px;color:{alg};background:rgba(16,58,64,.82);padding:4px 10px;border-radius:6px">Faixa de título nos 3 primeiros segundos (y 250 a 420)</p>"""
    rd.png(base(guias), 1080, 1920, pasta / "zona-segura-9x16-guia.png", True)
    rd.png(base("", rotulos=False), 1080, 1920, pasta / "zona-segura-9x16-simples.png", True)
    rd.png(base("", anuncio=True), 1080, 1920, pasta / "zona-segura-9x16-anuncio.png", True)
    capa = f"""
      <div style="position:absolute;left:80px;top:420px;width:920px;height:1080px;border:4px solid {C['caramelo']}"></div>
      <p style="position:absolute;left:96px;top:436px;font-weight:600;font-size:22px;color:{alg};background:rgba(16,58,64,.82);padding:4px 10px;border-radius:6px">Capa de Reels e TikTok: título dentro de x 80 a 1000 · y 420 a 1500</p>"""
    rd.png(base(capa, rotulos=False), 1080, 1920, pasta / "zona-segura-9x16-capa-reels.png", True)
    # prévia: a guia por cima de uma foto real, para o README e o manual
    from PIL import Image
    foto = Image.open(FOTOS / "ana-04-janela-sorrindo.webp").convert("RGBA")
    s = 1920 / foto.height
    foto = foto.resize((round(foto.width * s), 1920), Image.LANCZOS)
    x = (foto.width - 1080) // 2
    foto = foto.crop((x, 0, x + 1080, 1920))
    foto.alpha_composite(Image.open(pasta / "zona-segura-9x16-guia.png").convert("RGBA"))
    foto.convert("RGB").resize((540, 960), Image.LANCZOS).save(pasta / "previa-zona-segura.jpg", quality=86, optimize=True)
    for f in pasta.glob("*.png"):
        otimizar_png(f)


# ---------------------------------------------------------------- legenda

ESTILO_LEGENDA = {
    "nome": "Legenda queimada · Ana Paula Costa",
    "quadro": [1080, 1920],
    "fonte": "Atkinson Hyperlegible Next",
    "peso": "SemiBold (600)",
    "algarismos": "Literata (zero aberto); se o editor não permitir duas fontes, mantenha a Atkinson",
    "tamanho_px": 60,
    "tamanho_faixa_px": [56, 64],
    "entrelinha": 1.25,
    "texto": "#F2F0EB",
    "destaque": {"cor": "#63AF9C", "regra": "uma palavra por frase, a que carrega o sentido"},
    "caixa": {"cor": "#103A40", "opacidade": 0.85, "raio_px": 12, "respiro_px": [14, 24]},
    "alternativa_sem_caixa": {"contorno": "#103A40", "espessura_px": 4},
    "posicao": {"alinhamento": "centro", "x_min": 60, "x_max": 940, "base_do_bloco_y": 1500},
    "limites": {"linhas": 2, "caracteres_por_linha": 32},
    "caixa_alta": "não; só uma palavra de ênfase",
    "proibido": ["emoji", "números de peso ou medida", "palavra que prometa resultado"],
    "contraste": {"texto_sobre_caixa": "10,8 para 1", "destaque_sobre_caixa": "4,8 para 1"},
}

SRT = """1
00:00:00,000 --> 00:00:01,900
Você, gestante,
que passa mal com o ferro…

2
00:00:01,900 --> 00:00:03,300
Posso parar o ferro?

3
00:00:03,300 --> 00:00:05,400
Não pare por conta própria. O que muda
é o <font color="#63AF9C">jeito</font> de tomar.

4
00:00:05,400 --> 00:00:07,900
Horário e forma de tomar
se ajustam no pré-natal.

5
00:00:07,900 --> 00:00:10,600
Cada <font color="#63AF9C">fase</font> pede outro prato,
e outro cuidado.

6
00:00:10,600 --> 00:00:13,400
Antes de mudar qualquer coisa,
fale com quem te acompanha.

7
00:00:13,400 --> 00:00:15,800
Me conta nos comentários:
o ferro te deixa enjoada?
"""


def legenda(rd):
    pasta = SAIDA / "legenda"
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "exemplo-legenda.srt").write_text(SRT, encoding="utf-8")
    sem_cor = SRT.replace('<font color="#63AF9C">', "").replace("</font>", "")
    (pasta / "exemplo-legenda-sem-cor.srt").write_text(sem_cor, encoding="utf-8")
    (pasta / "estilo-legenda.json").write_text(json.dumps(ESTILO_LEGENDA, ensure_ascii=False, indent=2) + "\n",
                                               encoding="utf-8")
    foto = (FOTOS / "ana-06-notebook-no-colo.webp").as_uri()
    alg, mar, sal = C["algodao"], C["mar"], C["salvia"]

    def quadro(medidas):
        m = ""
        if medidas:
            nota = "position:absolute;font-weight:600;font-size:22px;color:" + alg + ";background:rgba(16,58,64,.82);padding:6px 12px;border-radius:8px"
            m = f"""
            <div style="position:absolute;left:60px;top:250px;width:880px;height:1290px;border:3px dashed {sal}"></div>
            <div style="position:absolute;left:60px;top:1500px;width:880px;border-top:3px solid {C['caramelo']}"></div>
            <p style="{nota};left:60px;top:1512px">Base do bloco: y 1500</p>
            <p style="{nota};left:60px;top:262px">Área útil: x 60 a 940 · y 250 a 1540</p>
            <p style="{nota};left:600px;top:1180px">60 px · SemiBold · 2 linhas</p>
            <p style="{nota};left:600px;top:1230px">Caixa Mar Fundo 85% · cantos 12 px</p>
            <p style="{nota};left:600px;top:1280px">Destaque em Sálvia Ana</p>"""
        return f"""<style>
          .q{{position:relative;width:1080px;height:1920px;overflow:hidden;background:{mar}}}
          .q img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:50% 25%}}
          .leg{{position:absolute;left:60px;width:880px;bottom:420px;text-align:center;font-weight:600;font-size:60px;line-height:1.25}}
          .leg span{{background:rgba(16,58,64,.85);color:{alg};padding:6px 24px;border-radius:12px;-webkit-box-decoration-break:clone;box-decoration-break:clone}}
          .leg b{{color:{sal};font-weight:600}}
        </style>
        <div class="q"><img src="{foto}">
          <p class="leg"><span>Não pare por conta própria.</span><br><span>O que muda é o <b>jeito</b> de tomar.</span></p>{m}</div>"""
    rd.png(quadro(False), 1080, 1920, pasta / "legenda-referencia.png")
    rd.png(quadro(True), 1080, 1920, pasta / "legenda-referencia-medidas.png")
    # versão sem caixa (contorno), para quando a caixa cobre demais a imagem
    contorno = quadro(False).replace(
        f".leg span{{background:rgba(16,58,64,.85);color:{alg};padding:6px 24px;border-radius:12px;-webkit-box-decoration-break:clone;box-decoration-break:clone}}",
        f".leg span{{color:{alg};text-shadow:" + ",".join(f"{x}px {y}px 0 {mar}" for x in (-4,-3,-2,0,2,3,4) for y in (-4,-3,-2,0,2,3,4) if x*x+y*y<=17 and (x or y)) + "}")
    rd.png(contorno, 1080, 1920, pasta / "legenda-referencia-contorno.png")
    from PIL import Image
    for f in pasta.glob("*.png"):
        if f.name == "legenda-referencia.png":
            otimizar_png(f)
            continue
        im = Image.open(f).convert("RGB")
        im.save(f.with_suffix(".jpg"), quality=88, optimize=True, progressive=True)
        f.unlink()


# ---------------------------------------------------------------- paleta

ORDEM = ["salvia", "algodao", "bruma", "mar", "salvia-funda", "pedra", "caramelo", "caramelo-tostado",
         "ouro-velho", "grafite"]
DERIVADAS = ["salvia-clara", "mar-medio", "mar-superficie"]


def cores_paleta():
    p = [dict(TOKENS["cores"][k], chave=k) for k in ORDEM]
    d = [dict(TOKENS["cores_derivadas"][k], chave=k) for k in DERIVADAS]
    return p, d


def ase(grupos):
    """Adobe Swatch Exchange 1.0: blocos de grupo (0xC001/0xC002) e de cor (0x0001), big-endian."""
    def nome_bytes(s):
        b = (s + "\0").encode("utf-16-be")
        return struct.pack(">H", len(s) + 1) + b

    blocos = []
    for gnome, cores in grupos:
        corpo = nome_bytes(gnome)
        blocos.append(struct.pack(">HI", 0xC001, len(corpo)) + corpo)
        for c in cores:
            r, g, b = (v / 255 for v in c["rgb"])
            corpo = nome_bytes(f"{c['nome']} {c['hex']}") + b"RGB " + struct.pack(">fffH", r, g, b, 2)
            blocos.append(struct.pack(">HI", 0x0001, len(corpo)) + corpo)
        blocos.append(struct.pack(">HI", 0xC002, 0))
    return b"ASEF" + struct.pack(">HHI", 1, 0, len(blocos)) + b"".join(blocos)


def ler_ase(dados):
    """Leitura de conferência (prova de que o arquivo é válido)."""
    assert dados[:4] == b"ASEF"
    _, _, n = struct.unpack(">HHI", dados[4:12])
    i, cores = 12, []
    for _ in range(n):
        tipo, tam = struct.unpack(">HI", dados[i:i + 6])
        corpo = dados[i + 6:i + 6 + tam]
        if tipo == 0x0001:
            ln = struct.unpack(">H", corpo[:2])[0]
            nome = corpo[2:2 + ln * 2].decode("utf-16-be").rstrip("\0")
            modelo = corpo[2 + ln * 2:6 + ln * 2]
            rgb = struct.unpack(">fff", corpo[6 + ln * 2:18 + ln * 2])
            cores.append((nome, modelo, tuple(round(v * 255) for v in rgb)))
        i += 6 + tam
    assert i == len(dados)
    return cores


def paleta(rd):
    pasta = SAIDA / "paleta"
    pasta.mkdir(parents=True, exist_ok=True)
    p, d = cores_paleta()
    dados = ase([("Ana Paula Costa · principais", p), ("Ana Paula Costa · derivadas", d)])
    (pasta / "ana-paula-costa-paleta.ase").write_bytes(dados)
    conf = ler_ase(dados)
    for (nome, modelo, rgb), c in zip(conf, p + d):
        assert modelo == b"RGB " and list(rgb) == c["rgb"], (nome, rgb, c["rgb"])
    gpl = ["GIMP Palette", "Name: Ana Paula Costa · Nutricionista", "Columns: 5",
           "# Sistema Rota ap. · cores principais e derivadas (tokens v1.2)", "#"]
    for c in p + d:
        r, g, b = c["rgb"]
        gpl.append(f"{r:3d} {g:3d} {b:3d}\t{c['nome']} {c['hex']}")
    (pasta / "ana-paula-costa-paleta.gpl").write_text("\n".join(gpl) + "\n", encoding="utf-8")
    txt = ["Ana Paula Costa · Nutricionista · paleta (sistema Rota ap., tokens v1.2)",
           "CMYK pelo perfil ISO Coated v2 300% (FOGRA39, papel revestido). Em papel não revestido, peça à gráfica para converter o RGB.",
           ""]
    for titulo, lista in (("PRINCIPAIS", p), ("DERIVADAS (só para os usos indicados)", d)):
        txt.append(titulo)
        for c in lista:
            r, g, b = c["rgb"]
            cm = " ".join(str(v) for v in c["cmyk_fogra39"])
            prop = c.get("proporcao_sugerida", "")
            txt.append(f"  {c['nome']:<17} {c['hex']}  RGB {r} {g} {b}  CMYK {cm}  {prop}".rstrip())
            txt.append(f"      {c['uso']}")
        txt.append("")
    (pasta / "ana-paula-costa-paleta.txt").write_text("\n".join(txt), encoding="utf-8")

    escuras = {"mar", "salvia-funda", "caramelo-tostado", "grafite", "mar-medio", "mar-superficie"}

    def cartao(c, grande):
        cor_txt = C["algodao"] if c["chave"] in escuras else C["mar"]
        r, g, b = c["rgb"]
        cm = " ".join(str(v) for v in c["cmyk_fogra39"])
        prop = c.get("proporcao_sugerida")
        return f"""<div class="am{' g' if grande else ''}" style="background:{c['hex']};color:{cor_txt}">
          <p class="nm t" style="color:{cor_txt}">{c['nome']}</p>
          <div class="cod"><span>{c['hex']}</span><span>RGB {r} {g} {b}</span><span>CMYK {cm}</span>{f'<span class="pp">{prop}</span>' if prop else ''}</div></div>"""

    principais = "".join(cartao(c, i < 5) for i, c in enumerate(p))
    deriv = "".join(cartao(c, False) for c in d)
    barra = "".join(f'<span style="flex:{float(c["proporcao_sugerida"].rstrip("%").replace(",", "."))};background:{c["hex"]}"></span>' for c in p)
    corpo = f"""<style>
      body{{background:{C['algodao']};padding:72px 80px}}
      .r{{font-size:16px;color:{C['salvia-funda']}}}
      h1{{font-size:60px;line-height:1.05;margin:10px 0 14px}}
      .sub{{font-size:22px;line-height:1.5;max-width:1200px}}
      .grade{{display:grid;grid-template-columns:repeat(5,1fr);gap:16px;margin-top:40px}}
      .am{{border-radius:14px;padding:22px 22px 20px;min-height:200px;display:flex;flex-direction:column;justify-content:space-between;
           box-shadow:inset 0 0 0 1px rgba(16,58,64,.08)}}
      .am.g{{min-height:280px}}
      .nm{{font-size:28px;line-height:1.1}}
      .cod{{display:grid;gap:2px;font-size:17px;font-weight:500}}
      .cod span:first-child{{font-weight:700;font-size:19px;letter-spacing:.02em}}
      .pp{{margin-top:6px;font-weight:700}}
      .prop{{display:flex;gap:3px;height:28px;margin-top:44px}} .prop span{{border-radius:6px;box-shadow:inset 0 0 0 1px rgba(16,58,64,.14)}}
      .der{{display:grid;grid-template-columns:repeat(5,1fr);gap:16px;margin-top:14px}}
      h2{{font-size:32px;margin-top:44px}}
      .pe{{margin-top:30px;font-size:17px;line-height:1.5;color:{C['grafite']};max-width:1500px}}
    </style>
    <p class="r">Ana Paula Costa · Nutricionista · sistema Rota ap.</p>
    <h1 class="t">Paleta</h1>
    <p class="sub">Sálvia por cima, Algodão para ler e um único ponto Caramelo por peça (o do logotipo conta).</p>
    <div class="grade">{principais}</div>
    <p class="r" style="margin-top:44px">Proporção de uso</p>
    <div class="prop" style="margin-top:12px">{barra}</div>
    <h2 class="t">Derivadas, só para os usos indicados</h2>
    <div class="der">{deriv}</div>
    <p class="pe">CMYK calculado pelo perfil ISO Coated v2 300% (FOGRA39, papel revestido). Em papel não revestido, peça à gráfica para converter os valores RGB com o perfil dela e faça prova de cor na primeira tiragem.</p>"""
    rd.png(corpo, 1800, None, pasta / "ana-paula-costa-paleta.png")
    otimizar_png(pasta / "ana-paula-costa-paleta.png")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--so", choices=["lut", "zona", "legenda", "paleta"])
    a = ap.parse_args()
    rd = Render()
    try:
        if a.so in (None, "lut"):
            previa_lut(rd, gerar_lut())
        if a.so in (None, "zona"):
            zona(rd)
        if a.so in (None, "legenda"):
            legenda(rd)
        if a.so in (None, "paleta"):
            paleta(rd)
    finally:
        rd.fechar()
    print("pronto: assets/producao/")


if __name__ == "__main__":
    main()
