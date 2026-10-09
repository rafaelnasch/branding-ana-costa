#!/usr/bin/env python3
"""Kit de vídeo da marca: abertura, encerramento e lower third animados.

  python3 tools/kit_video.py                    gera tudo em assets/video/
  python3 tools/kit_video.py --so abertura      só uma peça (abertura | encerramento | lower)
  python3 tools/kit_video.py --crn "CRN-4 00000"  troca o marcador do CRN quando o número chegar
  python3 tools/kit_video.py --conferir         extrai quadros de cada vídeo para _qa/video/

Como funciona
  1. Cada quadro é desenhado no Chromium (Playwright) a partir dos SVG oficiais da marca em
     assets/marca/svg/ (rode antes tools/sync_marca.py). O símbolo é revelado por uma máscara
     que segue o caminho da pena: a, depois a haste do a, a haste do p com o mergulho e o bojo
     do p. O ponto pousa por último, caindo um pouco e ganhando corpo (0,6 para 1).
  2. Os quadros saem em PNG com fundo transparente, a 30 quadros por segundo.
  3. O ffmpeg monta:
       MOV Apple ProRes 4444 com canal alfa (para pôr por cima do vídeo no editor)
       MP4 H.264 já com o fundo da marca (para usar direto como cartela)
  4. O último quadro de cada peça vira PNG estático.

Nada aqui altera o desenho da marca: o símbolo não gira, não quica e não pulsa. Só o traço
se desenha e o ponto pousa (regras das seções 14 e 17 do manual).
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SVG = RAIZ / "assets" / "marca" / "svg"
FONTES = RAIZ / "assets" / "fontes"
SAIDA = RAIZ / "assets" / "video"
QA = RAIZ / "_qa" / "video"
FPS = 30

COR = {
    "algodao": "#F2F0EB", "bruma": "#D8ECE5", "mar": "#103A40", "salvia": "#63AF9C",
    "salvia-funda": "#2F6E60", "caramelo": "#C99A68",
}

# esquema do logotipo -> sufixo do arquivo e cor do texto de apoio (CRN)
ESQUEMA = {
    "claro": {"arq": "cor", "texto": COR["mar"]},
    "escuro": {"arq": "sobre-escuro", "texto": COR["algodao"]},
    "salvia": {"arq": "sobre-salvia", "texto": COR["mar"]},
}

FORMATO = {"vertical": (1080, 1920), "horizontal": (1920, 1080)}

# Peças. Cada MP4 = esquema + cor de fundo. Cada MOV = esquema com fundo transparente.
PECAS = {
    "abertura": {
        "dur": 2.5,
        "mp4": [("claro", "algodao"), ("claro", "bruma"), ("escuro", "mar")],
        "mov": ["claro", "escuro"],
    },
    "encerramento": {
        "dur": 2.5,
        "mp4": [("escuro", "mar"), ("salvia", "salvia"), ("claro", "algodao"), ("claro", "bruma")],
        "mov": ["claro", "escuro"],
    },
    # versão de 1 segundo para Reels e TikTok: símbolo já escrito, o ponto pousa aos 0,3 s
    "encerramento-curto": {
        "dur": 1.0,
        "mp4": [("escuro", "mar"), ("salvia", "salvia"), ("claro", "algodao"), ("claro", "bruma")],
        "mov": ["claro", "escuro"],
    },
}
LOWER_DUR = 4.0


def chromium():
    cands = sorted(glob.glob(os.path.expanduser(
        "~/Library/Caches/ms-playwright/chromium-*/chrome-mac*/*.app/Contents/MacOS/*")))
    cands = [c for c in cands if os.access(c, os.X_OK)]
    return cands[-1] if cands else None


def pagina_html(w, h):
    f = FONTES.as_uri()
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>
@font-face{{font-family:'Ana Numerais';src:url('{f}/Literata[opsz,wght].ttf');font-weight:200 900;unicode-range:U+0030-0039}}
@font-face{{font-family:'Atkinson Hyperlegible Next';src:url('{f}/AtkinsonHyperlegibleNext[wght].ttf');font-weight:200 800}}
html,body{{margin:0;padding:0;width:{w}px;height:{h}px;overflow:hidden;background:transparent}}
#palco{{position:absolute;inset:0}}
svg{{display:block;overflow:visible}}
.linha{{font-family:'Ana Numerais','Atkinson Hyperlegible Next',sans-serif;font-weight:600;white-space:nowrap}}
</style></head><body><div id="palco"></div><script>{JS}</script></body></html>"""


