/* P3: até a autorização por escrito da Ana, as fotos dela ficam fora do repositório público.
   No endereço publicado, cada foto que não carrega vira uma moldura "autorização em confirmação". */
(function () {
  var ALVO = /assets\/(fotos|redes|aplicacoes\/site|referencia|producao\/(legenda|cor|zona-segura))\//;
  function reservar(im) {
    if (!im || im.tagName !== "IMG" || !ALVO.test(im.getAttribute("src") || "") || !im.parentNode) return;
    var d = document.createElement("span"), w = +im.getAttribute("width"), h = +im.getAttribute("height");
    d.className = "foto-reservada" + (im.className ? " " + im.className : "");
    d.setAttribute("role", "img");
    d.setAttribute("aria-label", "Foto da Ana: autorização de uso em confirmação");
    d.style.cssText = "display:flex;align-items:center;justify-content:center;text-align:center;box-sizing:border-box;width:100%;max-width:100%;" +
      (w && h ? "aspect-ratio:" + w + "/" + h + ";" : "height:100%;") +
      "padding:12px;background:var(--cor-pedra);color:var(--cor-grafite);font:600 13px/1.35 var(--fonte-texto);border-radius:inherit";
    d.textContent = "Foto da Ana · autorização em confirmação [P3]";
    im.parentNode.replaceChild(d, im);
    var a = d.closest ? d.closest("a[download]") : null;
    if (a) { a.removeAttribute("href"); a.removeAttribute("download"); a.setAttribute("aria-disabled", "true"); }
  }
  document.addEventListener("error", function (e) { reservar(e.target); }, true);
  function varrer() { Array.prototype.forEach.call(document.images, function (i) { if (i.complete && !i.naturalWidth && i.getAttribute("src")) reservar(i); }); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", varrer); else varrer();
  window.addEventListener("load", varrer);
})();

/* Páginas de apoio: botão Copiar e botão Baixar arquivo de texto.
   <button data-copiar-de="#id">  copia o texto do elemento (pre, textarea ou outro)
   <button data-copiar="texto">   copia o texto do atributo
   <button data-baixar-de="#id" data-nome="arquivo.html" data-tipo="text/html">  baixa o texto como arquivo */
(function () {
  "use strict";
  function textoDe(sel) {
    var el = document.querySelector(sel);
    if (!el) return "";
    return (el.value !== undefined && el.tagName === "TEXTAREA") ? el.value : el.textContent;
  }
  function copiar(texto) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(texto);
    return new Promise(function (ok, falha) {
      try {
        var t = document.createElement("textarea");
        t.value = texto; t.setAttribute("readonly", ""); t.style.position = "fixed"; t.style.opacity = "0";
        document.body.appendChild(t); t.select(); document.execCommand("copy"); document.body.removeChild(t); ok();
      } catch (e) { falha(e); }
    });
  }
  function avisar(b, msg) {
    var r = b.querySelector("[data-rotulo]") || b;
    var antes = r.getAttribute("data-original") || r.textContent;
    r.setAttribute("data-original", antes);
    r.textContent = msg; b.setAttribute("data-copiado", "");
    setTimeout(function () { r.textContent = antes; b.removeAttribute("data-copiado"); }, 1800);
  }
  document.addEventListener("click", function (ev) {
    var b = ev.target.closest("[data-copiar],[data-copiar-de]");
    if (b) {
      var texto = b.hasAttribute("data-copiar") ? b.getAttribute("data-copiar") : textoDe(b.getAttribute("data-copiar-de"));
      copiar(texto.replace(/^\n+|\s+$/g, "")).then(function () { avisar(b, "Copiado"); }, function () { avisar(b, "Selecione e copie"); });
      return;
    }
    var d = ev.target.closest("[data-baixar-de]");
    if (d) {
      var blob = new Blob([textoDe(d.getAttribute("data-baixar-de")).replace(/^\n+/, "")], { type: (d.getAttribute("data-tipo") || "text/plain") + ";charset=utf-8" });
      var a = document.createElement("a");
      a.href = URL.createObjectURL(blob); a.download = d.getAttribute("data-nome") || "trecho.txt";
      document.body.appendChild(a); a.click(); document.body.removeChild(a);
      setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
      avisar(d, "Baixado");
    }
  });
})();
