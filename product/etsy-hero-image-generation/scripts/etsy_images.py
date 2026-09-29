#!/usr/bin/env python3
"""
Etsy listing-image helpers: list / upload / delete / replace-hero, each write
followed by a re-fetch (never trust a 2xx alone - see etsy-api skill).

  etsy_images.py list    <listing_id>
  etsy_images.py upload  <listing_id> <image> [--rank N] [--alt "text"]
  etsy_images.py delete  <listing_id> <listing_image_id>
  etsy_images.py hero    <listing_id> <new_hero_image> [--keep-old-as-last OLD_LOCAL_FILE] [--alt "text"]

`hero` = the confirmed pattern: upload new with rank=1 -> verify present ->
DELETE the previous rank-1 image -> re-fetch and assert the new image is first.
Auth reuses listing-bot's OAuth module exactly as etsy-api documents.
"""
import argparse, json, os, sys, time
import requests

sys.path.insert(0, "/Volumes/data/projects/listing-bot/src")
from platforms.etsy_oauth import get_valid_access_token  # noqa: E402

BASE = "https://openapi.etsy.com/v3/application"
CID = open("/Volumes/data/secrets/etsy-api-key").read().strip()
SEC = open("/Volumes/data/secrets/etsy-api-secret").read().strip()
SHOP = json.load(open(os.path.expanduser("~/.config/listing-bot/etsy_tokens.json")))["shop_id"]


def H():
    return {"Authorization": f"Bearer {get_valid_access_token(CID)}", "x-api-key": f"{CID}:{SEC}"}


def images(lid, retry=True):
    r = requests.get(f"{BASE}/listings/{lid}/images", headers=H())
    r.raise_for_status()
    res = sorted(r.json()["results"], key=lambda i: i["rank"])
    if not res and retry:  # documented rate-limit false negative: wait, re-check once
        time.sleep(4)
        return images(lid, retry=False)
    return res


def show(lid):
    for i in images(lid):
        print(f"  rank {i['rank']:>2}  id {i['listing_image_id']}  {i['full_width']}x{i['full_height']}")


def upload(lid, path, rank=None, alt=None):
    data = {}
    if rank:
        data["rank"] = str(rank)
    if alt:
        data["alt_text"] = alt[:500]
    mime = "image/jpeg" if path.lower().endswith((".jpg", ".jpeg")) else "image/png"
    with open(path, "rb") as f:
        r = requests.post(f"{BASE}/shops/{SHOP}/listings/{lid}/images", headers=H(),
                          files={"image": (os.path.basename(path), f, mime)}, data=data)
    if r.status_code >= 300:
        sys.exit(f"UPLOAD FAILED {r.status_code}: {r.text[:400]}")
    new_id = r.json()["listing_image_id"]
    time.sleep(2)
    if new_id not in [i["listing_image_id"] for i in images(lid)]:
        time.sleep(5)
        if new_id not in [i["listing_image_id"] for i in images(lid)]:
            sys.exit(f"UPLOAD NOT VISIBLE: {new_id} missing from GET images after retry")
    print(f"uploaded {path} -> listing_image_id {new_id}")
    return new_id


def delete(lid, image_id):
    r = requests.delete(f"{BASE}/shops/{SHOP}/listings/{lid}/images/{image_id}", headers=H())
    if r.status_code == 404:  # fall back to listing-scoped form
        r = requests.delete(f"{BASE}/listings/{lid}/images/{image_id}", headers=H())
    if r.status_code >= 300:
        sys.exit(f"DELETE FAILED {r.status_code}: {r.text[:400]}")
    time.sleep(2)
    if image_id in [i["listing_image_id"] for i in images(lid)]:
        time.sleep(5)
        if image_id in [i["listing_image_id"] for i in images(lid)]:
            sys.exit(f"DELETE NOT APPLIED: {image_id} still present")
    print(f"deleted listing_image_id {image_id} (HTTP {r.status_code})")


def hero(lid, new_path, keep_old=None, alt=None):
    before = images(lid)
    old = before[0]["listing_image_id"]
    print(f"before: {len(before)} images, current hero {old}")
    new_id = upload(lid, new_path, rank=1, alt=alt)
    delete(lid, old)
    after = images(lid)
    if after[0]["listing_image_id"] != new_id:
        sys.exit(f"HERO NOT FIRST: first is {after[0]['listing_image_id']}, expected {new_id}")
    print(f"VERIFIED: new hero {new_id} is rank {after[0]['rank']}, old {old} gone")
    if keep_old:
        # rank defaults to 1 on Etsy's side, so an upload without an explicit rank
        # ties with the hero. Always pass the last position explicitly.
        upload(lid, keep_old, rank=len(images(lid)) + 1)
    show(lid)
    return new_id


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["list", "upload", "delete", "hero"])
    ap.add_argument("listing_id", type=int)
    ap.add_argument("arg", nargs="?")
    ap.add_argument("--rank", type=int)
    ap.add_argument("--alt")
    ap.add_argument("--keep-old-as-last")
    a = ap.parse_args()
    if a.cmd == "list":
        show(a.listing_id)
    elif a.cmd == "upload":
        upload(a.listing_id, a.arg, a.rank, a.alt); show(a.listing_id)
    elif a.cmd == "delete":
        delete(a.listing_id, int(a.arg)); show(a.listing_id)
    else:
        hero(a.listing_id, a.arg, a.keep_old_as_last, a.alt)