# Linhas centrais da pena, no sistema de coordenadas de simbolo-*.svg (unidade x = 50).
# Ordem de escrita: bojo do a, haste e cauda do a, haste e mergulho do p, bojo do p.
TRACOS = [
    {"letra": "a", "w": 16, "pts": [[55.5, 36], [47, 30.6], [36, 30.1], [22.5, 34.3], [14.2, 44], [11.6, 56],
                                     [14.4, 67.5], [22, 75.8], [33, 79.6], [43.5, 78.6], [51, 75.5], [56.5, 69]]},
    {"letra": "a", "w": 13, "pts": [[59.6, 29.2], [59, 50], [58.8, 71.5], [60.4, 78.6], [65.6, 79.7], [72.3, 76.2]]},
    {"letra": "p", "w": 11.6, "pts": [[89.9, 33.5], [89.8, 60], [89.8, 100], [90.8, 109.4], [96.8, 115.6], [104, 115.7],
                                     [112, 114.2], [118.6, 110.6], [124, 102.2]]},
    {"letra": "p", "w": 13, "pts": [[94.5, 41], [99.5, 33.4], [106, 30.6], [113, 30.1], [124, 32.4], [132.4, 41],
                                     [135.4, 56], [132.2, 70], [123.2, 77.6], [113, 79.6], [104, 78.8], [96.2, 74.6]]},
]

