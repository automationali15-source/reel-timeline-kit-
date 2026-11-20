# Reel Timeline Kit 🎬

An original open-source, offline Python toolkit for **planning short videos**: frame-aligned scene timelines, rough subtitles (SRT), shot prompts, and estimated voiceover pacing.

**Status:** Early version 0.1.0. New project; no community adoption or usage statistics claimed.

## Requirements

Python 3.10 or newer. No paid API or runtime dependencies.

## Quick start

```bash
python -m pip install -e .
reel-timeline examples/baby-reel.json --out exports
python -m unittest discover -s tests -v
```

The included four-scene example is a 20-second, 30 FPS reel (600 frames).

## Generated files

- `timeline.csv` — ordered shots, timing, frame boundaries and voiceovers
- `captions.srt` — rough scene-level SRT draft (not word-level transcription)
- `shot_prompts.txt` — visual prompts, voiceover and sound-effect notes
- `summary.json` — project statistics and pacing warnings

## Input example

```json
{
  "project": "Short Demo",
  "fps": 30,
  "scenes": [
    {"name": "Hook", "duration": 2, "visual": "Close-up", "voiceover": "Watch this!", "sfx": ["pop"]},
    {"name": "Reveal", "duration": 6, "visual": "A surprising reveal", "voiceover": "Something unexpected happens.", "sfx": ["whoosh"]}
  ]
}
```

Scene durations are specified in seconds and rounded to whole frames. Voice pacing is an estimate based on spoken word count, not an analysis of audio files.

## CLI options

```bash
reel-timeline --help
reel-timeline examples/baby-reel.json --out exports --max-wpm 160
reel-timeline examples/baby-reel.json --strict
```

`--strict` returns exit code 2 on pacing warnings, while still writing the output files.

## Limitations

This tool **does not render videos**. It generates planning files only. Do not treat scene-based caption drafts as precisely synced audio transcripts.

## Contributing and security

See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md). Open reproducible issues, submit tested pull requests, and avoid sharing copyrighted media or private keys.

Licensed under the [MIT License](LICENSE). Created as a starting point for genuine ongoing open-source maintenance.
