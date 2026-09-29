#!/usr/bin/env python3
"""
Budget-guarded Fal.ai text-to-image call for Etsy listing BACKGROUNDS.

Same auth/request pattern the n8n "Content Image Generator" workflow already
uses in production (POST https://fal.run/<model>, header `Authorization: Key <key>`).
The only additions: a live price lookup before spending anything, a hard
per-call cost cap, and a spend log so batches can be audited afterwards.

Usage:
  fal_generate.py --prompt "..." --out bg.png [--model fal-ai/flux/dev]
                  [--width 1536 --height 1536] [--max-cost 0.10] [--dry-run]

--dry-run prints the model, megapixels and estimated cost and exits WITHOUT
calling the paid endpoint. Always dry-run a new prompt/size first.
"""
import argparse, json, os, sys, time, urllib.request

KEY_PATHS = ["/Volumes/data/secrets/content_studio_fal_api_key",
             "/Volumes/data/secrets/n8n_fal_api_key"]
SPEND_LOG = os.path.expanduser("~/.local/share/fal-spend.jsonl")


def load_key():
    for p in KEY_PATHS:
        if os.path.exists(p):
            k = open(p).read().strip()
            if k:
                return k
    sys.exit("BLOCKER: no Fal.ai key found at " + ", ".join(KEY_PATHS))


def http_json(url, key, body=None, timeout=180):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method="POST" if data else "GET",
                                 headers={"Authorization": f"Key {key}",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def unit_price(model, key):
    """Live price from Fal's platform API: returns (unit_price, unit)."""
    d = http_json(f"https://api.fal.ai/v1/models/pricing?endpoint_id={model}", key)
    p = d["prices"][0]
    return float(p["unit_price"]), p["unit"]


def estimate(model, key, w, h):
    price, unit = unit_price(model, key)
    mp = (w * h) / 1_000_000
    cost = price * mp if unit == "megapixels" else price  # "images" = flat per image
    return cost, price, unit, mp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="fal-ai/flux/dev")
    ap.add_argument("--width", type=int, default=1536)
    ap.add_argument("--height", type=int, default=1536)
    ap.add_argument("--steps", type=int, default=28)
    ap.add_argument("--seed", type=int)
    ap.add_argument("--max-cost", type=float, default=0.10,
                    help="refuse to run if one image would cost more than this (USD)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    key = load_key()
    cost, price, unit, mp = estimate(a.model, key, a.width, a.height)
    print(f"model={a.model} size={a.width}x{a.height} ({mp:.2f}MP) "
          f"price=${price}/{unit} est_cost=${cost:.4f}")
    if cost > a.max_cost:
        sys.exit(f"REFUSED: est ${cost:.4f} > --max-cost ${a.max_cost}")
    if a.dry_run:
        return

    body = {"prompt": a.prompt, "image_size": {"width": a.width, "height": a.height},
            "num_images": 1, "enable_safety_checker": True}
    if "schnell" in a.model:
        body["num_inference_steps"] = 4
    elif "flux/dev" in a.model:
        body["num_inference_steps"] = a.steps
    if a.seed is not None:
        body["seed"] = a.seed

    t0 = time.time()
    res = http_json(f"https://fal.run/{a.model}", key, body, timeout=300)
    img = res["images"][0]
    urllib.request.urlretrieve(img["url"], a.out)
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "model": a.model,
           "w": img.get("width"), "h": img.get("height"), "est_cost": round(cost, 4),
           "seed": res.get("seed"), "out": os.path.abspath(a.out),
           "secs": round(time.time() - t0, 1), "prompt": a.prompt}
    os.makedirs(os.path.dirname(SPEND_LOG), exist_ok=True)
    with open(SPEND_LOG, "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps({k: rec[k] for k in ("model", "w", "h", "est_cost", "seed", "out", "secs")}))


if __name__ == "__main__":
    main()