JS = r"""
const P = window.__P;
const NS = 'http://www.w3.org/2000/svg';
// curva maré: cubic-bezier(.33,0,.15,1)
function bezier(x1,y1,x2,y2){
  const cx=3*x1,bx=3*(x2-x1)-cx,ax=1-cx-bx,cy=3*y1,by=3*(y2-y1)-cy,ay=1-cy-by;
  const fx=t=>((ax*t+bx)*t+cx)*t, fy=t=>((ay*t+by)*t+cy)*t, dx=t=>(3*ax*t+2*bx)*t+cx;
  return x=>{ if(x<=0)return 0; if(x>=1)return 1; let t=x;
    for(let i=0;i<8;i++){const e=fx(t)-x; const d=dx(t); if(Math.abs(e)<1e-6)break; if(Math.abs(d)<1e-6)break; t-=e/d;}
    let lo=0,hi=1; if(Math.abs(fx(t)-x)>1e-5){t=x; for(let i=0;i<40;i++){ if(fx(t)<x)lo=t; else hi=t; t=(lo+hi)/2; }}
    return fy(t); };
}
const mare = bezier(.33,0,.15,1);
const fase = (t,a,b)=> t<=a?0 : t>=b?1 : (t-a)/(b-a);
function catmull(pts){
  let d=`M${pts[0][0]} ${pts[0][1]}`;
  for(let i=0;i<pts.length-1;i++){
    const p0=pts[Math.max(i-1,0)],p1=pts[i],p2=pts[i+1],p3=pts[Math.min(i+2,pts.length-1)];
    const c1=[p1[0]+(p2[0]-p0[0])/6,p1[1]+(p2[1]-p0[1])/6], c2=[p2[0]-(p3[0]-p1[0])/6,p2[1]-(p3[1]-p1[1])/6];
    d+=`C${c1[0]} ${c1[1]} ${c2[0]} ${c2[1]} ${p2[0]} ${p2[1]}`;
  }
  return d;
}
function el(tag,attrs,pai){const e=document.createElementNS(NS,tag); for(const k in attrs)e.setAttribute(k,attrs[k]); if(pai)pai.appendChild(e); return e;}
function inserirSvg(texto,larg){
  const box=document.createElement('div'); box.innerHTML=texto; const s=box.querySelector('svg');
  const vb=s.viewBox.baseVal; s.setAttribute('width',larg); s.setAttribute('height',larg*vb.height/vb.width);
  s.removeAttribute('role'); return s;
}
const palco=document.getElementById('palco');
const estado={};

function montarMarca(){
  // símbolo de referência (coordenadas das linhas centrais) para achar a transformação
  const ref=inserirSvg(P.simbolo,100); ref.style.position='absolute'; ref.style.visibility='hidden'; palco.appendChild(ref);
  const bbRef=ref.querySelector('path').getBBox();
  const s=inserirSvg(P.logo,P.largura); s.style.position='absolute'; palco.appendChild(s);
  const vb=s.viewBox.baseVal, H=P.largura*vb.height/vb.width;
  s.style.left=(P.cx-P.largura/2)+'px'; s.style.top=(P.cy-H/2)+'px';
  const caminhos=[...s.querySelectorAll('path')];
  const letras=caminhos[0], ponto=caminhos[1], textos=caminhos.slice(2);
  const bb=letras.getBBox(); const k=bb.width/bbRef.width;
  const tx=bb.x-bbRef.x*k, ty=bb.y-bbRef.y*k;
  // separa o a e o p (subcaminhos: p, a, miolo do a, miolo do p)
  const subs=letras.getAttribute('d').split(/(?=M)/);
  const cor=letras.getAttribute('fill');
  const defs=el('defs',{},s);
  const grupos={};
  for(const L of ['a','p']){
    const m=el('mask',{id:'m'+L,maskUnits:'userSpaceOnUse',x:-5000,y:-5000,width:10000,height:10000},defs);
    grupos[L]=el('g',{transform:`matrix(${k} 0 0 ${k} ${tx} ${ty})`},m);
  }
  const dA=subs[1]+subs[2], dP=subs[0]+subs[3];
  const pa=el('path',{d:dA,fill:cor,mask:'url(#ma)'}); const pp=el('path',{d:dP,fill:cor,mask:'url(#mp)'});
  s.insertBefore(pa,letras); s.insertBefore(pp,letras); letras.style.display='none';
  const tracos=P.tracos.map(t=>{
    const p=el('path',{d:catmull(t.pts),fill:'none',stroke:'#fff','stroke-width':t.w,'stroke-linecap':'round','stroke-linejoin':'round'},grupos[t.letra]);
    return {el:p,len:p.getTotalLength()};
  });
  const total=tracos.reduce((a,t)=>a+t.len,0), pausa=total*0.035;
  let acc=0; const soma=total+pausa*(tracos.length-1);
  tracos.forEach(t=>{t.ini=acc/soma; t.fim=(acc+t.len)/soma; acc+=t.len+pausa;});
  // ponto: cai de cima e ganha corpo
  const pb=ponto.getBBox(); ponto.style.transformBox='fill-box'; ponto.style.transformOrigin='center';
  const gt=el('g',{},s); textos.forEach(x=>gt.appendChild(x));
  Object.assign(estado,{tracos,pa,pp,letras,ponto,gt,k,pb});
}

function montarLinha(){
  const d=document.createElement('div'); d.className='linha'; d.textContent=P.linha;
  Object.assign(d.style,{position:'absolute',left:'0',width:'100%',textAlign:'center',top:P.linhaY+'px',
    fontSize:P.linhaTam+'px',color:P.linhaCor,letterSpacing:'.02em'});
  palco.appendChild(d); estado.linha=d;
}

function montarLower(){
  const c=document.createElement('div');
  Object.assign(c.style,{position:'absolute',left:P.x+'px',background:'#F2F0EB',borderRadius:'24px',
    padding:'28px 36px 26px',boxShadow:'0 2px 4px rgba(16,58,64,.08),0 14px 36px rgba(16,58,64,.16)'});
  const s=inserirSvg(P.assinatura,P.largura); c.appendChild(s);
  const l=document.createElement('div'); l.className='linha'; l.textContent=P.linha;
  Object.assign(l.style,{fontSize:'30px',lineHeight:'1.2',color:'#2F6E60',marginTop:'16px',letterSpacing:'.01em'});
  c.appendChild(l); palco.appendChild(c);
  c.style.top=(P.base-c.offsetHeight)+'px';
  estado.cartao=c;
}

window.montar=async function(){
  await document.fonts.ready;
  if(P.peca==='crn'){ montarLinha(); await document.fonts.ready; return true; }
  if(P.peca==='lower'){ montarLower(); }
  else { montarMarca(); if(P.linha) montarLinha(); }
  await document.fonts.ready;
  return true;
};

window.quadro=function(t){
  if(P.peca==='crn') return;
  const T=P.tempo;
  if(P.peca==='lower'){
    const e=mare(fase(t,0,0.24)), sai=fase(t,T-0.24,T);
    estado.cartao.style.opacity=(e*(1-sai)).toFixed(4);
    estado.cartao.style.transform=`translateY(${(16*(1-e)).toFixed(2)}px)`;
    return;
  }
  const u=mare(fase(t,T.traco[0],T.traco[1]));
  const pronto=u>=1;
  estado.letras.style.display=pronto?'':'none';
  estado.pa.style.display=pronto?'none':''; estado.pp.style.display=pronto?'none':'';
  for(const tr of estado.tracos){
    const f=Math.min(1,Math.max(0,(u-tr.ini)/(tr.fim-tr.ini)));
    if(f<=0){tr.el.style.visibility='hidden';continue;}
    tr.el.style.visibility='visible';
    tr.el.setAttribute('stroke-dasharray',`${(f*tr.len).toFixed(3)} ${tr.len*2}`);
  }
  const q=mare(fase(t,T.ponto[0],T.ponto[1]));
  const queda=(1-q)*14*estado.k;
  estado.ponto.style.opacity=Math.min(1,fase(t,T.ponto[0],T.ponto[0]+(T.ponto[1]-T.ponto[0])*0.6)).toFixed(4);
  estado.ponto.style.transform=`translateY(${(-queda).toFixed(3)}px) scale(${(0.6+0.4*q).toFixed(4)})`;
  const x=mare(fase(t,T.texto[0],T.texto[1]));
  estado.gt.style.opacity=x.toFixed(4);
  estado.gt.style.transform=`translateY(${(16*(1-x)/ (P.largura/ estado.gt.ownerSVGElement.viewBox.baseVal.width)).toFixed(3)}px)`;
  if(estado.linha){ const y=mare(fase(t,T.texto[0],T.texto[1]));
    estado.linha.style.opacity=y.toFixed(4); estado.linha.style.transform=`translateY(${(16*(1-y)).toFixed(2)}px)`; }
};
"""


