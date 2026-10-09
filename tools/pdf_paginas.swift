// Renderiza páginas de um PDF em PNG (macOS, PDFKit). Uso: swift tools/pdf_paginas.swift arquivo.pdf pasta-saida [largura]
import Foundation
import PDFKit
import AppKit
let a = CommandLine.arguments
guard a.count >= 3, let doc = PDFDocument(url: URL(fileURLWithPath: a[1])) else { print("uso: arquivo.pdf pasta [largura]"); exit(1) }
let largura = a.count > 3 ? CGFloat(Double(a[3]) ?? 800) : 800
try? FileManager.default.createDirectory(atPath: a[2], withIntermediateDirectories: true)
for i in 0..<doc.pageCount {
  guard let p = doc.page(at: i) else { continue }
  let r = p.bounds(for: .mediaBox); let e = largura / r.width
  let img = p.thumbnail(of: NSSize(width: r.width * e, height: r.height * e), for: .mediaBox)
  if let t = img.tiffRepresentation, let b = NSBitmapImageRep(data: t), let png = b.representation(using: .png, properties: [:]) {
    try? png.write(to: URL(fileURLWithPath: "\(a[2])/pagina-\(String(format: "%02d", i + 1)).png"))
  }
}
print("\(doc.pageCount) páginas")
