#!/usr/bin/env python3
"""Gera dist-skill/branding-ana-costa.zip, o pacote da skill para claude.ai, ChatGPT e Codex.

O ZIP tem a pasta branding-ana-costa/ no topo e só o que a skill precisa para operar:
  SKILL.md, references/, agents/openai.yaml, tokens.css, tokens.json, lockup.html, guia-de-uso.html,
  o estilo das páginas de apoio, a marca (SVG, PNG de 512 e 1024 px, favicon, prévia de link),
  a forma (Rota, régua, moldura, padrão, ícones), as fontes (licença aberta), os modelos de
  assinatura de e-mail e plano alimentar, a paleta e a legenda do kit de produção e o catálogo
  de fotos REESCRITO para as URLs públicas do GitHub Pages.

Fotos, vídeos, PNG de redes e o manual não viajam no ZIP (pesados): dentro do pacote (nunca no
repositório), todo caminho relativo de HTML para um arquivo que não está no ZIP vira URL absoluta
do GitHub Pages, e o catalogo.json aponta as fotos para o Pages.

Falha (código 1) se: ZIP com 10 MB ou mais, soma descompactada acima de 25 MB, mais de 400
arquivos, algum arquivo acima de 5 MB, description acima de 1.024 caracteres, SKILL.md com 500
linhas ou mais, nome divergente, SKILL.md ausente no topo, mais de um SKILL.md, link relativo de
SKILL.md ou references/ para arquivo ausente no pacote.

Uso:
  python3 tools/empacotar_skill.py
"""
import io
import json
import re
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
NOME = "branding-ana-costa"
PAGES = "https://rafaelnasch.github.io/branding-ana-costa/"
SAIDA = RAIZ / "dist-skill" / f"{NOME}.zip"
MB = 1024 * 1024
LIM_ZIP, LIM_SOMA, LIM_ARQ, LIM_N = 10 * MB, 25 * MB, 5 * MB, 400

RAIZ_ARQS = ["SKILL.md", "tokens.css", "tokens.json", "agents/openai.yaml", "lockup.html", "guia-de-uso.html",
             "assets/paginas/paginas.css", "assets/paginas/paginas.js"]
PADROES = [
    "references/*.md",
    "assets/marca/svg/*.svg",
    "assets/marca/png/*-512.png",
    "assets/marca/png/*-1024.png",
    "assets/marca/favicon/*",
    "assets/marca/og/*.png",
    "assets/forma/*.svg",
    "assets/forma/icones-destaques/*.svg",
    "assets/forma/icones-destaques/png/*-1080.png",
    "assets/fontes/*.ttf",
    "assets/fontes/OFL-*.txt",
    "assets/fontes/web/*.woff2",
    "assets/aplicacoes/*.html",
    "assets/aplicacoes/*.png",
    "assets/producao/README.md",
    "assets/producao/paleta/*",
    "assets/producao/legenda/*.json",
    "assets/producao/legenda/*.srt",
    "assets/producao/cor/*.cube",
]


def lista():
    arqs = list(RAIZ_ARQS)
    for padrao in PADROES:
        arqs += sorted(str(p.relative_to(RAIZ)) for p in RAIZ.glob(padrao)
                       if p.is_file() and p.name != ".DS_Store")
    arqs.append("assets/fotos/catalogo.json")
    faltam = [a for a in arqs if not (RAIZ / a).is_file()]
    if faltam:
        sys.exit("arquivos esperados que não existem: " + ", ".join(faltam))
    return list(dict.fromkeys(arqs))


# caminho relativo em atributo HTML (href, src, srcset, data-*) ou em url() de CSS
REF = re.compile(r"""(?P<pre>(?:href|src|data-[a-z-]+)=["']|url\(["']?|,\s*|srcset=["'])(?P<cam>(?:assets/|[a-z0-9-]+\.html|tokens\.(?:css|json))[^"'\s)#?]*)""")


def reescreve(texto, no_pacote):
    trocas = 0

    def troca(m):
        nonlocal trocas
        cam = m.group("cam")
        if cam in no_pacote:
            return m.group(0)
        trocas += 1
        return m.group("pre") + PAGES + cam

    return REF.sub(troca, texto), trocas


def catalogo_absoluto(texto):
    dados = json.loads(texto)

    def anda(o):
        if isinstance(o, dict):
            return {k: anda(v) for k, v in o.items()}
        if isinstance(o, list):
            return [anda(v) for v in o]
        if isinstance(o, str) and o.startswith("assets/"):
            return PAGES + o
        return o

    dados = anda(dados)
    dados["_pacote"] = ("Catálogo do pacote da skill: as fotos não viajam no ZIP e são servidas pelo GitHub Pages "
                        "nas URLs absolutas. No repositório, o mesmo catálogo usa caminhos relativos.")
    return json.dumps(dados, ensure_ascii=False, indent=2) + "\n"