def ler(p):
    return Path(p).read_text(encoding="utf-8")


def posicao_encerramento(formato):
    """Largura e centro do logotipo vertical no encerramento (dentro da área útil no vertical)."""
    return (520, 500, 820) if formato == "vertical" else (500, 960, 470)


def linha_crn_y(formato):
    """Topo da linha do CRN: 56 px abaixo do logotipo vertical."""
    import re as _re
    vb = _re.search(r'viewBox="([^"]+)"', ler(SVG / "logo-vertical-cor.svg")).group(1).split()
    larg, cx, cy = posicao_encerramento(formato)
    alt = larg * float(vb[3]) / float(vb[2])
    return round(cy + alt / 2 + 56)


def parametros(peca, formato, esquema, crn, linha_lower=None):
    w, h = FORMATO[formato]
    arq = ESQUEMA[esquema]["arq"]
    p = {"peca": peca, "simbolo": ler(SVG / "simbolo-cor.svg"), "tracos": TRACOS}
    if peca == "abertura":
        if formato == "vertical":
            # logotipo vertical centrado na área útil (x 60 a 940, y 250 a 1540)
            p.update(logo=ler(SVG / f"logo-vertical-{arq}.svg"), largura=680, cx=500, cy=880)
        else:
            p.update(logo=ler(SVG / f"logo-horizontal-{arq}.svg"), largura=1040, cx=960, cy=540)
        p["tempo"] = {"traco": [0.2, 1.4], "ponto": [1.4, 1.72], "texto": [1.62, 2.1]}
        p["linha"] = None
    elif peca in ("encerramento", "encerramento-curto", "crn"):
        # logotipo vertical: símbolo, nome e "Nutricionista" (o ap. sozinho ainda não é reconhecido, P7)
        larg, cx, cy = posicao_encerramento(formato)
        if peca != "crn":
            p.update(logo=ler(SVG / f"logo-vertical-{arq}.svg"), largura=larg, cx=cx, cy=cy)
        p.update(linha=crn, linhaTam=32 if formato == "vertical" else 34, linhaCor=ESQUEMA[esquema]["texto"],
                 linhaY=linha_crn_y(formato))
        if formato == "vertical":
            p["linhaCentro"] = 500
        if peca == "crn":
            p["tempo"] = None
        elif peca == "encerramento":
            p["tempo"] = {"traco": [0.1, 1.1], "ponto": [1.1, 1.42], "texto": [1.32, 1.8]}
        else:
            p["tempo"] = {"traco": [-2, -1], "ponto": [0.0, 0.3], "texto": [-2, -1]}
    else:  # lower third
        p.update(assinatura=ler(SVG / "assinatura-compacta-cor.svg"), linha=linha_lower, tempo=LOWER_DUR)
        if formato == "vertical":
            p.update(x=60, base=1260, largura=460)
        else:
            p.update(x=96, base=960, largura=520)
    return p, (w, h)


