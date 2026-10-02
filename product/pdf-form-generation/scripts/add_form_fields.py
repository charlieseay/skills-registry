#!/usr/bin/env python3
"""
Generalized version of pdf-form-generation's add_form_fields.py (was
hardcoded to one demo product/page). Reads pdf-form-fields.json (multi-page
format from the generalized render_layout.py) and overlays real AcroForm
/Widget annotations on each page's rendered PDF, merging all pages into one
output file with one shared /AcroForm.

Field type is now driven by a data-type convention baked into field names
rather than a hardcoded name allowlist: any field name containing "notes"
or starting with "name"/"month"/"year" is a text field; everything else
(amount fields, checkboxes) defaults to text too, since this product has no
checkboxes -- a future product with checkboxes should extend TEXT_FIELD_HINTS
or restore the /Btn branch from the original demo script.

CRITICAL FIX (2026-10-01, confirmed on product-item-225 after a 5-round
debugging cycle -- see pdf-form-generation SKILL.md's "Illustrated themes"
section for the full story): pypdf's PdfWriter.append() silently drops
/Pattern (CSS gradient/shading) resources when called once per page across
SEPARATE PdfReader objects (the naive "loop and append each page" approach
this script used to take). The script can run with no errors, report the
correct field count, and still ship a customer-facing file with the
gradient/background completely missing -- field-count correctness and
visual-content correctness are independent failure surfaces, verify both.
Fix: merge all per-page PDFs into ONE file via Ghostscript first (which
preserves Pattern/Shading resources correctly across pages), then call
pypdf.append() exactly once against that single merged source. Any product
using a CSS gradient/pattern background MUST use this merge step --
products with a plain solid-color or no background are not affected by this
specific bug, but using the merge path is harmless for them too, so it is
now the default here rather than a per-product opt-in.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject, BooleanObject, DictionaryObject, NameObject,
    NumberObject, TextStringObject, DecodedStreamObject,
)

PX_TO_PT = 72 / 96

TEXT_FIELD_HINTS = ("name", "month", "year", "notes", "budget", "actual",
                     "income", "expenses", "saved")


def is_text_field(field_name: str) -> bool:
    return any(hint in field_name for hint in TEXT_FIELD_HINTS)


def to_pdf_rect(r, page_h_in, margin_in):
    page_h_pt = page_h_in * 72
    margin_pt = margin_in * 72
    x0 = margin_pt + r["x"] * PX_TO_PT
    x1 = margin_pt + (r["x"] + r["w"]) * PX_TO_PT
    top_from_page_top = margin_pt + r["y"] * PX_TO_PT
    bottom_from_page_top = margin_pt + (r["y"] + r["h"]) * PX_TO_PT
    ury = page_h_pt - top_from_page_top
    lly = page_h_pt - bottom_from_page_top
    return [x0, lly, x1, ury]


def make_appearance_stream(writer, rect):
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]
    stream = DecodedStreamObject()
    stream.set_data(b"")
    stream[NameObject("/Type")] = NameObject("/XObject")
    stream[NameObject("/Subtype")] = NameObject("/Form")
    stream[NameObject("/FormType")] = NumberObject(1)
    stream[NameObject("/BBox")] = ArrayObject(
        [NumberObject(0), NumberObject(0), NumberObject(w), NumberObject(h)]
    )
    resources = DictionaryObject()
    font_dict = DictionaryObject()
    helv = DictionaryObject({
        NameObject("/Type"): NameObject("/Font"),
        NameObject("/Subtype"): NameObject("/Type1"),
        NameObject("/BaseFont"): NameObject("/Helvetica"),
    })
    font_dict[NameObject("/Helv")] = writer._add_object(helv)
    resources[NameObject("/Font")] = font_dict
    stream[NameObject("/Resources")] = resources
    return writer._add_object(stream)


def merge_pdfs_with_ghostscript(pdf_paths, output_path):
    """Merge PDFs via Ghostscript, which preserves Pattern/Shading resources
    that pypdf.PdfWriter.append() drops when crossing PdfReader boundaries."""
    cmd = [
        "gs", "-q", "-dNOPAUSE", "-dBATCH", "-dSAFER",
        "-sDEVICE=pdfwrite", f"-sOutputFile={output_path}",
        "-dEmbedAllFonts=true", "-dSubsetFonts=false", "-dCompressFonts=false",
        "-dPreserveColorInfo=true", "-dPreserveHalftoneInfo=true",
        "-dPreserveOverprintSettings=true",
    ] + [str(p) for p in pdf_paths]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Ghostscript merge failed: {result.stderr}")
    print(f"Merged {len(pdf_paths)} PDFs with Ghostscript -> {output_path}")


def main():
    in_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else in_dir / "output.pdf"

    with open(in_dir / "pdf-form-fields.json") as f:
        data = json.load(f)

    # Collect per-page PDF paths in order, then merge via Ghostscript into ONE
    # file before pypdf ever touches it -- see the CRITICAL FIX note above.
    pdf_paths = [(in_dir / page_meta["pdf_path"]).resolve() for page_meta in data["pages"]]

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        merged_pdf = tmp.name

    try:
        merge_pdfs_with_ghostscript(pdf_paths, merged_pdf)
        merged_reader = PdfReader(merged_pdf)
        writer = PdfWriter()
        writer.append(merged_reader)
        all_field_refs = []

        for i, page_meta in enumerate(data["pages"]):
            page = writer.pages[i]
            if page.get(NameObject("/Annots")) is None:
                page[NameObject("/Annots")] = ArrayObject()

            for r in page_meta["rects"]:
                rect = to_pdf_rect(r, page_meta["page_h_in"], page_meta["margin_in"])
                field_name = f"{page_meta['name']}__{r['field']}"
                is_text = is_text_field(r["field"])

                field_dict = DictionaryObject()
                field_dict[NameObject("/Type")] = NameObject("/Annot")
                field_dict[NameObject("/Subtype")] = NameObject("/Widget")
                field_dict[NameObject("/Rect")] = ArrayObject([NumberObject(v) for v in rect])
                field_dict[NameObject("/T")] = TextStringObject(field_name)
                field_dict[NameObject("/F")] = NumberObject(4)
                field_dict[NameObject("/P")] = page.indirect_reference

                if is_text:
                    field_dict[NameObject("/FT")] = NameObject("/Tx")
                    field_dict[NameObject("/DA")] = TextStringObject("/Helv 9 Tf 0 g")
                    if r["field"].endswith("notes"):
                        field_dict[NameObject("/Ff")] = NumberObject(1 << 12)
                else:
                    field_dict[NameObject("/FT")] = NameObject("/Btn")
                    field_dict[NameObject("/AS")] = NameObject("/Off")
                    field_dict[NameObject("/DA")] = TextStringObject("/Helv 0 Tf")

                border = DictionaryObject({NameObject("/W"): NumberObject(0)})
                field_dict[NameObject("/BS")] = border
                ap_n = make_appearance_stream(writer, rect)
                field_dict[NameObject("/AP")] = DictionaryObject({NameObject("/N"): ap_n})

                field_ref = writer._add_object(field_dict)
                all_field_refs.append(field_ref)
                page[NameObject("/Annots")].append(field_ref)

        acroform = DictionaryObject()
        acroform[NameObject("/Fields")] = ArrayObject(all_field_refs)
        acroform[NameObject("/NeedAppearances")] = BooleanObject(True)
        dr = DictionaryObject()
        font_dict = DictionaryObject()
        font_dict[NameObject("/Helv")] = writer._add_object(DictionaryObject({
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }))
        dr[NameObject("/Font")] = font_dict
        acroform[NameObject("/DR")] = dr
        writer._root_object[NameObject("/AcroForm")] = writer._add_object(acroform)

        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "wb") as f:
            writer.write(f)

        print(f"wrote {out_path} with {len(all_field_refs)} fields across {len(data['pages'])} pages")
    finally:
        Path(merged_pdf).unlink(missing_ok=True)


if __name__ == "__main__":
    main()
