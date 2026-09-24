#!/usr/bin/env python3
"""
Overlay REAL fillable AcroForm fields (checkboxes + text fields) onto the
static Playwright-rendered layout, positioned exactly on top of the visual
boxes/lines using coordinates captured from the live DOM.

pypdf 6.x removed the old add_text_field()/add_checkbox() convenience
helpers, so fields are built here at the low level: each is a /Widget
annotation dict registered on the page's /Annots array and in the document's
/AcroForm /Fields array, with real appearance streams (/AP) so the check
mark actually renders in a PDF viewer, not just passes a field-presence
check.
"""
import json
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject, BooleanObject, DictionaryObject, NameObject,
    NumberObject, TextStringObject, DecodedStreamObject,
)

with open("/tmp/pdf-form-fields.json") as f:
    data = json.load(f)

PAGE_H_PT = data["page_h_in"] * 72
MARGIN_PT = data["margin_in"] * 72
PX_TO_PT = 72 / 96


def to_pdf_rect(r):
    x0 = MARGIN_PT + r["x"] * PX_TO_PT
    x1 = MARGIN_PT + (r["x"] + r["w"]) * PX_TO_PT
    top_from_page_top = MARGIN_PT + r["y"] * PX_TO_PT
    bottom_from_page_top = MARGIN_PT + (r["y"] + r["h"]) * PX_TO_PT
    ury = PAGE_H_PT - top_from_page_top
    lly = PAGE_H_PT - bottom_from_page_top
    return [x0, lly, x1, ury]


reader = PdfReader("/tmp/pdf-form-layout.pdf")
writer = PdfWriter()
writer.append(reader)
page = writer.pages[0]

if page.get(NameObject("/Annots")) is None:
    page[NameObject("/Annots")] = ArrayObject()


def make_appearance_stream(writer, rect, draw_ops):
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]
    stream = DecodedStreamObject()
    stream.set_data(draw_ops.encode("latin-1"))
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


text_field_refs = []
checkbox_field_refs = []

for r in data["rects"]:
    rect = to_pdf_rect(r)
    field_name = r["field"]
    field_dict = DictionaryObject()
    field_dict[NameObject("/Type")] = NameObject("/Annot")
    field_dict[NameObject("/Subtype")] = NameObject("/Widget")
    field_dict[NameObject("/Rect")] = ArrayObject([NumberObject(v) for v in rect])
    field_dict[NameObject("/T")] = TextStringObject(field_name)
    field_dict[NameObject("/F")] = NumberObject(4)  # Print flag
    field_dict[NameObject("/P")] = page.indirect_reference

    if field_name in ("name", "notes"):
        field_dict[NameObject("/FT")] = NameObject("/Tx")
        field_dict[NameObject("/DA")] = TextStringObject("/Helv 10 Tf 0 g")
        if field_name == "notes":
            field_dict[NameObject("/Ff")] = NumberObject(1 << 12)  # multiline
        border = DictionaryObject({NameObject("/W"): NumberObject(0)})
        field_dict[NameObject("/BS")] = border
        ap_n = make_appearance_stream(writer, rect, "")
        field_dict[NameObject("/AP")] = DictionaryObject({NameObject("/N"): ap_n})

        field_ref = writer._add_object(field_dict)
        text_field_refs.append(field_ref)
    else:
        field_dict[NameObject("/FT")] = NameObject("/Btn")
        field_dict[NameObject("/AS")] = NameObject("/Off")
        field_dict[NameObject("/V")] = NameObject("/Off")

        on_ap = make_appearance_stream(
            writer, rect,
            f"1 1 1 RG 0 0 0 rg {rect[2]-rect[0]:.2f} 0 m 0 0 l 0 {rect[3]-rect[1]:.2f} l "
            f"{rect[2]-rect[0]:.2f} {rect[3]-rect[1]:.2f} l f "
            f"1 0 0 RG 2 2 m {rect[2]-rect[0]-2:.2f} {rect[3]-rect[1]-2:.2f} l S "
            f"2 {rect[3]-rect[1]-2:.2f} m {rect[2]-rect[0]-2:.2f} 2 l S"
        )
        off_ap = make_appearance_stream(writer, rect, "")

        field_dict[NameObject("/AP")] = DictionaryObject({
            NameObject("/N"): DictionaryObject({
                NameObject("/Yes"): on_ap,
                NameObject("/Off"): off_ap,
            })
        })

        field_ref = writer._add_object(field_dict)
        checkbox_field_refs.append(field_ref)

    page[NameObject("/Annots")].append(field_ref)

all_field_refs = text_field_refs + checkbox_field_refs

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

with open("/tmp/pdf-form-poc-2026-09-23.pdf", "wb") as f:
    writer.write(f)

print(f"wrote /tmp/pdf-form-poc-2026-09-23.pdf with {len(all_field_refs)} fields")