def render_quadros(browser, peca, formato, esquema, crn, destino, linha_lower=None):
    p, (w, h) = parametros(peca, formato, esquema, crn, linha_lower)
    dur = LOWER_DUR if peca == "lower" else (0 if peca == "crn" else PECAS[peca]["dur"])
    n = int(round(dur * FPS))
    tmp_html = Path(destino) / "pagina.html"
    tmp_html.write_text(pagina_html(w, h).replace("{JS}", JS), encoding="utf-8")
    pg = browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
    pg.add_init_script("window.__P = " + json.dumps(p) + ";")
    pg.goto(tmp_html.as_uri())
    pg.evaluate("montar()")
    # a linha do encerramento vertical fica centrada na área útil (x 60 a 940), não no quadro
    if (peca.startswith("encerramento") or peca == "crn") and formato == "vertical" and p.get("linha"):
        pg.evaluate("""()=>{const l=document.querySelector('.linha'); l.style.left='60px'; l.style.width='880px';}""")
    for i in range(n):
        t = i / FPS
        pg.evaluate(f"quadro({t})")
        pg.screenshot(path=str(Path(destino) / f"q{i:04d}.png"), omit_background=True)
    # quadro final exato (estado parado) para o PNG estático
    pg.evaluate(f"quadro({dur + 1})")
    pg.screenshot(path=str(Path(destino) / "final.png"), omit_background=True)
    pg.close()
    return n, (w, h)


def ff(*args):
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args]
    r = subprocess.run(cmd)
    if r.returncode:
        sys.exit("ffmpeg falhou: " + " ".join(cmd))


def mov_alfa(pasta, saida):
    ff("-framerate", str(FPS), "-i", str(Path(pasta) / "q%04d.png"),
       "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", "-alpha_bits", "8",
       "-vendor", "apl0", "-qscale:v", "6",
       "-vf", "scale=out_color_matrix=bt709",
       "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
       "-metadata", "title=Ana Paula Costa · Nutricionista", str(saida))


def mp4_fundo(pasta, saida, wh, cor):
    w, h = wh
    ff("-f", "lavfi", "-i", f"color=c=0x{cor.lstrip('#')}:s={w}x{h}:r={FPS},format=gbrp",
       "-framerate", str(FPS), "-i", str(Path(pasta) / "q%04d.png"),
       "-filter_complex", "[0]format=gbrp[f];[1]format=rgba[q];[f][q]overlay=shortest=1:format=gbrp,scale=in_range=pc:out_color_matrix=bt709:out_range=tv,format=yuv420p",
       "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-profile:v", "high", "-tune", "animation",
       "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
       "-movflags", "+faststart", "-tag:v", "avc1", "-r", str(FPS),
       "-metadata", "title=Ana Paula Costa · Nutricionista", str(saida))


def png_fundo(png, saida, cor):
    from PIL import Image
    im = Image.open(png).convert("RGBA")
    fundo = Image.new("RGBA", im.size, cor)
    fundo.alpha_composite(im)
    fundo.convert("RGB").save(saida, optimize=True)


