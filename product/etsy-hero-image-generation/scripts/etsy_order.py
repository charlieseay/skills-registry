#!/usr/bin/env python3
"""Put a listing's images in an exact order.

Etsy can't move an image: a mid-list rank ties, and ties are served by
ascending image id. So: keep the longest prefix that is already right; for the
rest, delete what we drop, then place each remaining item in order (a moved
image is re-uploaded, then its old copy deleted). The listing never drops to
zero images or goes over Etsy's 20-image cap.

usage: etsy_order.py <listing_id> <workdir> <item> [<item> ...]
  item = an existing image id (keep, in this position)
       | a local file path (new image), optionally path::alt text
Images on the listing that are not named are deleted.
"""
import sys, os, time, json, urllib.request
sys.path.insert(0, "/Volumes/data/projects/listing-bot/src")
from platforms.etsy_shop import EtsyShop

lid, work, items = int(sys.argv[1]), sys.argv[2], sys.argv[3:]
os.makedirs(work, exist_ok=True)
s = EtsyShop()

def served():
    return sorted(s.images(lid), key=lambda i: (i["rank"], i["listing_image_id"]))

cur = served()
by_id = {i["listing_image_id"]: i for i in cur}
want = []
for it in items:
    if it.isdigit():
        if int(it) not in by_id:
            sys.exit(f"image {it} not on listing {lid}")
        want.append(("id", int(it)))
    else:
        path, _, alt = it.partition("::")
        if not os.path.exists(path):
            sys.exit(f"missing file {path}")
        want.append(("file", (path, alt or None)))

json.dump([{k: i.get(k) for k in ("listing_image_id", "rank", "url_fullxfull", "alt_text")} for i in cur],
          open(f"{work}/before-{lid}.json", "w"), indent=1)

# longest prefix already in place
k = 0
while k < len(want) and k < len(cur) and want[k] == ("id", cur[k]["listing_image_id"]):
    k += 1
keep_prefix = [cur[i]["listing_image_id"] for i in range(k)]

# Mutation order keeps the listing between 1 and 20 images the whole time
# (Etsy refuses to delete the last image, HTTP 400, and caps listings at 20):
#   1. delete images we're dropping, never the last one
#   2. for each remaining item in order: upload it at the end; if it is an existing
#      image being moved, delete the old copy right after its replacement lands
# 2026-10-16: deleting everything first left 10 live listings with one image, and
# uploading everything first hit the 20-image cap.
want_ids = {v for kind, v in want if kind == "id"}
dropped = [i for i in cur[k:] if i["listing_image_id"] not in want_ids]
for i in dropped:
    if len(s.images(lid)) > 1:
        s.delete_image(lid, i["listing_image_id"])
        i["_gone"] = True
new_ids = []
for kind, v in want[k:]:
    rank = len(s.images(lid)) + 1
    if kind == "id":
        p = f"{work}/{lid}-{v}.jpg"
        urllib.request.urlretrieve(by_id[v]["url_fullxfull"], p)
        new_ids.append(s.upload_image(lid, p, rank=rank, alt=by_id[v].get("alt_text")))
        s.delete_image(lid, v)
    else:
        path, alt = v
        new_ids.append(s.upload_image(lid, path, rank=rank, alt=alt))
    time.sleep(1)
for i in dropped:
    if not i.get("_gone"):
        s.delete_image(lid, i["listing_image_id"])
print(f"kept first {k}, placed {len(new_ids)}, dropped {len(dropped)}")

time.sleep(3)
final = [i["listing_image_id"] for i in served()]
expect = keep_prefix + new_ids
print("final:", final)
print("ORDER OK" if final == expect else f"ORDER MISMATCH expected {expect}")
sys.exit(0 if final == expect else 1)
