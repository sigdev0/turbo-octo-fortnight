import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from clipper.download import load_settings
from clipper.pipeline import apply_preset, batch, process
from clipper.settings_schema import apply_overrides, parse_override


def _overrides(args):
    settings = load_settings()
    out = {}
    for token in getattr(args, "set", None) or []:
        try:
            key, val = parse_override(token, settings)
        except ValueError as e:
            raise SystemExit(f"--set error: {e}") from e
        out[key] = val
    return out


def cmd_process(args):
    settings = load_settings()
    process(
        args.url,
        settings,
        name=args.name,
        style=args.style,
        max_clips=args.max_clips,
        skip_transcribe=args.skip_transcribe or args.resume,
        skip_rank=args.skip_rank or args.resume,
        preset=args.preset,
        overrides=_overrides(args),
    )


def cmd_transcribe(args):
    from clipper.transcribe import transcribe

    settings = load_settings()
    t = transcribe(args.audio, settings, out_path=args.out)
    print(f"backend={t['backend']} segments={len(t['segments'])} lang={t['lang']}")


def cmd_rank(args):
    from clipper.prefilter import prefilter
    from clipper.rank import rank

    settings = load_settings()
    with open(args.transcript) as f:
        t = json.load(f)
    cands = prefilter(t, settings)
    print(f"{len(cands)} candidates")
    ranked, meta = rank(cands, settings, out_path=args.out)
    print(f"model={meta['model']} tokens={meta['total_tokens']}")
    for r in ranked[:10]:
        print(f"[{r['id']}] score={r['score']} {r['hook'][:80]}")


def cmd_clip(args):
    from clipper.clip import cut_clips

    settings = apply_preset(load_settings(), args.preset)
    settings = apply_overrides(settings, _overrides(args))
    with open(args.ranked) as f:
        ranked = json.load(f)
    made = cut_clips(
        args.source,
        ranked,
        args.out_dir,
        settings,
        style=args.style,
        max_clips=args.max_clips,
    )
    for m in made:
        print(m["clip"])


def _preset_arg(p):
    p.add_argument(
        "--preset", default=None, help="shorts|tiktok|reels (config/presets/)"
    )


def _set_arg(p):
    p.add_argument(
        "--set",
        action="append",
        default=[],
        metavar="SECTION.KEY=VALUE",
        help="per-run settings override, repeatable (e.g. clips.layout=fit)",
    )


def cmd_batch(args):
    settings = load_settings()
    res = batch(
        settings,
        sources_path=args.sources,
        style=args.style,
        max_clips=args.max_clips,
        skip_transcribe=args.skip_transcribe or args.resume,
        skip_rank=args.skip_rank or args.resume,
        preset=args.preset,
        overrides=_overrides(args),
    )
    if res["failed"]:
        raise SystemExit(1)


def cmd_costs(args):
    from clipper.pipeline import COSTS_LOG

    total = {"groq_usd": 0.0, "router_usd": 0.0, "runs": 0, "tokens": 0}
    if not os.path.exists(COSTS_LOG):
        print(f"no cost log yet ({COSTS_LOG})")
        return
    month = args.month
    with open(COSTS_LOG) as f:
        for line in f:
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            if month and not e.get("ts", "").startswith(month):
                continue
            total["runs"] += 1
            total["groq_usd"] += (e.get("groq") or {}).get("usd", 0)
            total["router_usd"] += e.get("router_usd", 0)
            total["tokens"] += (e.get("rank") or {}).get("total_tokens", 0)
    print(
        f"runs={total['runs']} tokens={total['tokens']} "
        f"groq_usd={total['groq_usd']:.4f} router_usd={total['router_usd']:.4f}"
    )


def main():
    p = argparse.ArgumentParser(prog="clipper")
    sub = p.add_subparsers(dest="cmd", required=True)

    pr = sub.add_parser("process", help="full pipeline: url -> clips")
    pr.add_argument("url")
    pr.add_argument("--name", default="job")
    pr.add_argument("--style", default=None)
    pr.add_argument("--max-clips", type=int, default=None)
    pr.add_argument("--skip-transcribe", action="store_true")
    pr.add_argument("--skip-rank", action="store_true")
    pr.add_argument("--resume", action="store_true")
    _preset_arg(pr)
    _set_arg(pr)
    pr.set_defaults(fn=cmd_process)

    tr = sub.add_parser("transcribe", help="audio -> transcript json")
    tr.add_argument("audio")
    tr.add_argument("--out", default="transcript.json")
    tr.set_defaults(fn=cmd_transcribe)

    rk = sub.add_parser("rank", help="transcript -> ranked candidates")
    rk.add_argument("transcript")
    rk.add_argument("--out", default="ranked.json")
    rk.set_defaults(fn=cmd_rank)

    cl = sub.add_parser("clip", help="ranked + source -> mp4 clips")
    cl.add_argument("source")
    cl.add_argument("ranked")
    cl.add_argument("--out-dir", default="output/job")
    cl.add_argument("--style", default=None)
    cl.add_argument("--max-clips", type=int, default=None)
    _preset_arg(cl)
    _set_arg(cl)
    cl.set_defaults(fn=cmd_clip)

    bt = sub.add_parser("batch", help="process all sources in sources.yaml")
    bt.add_argument("--sources", default="config/sources.yaml")
    bt.add_argument("--style", default=None)
    bt.add_argument("--max-clips", type=int, default=None)
    bt.add_argument("--skip-transcribe", action="store_true")
    bt.add_argument("--skip-rank", action="store_true")
    bt.add_argument("--resume", action="store_true")
    _preset_arg(bt)
    _set_arg(bt)
    bt.set_defaults(fn=cmd_batch)

    co = sub.add_parser("costs", help="summarize work/costs.jsonl")
    co.add_argument("--month", default=None, help="filter YYYY-MM, e.g. 2026-09")
    co.set_defaults(fn=cmd_costs)

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
