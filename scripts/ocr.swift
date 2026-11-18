import Foundation
import Vision
import PDFKit
import AppKit
guard CommandLine.arguments.count > 1 else { fputs("Usage: beru-ocr image [--json]\n", stderr); exit(2) }
let path = CommandLine.arguments[1]
let jsonMode = CommandLine.arguments.contains("--json")
func recognize(_ image: CGImage) throws -> String {
 let request = VNRecognizeTextRequest()
 request.recognitionLevel = .accurate
 request.recognitionLanguages = ["fr-FR", "en-US"]
 request.usesLanguageCorrection = true
 try VNImageRequestHandler(cgImage: image).perform([request])
 if jsonMode {
 let lines: [[String: Any]] = (request.results ?? []).compactMap { item in
 guard let candidate = item.topCandidates(1).first else { return nil }
 let b = item.boundingBox
 return ["text": candidate.string, "confidence": candidate.confidence, "box": [b.minX, 1-b.maxY, b.width, b.height]]
 }
 let data = try JSONSerialization.data(withJSONObject: ["lines": lines])
 return String(data: data, encoding: .utf8)!
 }
 return (request.results ?? []).compactMap { $0.topCandidates(1).first?.string }.joined(separator: "\n")
}
if path.lowercased().hasSuffix(".pdf"), let doc = PDFDocument(url: URL(fileURLWithPath:path)) {
 for i in 0..<doc.pageCount {
  guard let page = doc.page(at:i) else { continue }
  let image = page.thumbnail(of:NSSize(width:1800,height:2400),for:.mediaBox)
  if let cg = image.cgImage(forProposedRect:nil,context:nil,hints:nil) { print("## Page \(i+1)\n\n\(try recognize(cg))\n") }
 }
} else if let image = NSImage(contentsOfFile:path), let cg = image.cgImage(forProposedRect:nil,context:nil,hints:nil) { print(try recognize(cg)) }