def monta(arqs):
    conteudo, trocas = {}, {}
    no_pacote = set(arqs)
    for a in arqs:
        b = (RAIZ / a).read_bytes()
        if a.endswith((".html", ".css")):
            t, n = reescreve(b.decode("utf-8"), no_pacote)
            b, trocas[a] = t.encode("utf-8"), n
        elif a == "assets/fotos/catalogo.json":
            b = catalogo_absoluto(b.decode("utf-8")).encode("utf-8")
        conteudo[a] = b
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for a, b in conteudo.items():
            info = zipfile.ZipInfo(f"{NOME}/{a}", date_time=(2026, 10, 9, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, b, compresslevel=9)
    return buf.getvalue(), conteudo, trocas


def confere(zip_bytes, conteudo):
    erros = []
    soma = sum(len(b) for b in conteudo.values())
    if len(zip_bytes) >= LIM_ZIP:
        erros.append(f"ZIP com {len(zip_bytes)/MB:.2f} MB (precisa ficar abaixo de 10 MB)")
    if soma > LIM_SOMA:
        erros.append(f"descompactado com {soma/MB:.2f} MB (limite 25 MB)")
    if len(conteudo) > LIM_N:
        erros.append(f"{len(conteudo)} arquivos (limite {LIM_N})")
    for a, b in conteudo.items():
        if len(b) > LIM_ARQ:
            erros.append(f"{a} com {len(b)/MB:.2f} MB (limite 5 MB por arquivo)")
        if a.lower().endswith((".jpg", ".jpeg", ".webp", ".mp4", ".mov")):
            erros.append(f"{a}: foto ou vídeo não entra no pacote")
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        nomes = z.namelist()
    if {n.split("/")[0] for n in nomes} != {NOME}:
        erros.append(f"pasta de topo diferente de {NOME}")
    skills = [n for n in nomes if n.endswith("SKILL.md")]
    if len(skills) != 1 or f"{NOME}/SKILL.md" not in nomes:
        erros.append("o pacote precisa de exatamente um SKILL.md, no topo da pasta")
    skill = conteudo.get("SKILL.md", b"").decode("utf-8")
    fm = re.match(r"^---\n(.*?)\n---\n", skill, re.S)
    nome = desc = ""
    if fm:
        m = re.search(r"^name:\s*(.+)$", fm.group(1), re.M)
        nome = m.group(1).strip().strip("\"'") if m else ""
        m = re.search(r"^description:\s*(.+)$", fm.group(1), re.M)
        desc = m.group(1).strip() if m else ""
        if desc[:1] in "\"'" and desc[-1:] == desc[:1]:
            desc = desc[1:-1]
    if nome != NOME:
        erros.append(f"name '{nome}' diferente de {NOME}")
    if not 1 <= len(desc) <= 1024:
        erros.append(f"description com {len(desc)} caracteres (limite 1.024)")
    linhas = skill.count("\n") + (0 if skill.endswith("\n") else 1)
    if linhas >= 500:
        erros.append(f"SKILL.md com {linhas} linhas (limite: menos de 500)")
    for a, b in conteudo.items():
        if not (a == "SKILL.md" or (a.startswith("references/") and a.endswith(".md"))):
            continue
        base = Path(a).parent
        for alvo in re.findall(r"\]\(([^)\s]+)\)", b.decode("utf-8")):
            if re.match(r"(https?:|mailto:|#)", alvo):
                continue
            partes = []
            for p in (base / alvo.split("#")[0]).as_posix().split("/"):
                if p == "..":
                    if partes:
                        partes.pop()
                elif p not in ("", "."):
                    partes.append(p)
            if "/".join(partes) not in conteudo:
                erros.append(f"{a}: link relativo para arquivo ausente no pacote: {alvo}")
    return erros, soma, linhas, len(desc)


def main():
    arqs = lista()
    zip_bytes, conteudo, trocas = monta(arqs)
    erros, soma, linhas, ndesc = confere(zip_bytes, conteudo)
    SAIDA.parent.mkdir(exist_ok=True)
    SAIDA.write_bytes(zip_bytes)
    maior = max(conteudo.items(), key=lambda kv: len(kv[1]))
    print(f"pacote: {SAIDA.relative_to(RAIZ)}")
    print(f"ZIP {len(zip_bytes)/MB:.2f} MB · descompactado {soma/MB:.2f} MB · {len(conteudo)} arquivos · "
          f"maior arquivo {maior[0]} ({len(maior[1])/MB:.2f} MB)")
    print(f"SKILL.md {linhas} linhas · description {ndesc} caracteres")
    print("caminhos reescritos para o Pages: " + (", ".join(f"{k} {v}" for k, v in trocas.items() if v) or "nenhum"))
    if erros:
        for e in erros:
            print("  FALHA:", e)
        sys.exit(1)
    print("limites atendidos")


if __name__ == "__main__":
    main()
