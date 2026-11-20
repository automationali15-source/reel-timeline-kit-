"""Offline scene timeline and subtitle exports."""
import csv
import json
import math
import re
from pathlib import Path

class ManifestError(ValueError):
    pass

def build_timeline(data, max_wpm=180):
    if not isinstance(data, dict):
        raise ManifestError("Manifest must be an object")
    fps = data.get("fps", 30)
    if type(fps) is not int or not 1 <= fps <= 240:
        raise ManifestError("fps must be an integer from 1 to 240")
    scenes = data.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        raise ManifestError("scenes must be a nonempty list")
    if type(max_wpm) is not int or max_wpm <= 0:
        raise ManifestError("max_wpm must be a positive integer")
    output = []
    warnings = []
    cursor = 0
    for i, scene in enumerate(scenes, 1):
        if not isinstance(scene, dict):
            raise ManifestError("Scene must be an object")
        duration = scene.get("duration")
        if type(duration) not in (int, float) or not math.isfinite(duration) or duration <= 0:
            raise ManifestError("Scene duration must be finite and positive")
        frames = round(duration * fps)
        if frames == 0:
            raise ManifestError("Scene must have at least one frame")
        name = scene.get("name", f"Scene {i}")
        voiceover = scene.get("voiceover", "")
        visual = scene.get("visual", "")
        sfx = scene.get("sfx", [])
        if not all(isinstance(x, str) for x in (name, voiceover, visual)) or not isinstance(sfx, list) or not all(isinstance(x, str) for x in sfx):
            raise ManifestError("Scene text must be strings and sfx must be a string list")
        words = len(re.findall(r"\b[\w'-]+\b", voiceover))
        wpm = words * 60 * fps / frames
        if wpm > max_wpm:
            warnings.append(f"Scene {i}: about {wpm:.0f} WPM (limit {max_wpm})")
        output.append({"index": i, "name": name, "start_frame": cursor, "end_frame": cursor+frames, "duration_frames": frames, "start_seconds": cursor/fps, "end_seconds": (cursor+frames)/fps, "visual": visual, "voiceover": voiceover, "sfx": sfx, "wpm": round(wpm,1)})
        cursor += frames
    return {"project": data.get("project", "Untitled"), "fps": fps, "total_frames": cursor, "total_seconds": cursor/fps, "scenes": output, "warnings": warnings}

def srt_time(seconds):
    milliseconds = round(seconds*1000)
    hours, rem = divmod(milliseconds, 3600000)
    minutes, rem = divmod(rem, 60000)
    seconds, ms = divmod(rem, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{ms:03}"

def export_timeline(timeline, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    with (output/"timeline.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(timeline["scenes"][0].keys()))
        writer.writeheader()
        for scene in timeline["scenes"]:
            writer.writerow({**scene,"sfx":" | ".join(scene["sfx"])})
    cues = []
    for scene in timeline["scenes"]:
        if scene["voiceover"].strip():
            cues.append(f'{len(cues)+1}\n{srt_time(scene["start_seconds"])} --> {srt_time(scene["end_seconds"])}\n{scene["voiceover"]}')
    (output/"captions.srt").write_text("\n\n".join(cues)+("\n" if cues else ""),encoding="utf-8")
    prompts = [f'# {timeline["project"]}']
    for scene in timeline["scenes"]:
        prompts.append(f'\nScene {scene["index"]}: {scene["name"]}\nTime: {scene["start_seconds"]:.3f}-{scene["end_seconds"]:.3f}s\nVisual: {scene["visual"]}\nVoiceover: {scene["voiceover"]}\nSFX: {", ".join(scene["sfx"])}')
    (output/"shot_prompts.txt").write_text("\n".join(prompts)+"\n", encoding="utf-8")
    (output/"summary.json").write_text(json.dumps({k:v for k,v in timeline.items() if k!="scenes"},indent=2)+"\n",encoding="utf-8")
