"""CLI entry point."""
import argparse
import json
import sys
from pathlib import Path
from .core import ManifestError, build_timeline, export_timeline

def main(argv=None):
    parser = argparse.ArgumentParser(description="Short-video timeline, SRT, and prompts")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--out", type=Path, default=Path("exports"))
    parser.add_argument("--max-wpm", type=int, default=180)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
        timeline = build_timeline(data, args.max_wpm)
        export_timeline(timeline, args.out)
    except (OSError, ValueError, ManifestError) as exc:
        print(f"Error: {exc}",file=sys.stderr)
        return 1
    print(f'{timeline["total_seconds"]:.3f}s, {timeline["total_frames"]} frames, {len(timeline["scenes"])} scenes')
    for warning in timeline["warnings"]:
        print("WARNING: "+warning,file=sys.stderr)
    return 2 if args.strict and timeline["warnings"] else 0

if __name__ == "__main__":
    raise SystemExit(main())
