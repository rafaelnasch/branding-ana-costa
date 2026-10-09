#!/usr/bin/env python3
"""Monta o acervo de fotos da Ana para o manual: WebP 1600, miniatura 640 e catálogo.

  python3 tools/fotos.py             gera o que falta ou mudou (idempotente)
  python3 tools/fotos.py --forcar    regenera tudo
  python3 tools/fotos.py --folha     também gera assets/fotos/_folha.jpg (folha de contato, fora do git)

Saída
  assets/fotos/1600/<id>.webp   lado maior com 1600 px (nunca amplia), qualidade 82
  assets/fotos/640/<id>.webp    lado maior com 640 px, qualidade 78 (miniatura e celular)
  assets/fotos/catalogo.json    id, arquivos, medidas, proporção, cor média, alt, uso, fase, notas

Tratamento: corrige a rotação pela câmera, converte para sRGB, um toque leve de contraste
(+3%) e de saturação (-3%) para ficar fiel ao Algodão dos ensaios, nitidez suave depois da
redução. Sem recorte, sem filtro, sem retoque de pele. Todos os metadados (EXIF, GPS,
modelo da câmera) são descartados.

Critério de seleção (especificação da marca, seção 9): só a Ana, sozinha; nenhuma foto com
os filhos, o marido ou outras pessoas; nenhuma foto com mão na barriga; nenhuma imagem de
pessoa gerada por IA; nenhuma foto que já traz texto aplicado (post antigo).
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image, ImageCms, ImageEnhance, ImageFilter, ImageOps

RAIZ = Path(__file__).resolve().parent.parent
ORIGEM = None  # definido por origem_local()


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


ORIGEM = origem_local("pesquisa", "ANA_PESQUISA")
SAIDA = RAIZ / "assets" / "fotos"
VERSAO_TRATAMENTO = "t1"  # mude para forçar regeneração quando o tratamento mudar

# fase: gestacao | pos-parto | 40-mais | todas  (o modo 40+ só usa foto sem gestação aparente)
FOTOS = [
    {
        "id": "ana-01-caderno-camiseta-branca",
        "origem": "drive/ensaio-profissional-gravida/IMG_9579.jpg",
        "alt": "Ana Paula Costa, grávida, de camiseta branca e jeans, segura um caderno aberto e sorri em um consultório claro com frutas sobre a bancada.",
        "uso": "Gestação: capa de carrossel educativo, página de atendimento na gestação, abertura de e-mail.",
        "fase": "gestacao",
        "enquadramento": "corpo inteiro, retrato vertical, espaço livre à direita",
    },
    {
        "id": "ana-02-bancada-notebook",
        "origem": "drive/ensaio-profissional-gravida/IMG_9595.jpg",
        "alt": "Ana de camisa branca e saia preta apoia as mãos na bancada branca do consultório, com notebook, frutas e um copo de água.",
        "uso": "Consultório e método: seção Como funciona do site, post de bastidores, apresentação.",
        "fase": "gestacao",
        "enquadramento": "plano aberto, muito ar no topo (bom para título)",
    },
    {
        "id": "ana-03-janela-perfil",
        "origem": "drive/ensaio-profissional-gravida/IMG_9601.jpg",
        "alt": "Ana de camisa branca, de perfil junto à janela, segura um copo de água e olha para fora.",
        "uso": "Peça reflexiva e editorial: abertura de capítulo, story de pergunta, artigo sobre hidratação.",
        "fase": "todas",
        "enquadramento": "meio corpo, luz lateral da janela",
    },
    {
        "id": "ana-04-janela-sorrindo",
        "origem": "drive/ensaio-profissional-gravida/IMG_9606.jpg",
        "alt": "Ana de camisa branca, junto à janela, segura um copo de água e sorri para a câmera.",
        "uso": "Retrato principal: topo do site, foto do perfil em tamanho grande, assinatura de apresentação.",
        "fase": "todas",
        "enquadramento": "meio corpo, olhar para a câmera; cabe na moldura em arco",
    },
    {
        "id": "ana-05-sofa-notebook",
        "origem": "drive/ensaio-profissional-gravida/IMG_9611.jpg",
        "alt": "Ana sentada em um sofá claro com o notebook no colo, ao lado de uma planta e de uma mesinha com livro.",
        "uso": "Atendimento online: página de consulta, anúncio de agenda aberta, capa de destaque Consulta.",
        "fase": "todas",
        "enquadramento": "plano aberto, ambiente inteiro",
    },
    {
        "id": "ana-06-notebook-no-colo",
        "origem": "drive/ensaio-profissional-gravida/IMG_9616.jpg",
        "alt": "Ana sentada no sofá, de camisa branca, segura o notebook fechado no colo e sorri para a câmera.",
        "uso": "Consulta online e convite para avaliação: post de chamada, rodapé de e-mail, página de agendamento.",
        "fase": "todas",
        "enquadramento": "meio corpo sentada, planta à direita",
    },
    {
        "id": "ana-07-tablet",
        "origem": "drive/ensaio-profissional-gravida/IMG_9621.jpg",
        "alt": "Ana sentada no sofá, de camisa branca, olha para um tablet nas mãos e sorri.",
        "uso": "Plano alimentar e acompanhamento: peça sobre o retorno, aplicativo, recado entre consultas.",
        "fase": "todas",
        "enquadramento": "meio corpo, olhar para o tablet",
    },
    {
        "id": "ana-08-bola-sentada",
        "origem": "drive/ensaio-profissional-gravida/IMG_9656.jpg",
        "alt": "Ana, grávida, de top e legging pretos, sentada em uma bola de pilates azul-esverdeada, sorri com as mãos nos joelhos.",
        "uso": "Gestação ativa: conteúdo sobre movimento, energia e alimentação na gravidez.",
        "fase": "gestacao",
        "enquadramento": "corpo inteiro, fundo branco amplo",
    },
    {
        "id": "ana-09-alongamento-bola",
        "origem": "drive/ensaio-profissional-gravida/IMG_9661.jpg",
        "alt": "Ana, grávida, de top e legging pretos, sentada no chão em alongamento com o braço apoiado em uma bola de pilates.",
        "uso": "Gestação ativa: carrossel sobre exercício e fome, capa de Reels.",
        "fase": "gestacao",
        "enquadramento": "corpo inteiro no chão, horizonte baixo, muito ar no topo",
    },
    {
        "id": "ana-10-jeans-retrato",
        "origem": "drive/ensaio-profissional-gravida/IMG_9675.jpg",
        "alt": "Retrato próximo da Ana de camisa jeans, com as mãos juntas perto do rosto, sorrindo para a câmera.",
        "uso": "Retrato de proximidade: depoimento, recado da Ana, foto de perfil alternativa, sobre a Ana.",
        "fase": "todas",
        "enquadramento": "close, rosto e mãos, fundo claro",
    },
    {
        "id": "ana-11-evento-mao-no-queixo",
        "origem": "drive/evento-nutricao/v2_1ffaccaa.jpg",
        "alt": "Ana de blazer preto e vestido estampado, com a mão no queixo, sorri diante de um fundo escuro texturizado.",
        "uso": "Modo 40+ e menopausa, palestra e autoridade: capa de aula, evento, carrossel profundo.",
        "fase": "40-mais",
        "enquadramento": "três quartos, fundo escuro (combina com Mar Fundo)",
    },
    {
        "id": "ana-12-evento-bracos-cruzados",
        "origem": "drive/evento-nutricao/v2_2aec76e0.jpg",
        "alt": "Ana de blazer preto e vestido estampado, de braços cruzados, sorri diante de um fundo escuro texturizado.",
        "uso": "Modo 40+ e menopausa: anúncio, página do atendimento 40+, apresentação para parceiros.",
        "fase": "40-mais",
        "enquadramento": "três quartos, pose firme",
    },
    {
        "id": "ana-13-barco-lagoa",
        "origem": "drive/ensaio-gestante-antonio/IMG_0353.jpg",
        "alt": "Ana, grávida, de roupa clara, sentada em um barco de madeira na beira de uma lagoa com árvores, sorrindo.",
        "uso": "Gestação, luz natural ao ar livre: capa de série, abertura de e-mail, fundo de story com faixa sólida.",
        "fase": "gestacao",
        "enquadramento": "horizontal, paisagem com água; texto só sobre faixa sólida",
    },
    {
        "id": "ana-14-retrato-blusa-caramelo",
        "origem": "fotos/00-foto-de-perfil-atual.jpg",
        "alt": "Retrato da Ana de blusa caramelo, cabelo solto, olhando para a câmera com um sorriso leve, sobre fundo cinza-claro.",
        "uso": "Retrato institucional quente: perfil em plataformas, assinatura de e-mail, cartão digital.",
        "fase": "todas",
        "enquadramento": "busto, quadrado; arquivo de origem pequeno (965 px)",
    },
    {
        "id": "ana-15-escritorio-oculos",
        "origem": "fotos/03-retrato-escritorio-notebook-oculos-sorrindo.jpg",
        "alt": "Selfie da Ana de óculos e blusa preta, com o queixo apoiado na mão, diante do notebook e de um mapa-múndi na parede.",
        "uso": "Bastidores e dia a dia: story, abertura do capítulo de voz, conteúdo de rotina.",
        "fase": "todas",
        "enquadramento": "selfie, luz de casa; não usar em anúncio",
    },
    {
        "id": "ana-16-formatura-pao-de-acucar",
        "origem": "fotos/15-formatura-nutricao-diploma-pao-de-acucar.jpg",
        "alt": "Ana de beca e capelo mostra o canudo do diploma de Nutrição, com o Pão de Açúcar ao fundo.",
        "uso": "História e virada de rota: página Sobre a Ana, post de aniversário de profissão, apresentação.",
        "fase": "todas",
        "enquadramento": "quadrado, paisagem do Rio ao fundo",
    },
]

QUALIDADE = {"1600": 82, "640": 78}


def srgb(im):
    """Converte para sRGB usando o perfil embutido, se houver."""
    perfil = im.info.get("icc_profile")
    if perfil:
        try:
            import io

            origem = ImageCms.ImageCmsProfile(io.BytesIO(perfil))
            destino = ImageCms.createProfile("sRGB")
            im = ImageCms.profileToProfile(im, origem, destino, outputMode="RGB")
        except Exception:
            pass
    return im.convert("RGB")


def tratar(caminho):
    im = Image.open(caminho)
    im = ImageOps.exif_transpose(im)
    im = srgb(im)
    im = ImageEnhance.Contrast(im).enhance(1.03)
    im = ImageEnhance.Color(im).enhance(0.97)
    return im


def reduzir(im, lado):
    w, h = im.size
    escala = min(1.0, lado / max(w, h))
    if escala < 1:
        im = im.resize((round(w * escala), round(h * escala)), Image.LANCZOS)
        im = im.filter(ImageFilter.UnsharpMask(radius=0.8, percent=40, threshold=2))
    return im


def cor_media(im):
    p = im.resize((1, 1), Image.BOX).getpixel((0, 0))
    return "#%02X%02X%02X" % p[:3]


def assinatura(arq):
    h = hashlib.sha256(arq.read_bytes()).hexdigest()[:16]
    return "%s-%s" % (h, VERSAO_TRATAMENTO)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--forcar", action="store_true")
    ap.add_argument("--folha", action="store_true")
    ap.add_argument("--origem", default=str(ORIGEM) if ORIGEM else None)
    args = ap.parse_args()
    if not args.origem:
        print("ERRO: defina a pasta de origem com --origem, com a variável de ambiente ou em tools/origens.local.json")
        return 2
    org = Path(args.origem)

    cat_arq = SAIDA / "catalogo.json"
    antigo = {}
    if cat_arq.exists():
        try:
            antigo = {f["id"]: f for f in json.loads(cat_arq.read_text(encoding="utf-8"))["fotos"]}
        except Exception:
            antigo = {}

    itens, feitos, iguais = [], 0, 0
    for n, f in enumerate(FOTOS, 1):
        src = org / f["origem"]
        if not src.exists():
            print("ERRO: origem não encontrada: %s" % src)
            return 1
        ass = assinatura(src)
        destinos = {k: SAIDA / k / ("%s.webp" % f["id"]) for k in QUALIDADE}
        anterior = antigo.get(f["id"], {})
        if not args.forcar and anterior.get("assinatura") == ass and all(p.exists() for p in destinos.values()):
            iguais += 1
            item = dict(anterior)
        else:
            im = tratar(src)
            medidas = {}
            for k, q in QUALIDADE.items():
                r = reduzir(im, int(k))
                destinos[k].parent.mkdir(parents=True, exist_ok=True)
                r.save(destinos[k], "WEBP", quality=q, method=6)  # sem exif nem icc: sRGB implícito
                medidas[k] = list(r.size)
            w, h = medidas["1600"]
            item = {
                "assinatura": ass,
                "largura": w,
                "altura": h,
                "orientacao": "vertical" if h > w * 1.05 else ("horizontal" if w > h * 1.05 else "quadrada"),
                "proporcao": round(w / h, 4),
                "cor_media": cor_media(im),
                "kb_1600": destinos["1600"].stat().st_size // 1024,
                "kb_640": destinos["640"].stat().st_size // 1024,
            }
            feitos += 1
        item.update({
            "id": f["id"],
            "n": n,
            "arquivo": "assets/fotos/1600/%s.webp" % f["id"],
            "miniatura": "assets/fotos/640/%s.webp" % f["id"],
            "alt": f["alt"],
            "uso": f["uso"],
            "fase": f["fase"],
            "enquadramento": f["enquadramento"],
        })
        itens.append(item)

    ordem = ["id", "n", "arquivo", "miniatura", "largura", "altura", "orientacao", "proporcao",
             "cor_media", "fase", "alt", "uso", "enquadramento", "kb_1600", "kb_640", "assinatura"]
    catalogo = {
        "acervo": "Fotos reais da Ana Paula Costa · sistema Rota ap.",
        "tratamento": "rotação corrigida, sRGB, contraste +3%, saturação -3%, nitidez suave; sem recorte nem retoque; metadados removidos",
        "regras": [
            "Só a Ana, sozinha. Nenhuma foto com os filhos, o marido ou outras pessoas.",
            "Nenhuma foto com mão na barriga em peça da marca.",
            "Nenhuma imagem de pessoa gerada por IA.",
            "No modo 40+ e menopausa, só fotos com fase 40-mais ou todas.",
            "Texto sobre foto só em faixa sólida (Sálvia Ana, Mar Fundo ou Algodão).",
            "Uso comercial depende da autorização da Ana para as fotos dos ensaios (pendência P3).",
        ],
        "fotos": [{k: it[k] for k in ordem if k in it} for it in itens],
    }
    novo = json.dumps(catalogo, ensure_ascii=False, indent=2) + "\n"
    if not cat_arq.exists() or cat_arq.read_text(encoding="utf-8") != novo:
        cat_arq.write_text(novo, encoding="utf-8")

    # órfãos
    ids = {f["id"] for f in FOTOS}
    for k in QUALIDADE:
        for p in (SAIDA / k).glob("*.webp"):
            if p.stem not in ids:
                print("  órfã (remova se não for mais usada): %s" % p.relative_to(RAIZ))

    if args.folha:
        W, H = 320, 420
        folha = Image.new("RGB", (W * 4, H * ((len(itens) + 3) // 4)), (242, 240, 235))
        for i, it in enumerate(itens):
            im = Image.open(RAIZ / it["miniatura"])
            im.thumbnail((W - 12, H - 12))
            folha.paste(im, ((i % 4) * W + 6, (i // 4) * H + 6))
        folha.save(SAIDA / "_folha.jpg", quality=82)

    total = sum((SAIDA / k / ("%s.webp" % f["id"])).stat().st_size for f in FOTOS for k in QUALIDADE)
    print("Acervo de fotos: %d fotos (%d geradas, %d iguais), %.1f MB" % (len(itens), feitos, iguais, total / 1048576))
    return 0


if __name__ == "__main__":
    sys.exit(main())