def conferir():
    QA.mkdir(parents=True, exist_ok=True)
    for v in sorted(SAIDA.rglob("*.mp4")) + sorted(SAIDA.rglob("*.mov")):
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(v)],
                                   capture_output=True, text=True).stdout.strip() or 0)
        for frac in (0.15, 0.35, 0.55, 0.7, 0.95):
            t = dur * frac
            out = QA / f"{v.stem}-{v.suffix[1:]}-{int(t*1000):04d}ms.png"
            ff("-ss", f"{t:.3f}", "-i", str(v), "-frames:v", "1", str(out))
    print(f"quadros extraídos em {QA}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--so", choices=["abertura", "encerramento", "encerramento-curto", "lower"])
    ap.add_argument("--crn", default="CRN-4 em confirmação", help="linha do CRN no encerramento e no lower third")
    ap.add_argument("--conferir", action="store_true")
    a = ap.parse_args()
    if a.conferir:
        conferir()
        return
    if not (SVG / "simbolo-cor.svg").exists():
        sys.exit("Faltam os SVG da marca: rode python3 tools/sync_marca.py")
    from playwright.sync_api import sync_playwright

    pecas = [a.so] if a.so else ["abertura", "encerramento", "encerramento-curto", "lower"]
    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=chromium())
        for peca in pecas:
            if peca == "lower":
                destino = SAIDA / "lower-third"
                destino.mkdir(parents=True, exist_ok=True)
                linhas = {"crn": a.crn, "fases": "Gestação, pós-parto e 40+"}
                for formato in FORMATO:
                    for chave, texto in linhas.items():
                        pasta = Path(tmp) / f"lower-{formato}-{chave}"
                        pasta.mkdir()
                        n, wh = render_quadros(br, "lower", formato, "claro", a.crn, pasta, texto)
                        nome = f"lower-third-{formato}-{chave}"
                        mov_alfa(pasta, destino / f"{nome}-alfa.mov")
                        shutil.copy(pasta / f"q{n//2:04d}.png", destino / f"{nome}.png")
                        print(f"  {nome}: {n} quadros")
                continue
            cfg = PECAS[peca]
            destino = SAIDA / peca
            destino.mkdir(parents=True, exist_ok=True)
            esquemas = sorted({e for e, _ in cfg["mp4"]} | set(cfg["mov"]))
            for formato in FORMATO:
                for esq in esquemas:
                    pasta = Path(tmp) / f"{peca}-{formato}-{esq}"
                    pasta.mkdir()
                    n, wh = render_quadros(br, peca, formato, esq, a.crn, pasta)
                    if peca.startswith("encerramento"):
                        # versão sem a linha do CRN, para o editor pôr o número por cima sem script
                        pasta_s = Path(tmp) / f"{peca}-{formato}-{esq}-sem-crn"
                        pasta_s.mkdir()
                        render_quadros(br, peca, formato, esq, "", pasta_s)
                        for e, fundo in cfg["mp4"]:
                            if e == esq:
                                mp4_fundo(pasta_s, destino / f"{peca}-{formato}-{fundo}-sem-crn.mp4", wh, COR[fundo])
                        if peca == "encerramento":
                            pasta_c = Path(tmp) / f"crn-{formato}-{esq}"
                            pasta_c.mkdir()
                            render_quadros(br, "crn", formato, esq, a.crn, pasta_c)
                            if esq in ("claro", "escuro"):
                                shutil.copy(pasta_c / "final.png", destino / f"crn-sobreposicao-{formato}-{esq}.png")
                    if esq in cfg["mov"]:
                        mov_alfa(pasta, destino / f"{peca}-{formato}-{esq}-alfa.mov")
                        shutil.copy(pasta / "final.png", destino / f"{peca}-{formato}-{esq}-alfa-final.png")
                    for e, fundo in cfg["mp4"]:
                        if e == esq:
                            nome = f"{peca}-{formato}-{fundo}"
                            mp4_fundo(pasta, destino / f"{nome}.mp4", wh, COR[fundo])
                            png_fundo(pasta / "final.png", destino / f"{nome}-final.png", COR[fundo])
                    print(f"  {peca} {formato} {esq}: {n} quadros")
        br.close()
    print("pronto: assets/video/")


if __name__ == "__main__":
    main()
