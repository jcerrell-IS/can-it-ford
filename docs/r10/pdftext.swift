// Extract text from a PDF using Apple's PDFKit.
//
// Written because this Mac has no pdftotext, no numpy, and no PyObjC, and
// because a stdlib zlib extractor fails on any PDF that uses subset fonts with
// custom CMaps, which is most modern journal typesetting. PDFKit handles the
// CMaps, so this is the reliable identity check.
//
// usage: swift pdftext.swift <file.pdf> [maxPages] [maxChars]
import Foundation
import PDFKit

let args = CommandLine.arguments
guard args.count > 1 else { FileHandle.standardError.write("usage: pdftext.swift <file> [pages] [chars]\n".data(using: .utf8)!); exit(2) }
let maxPages = args.count > 2 ? Int(args[2]) ?? 1 : 1
let maxChars = args.count > 3 ? Int(args[3]) ?? 3000 : 3000

guard let doc = PDFDocument(url: URL(fileURLWithPath: args[1])) else {
    print("PDFKIT_OPEN_FAILED"); exit(1)
}
var out = ""
for i in 0..<min(maxPages, doc.pageCount) {
    if let p = doc.page(at: i), let s = p.string { out += s + "\n" }
    if out.count >= maxChars { break }
}
out = out.replacingOccurrences(of: "\n", with: " ")
out = out.replacingOccurrences(of: "\\s+", with: " ", options: .regularExpression)
print(String(out.prefix(maxChars)))
