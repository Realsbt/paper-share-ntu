#!/usr/bin/env python3
"""Build local narrated videos from physical PDF pages and ordered JSON notes."""
import argparse
import json
import math
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


def tool(name, env):
    value = os.environ.get(env, name)
    found = shutil.which(value)
    if not found and env not in os.environ and name in {"ffmpeg", "ffprobe"}:
        found = shutil.which("static_" + name)
    if not found:
        raise ValueError(f"Missing tool: {value}; install {name} or set {env}.")
    return found


def run(command, cwd=None, timeout=600):
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True,
                            timeout=timeout, env={**os.environ, "LC_ALL": "C"})
    if result.returncode:
        raise ValueError(f"{Path(command[0]).name} failed: {result.stderr[-2000:]}")
    return result.stdout


def read_notes(pdf, notes_path):
    if not pdf.is_file() or not pdf.stat().st_size:
        raise ValueError(f"Missing or empty PDF: {pdf}")
    info = run([tool("pdfinfo", "PDFINFO"), str(pdf)])
    match = re.search(r"^Pages:\s+(\d+)\s*$", info, re.MULTILINE)
    if not match:
        raise ValueError("Cannot determine PDF physical page count.")
    count = int(match.group(1))
    notes = json.loads(notes_path.read_text(encoding="utf-8"))
    if not isinstance(notes, list) or len(notes) != count or count < 1:
        raise ValueError(f"Narration must contain exactly {count} entries, one per PDF page.")
    for page, entry in enumerate(notes, 1):
        if not isinstance(entry, dict) or type(entry.get("page")) is not int or entry["page"] != page:
            raise ValueError(f"Expected page {page} in position {page}.")
        if not isinstance(entry.get("text"), str) or not entry["text"].strip():
            raise ValueError(f"Empty narration for page {page}.")
    return notes


def probe(path, executable):
    result = json.loads(run([executable, "-v", "error", "-show_entries",
                            "format=duration:stream=codec_type", "-of", "json", str(path)]))
    duration = float(result.get("format", {}).get("duration", 0))
    streams = {s.get("codec_type") for s in result.get("streams", [])}
    if not math.isfinite(duration) or duration <= 0 or "audio" not in streams:
        raise ValueError(f"Invalid or empty audio: {path}")
    return duration, streams


def audio_paths(notes, base):
    paths = []
    for entry in notes:
        name = entry.get("audio")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"Missing audio for page {entry['page']}.")
        path = (base / name).resolve()
        if not path.is_file() or not path.stat().st_size:
            raise ValueError(f"Missing or empty recording: {path}")
        paths.append(path)
    return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("notes", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--engine", choices=["edge", "audio"], default="edge")
    parser.add_argument("--voice", default="zh-CN-XiaoxiaoNeural")
    parser.add_argument("--rate", default="+0%")
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    try:
        pdf, notes_file = args.pdf.resolve(), args.notes.resolve()
        notes = read_notes(pdf, notes_file)
        recordings = audio_paths(notes, notes_file.parent) if args.engine == "audio" else []
        if args.check:
            print(json.dumps({"pages": len(notes), "narrations": len(notes),
                              "input_check": "passed", "media_not_generated": True}))
            return 0
        if args.output is None or args.output.suffix.lower() != ".mp4":
            raise ValueError("Specify --output ending in .mp4.")
        if args.height < 240 or args.height > 2160 or args.height % 2:
            raise ValueError("--height must be an even integer from 240 to 2160.")
        output = args.output.resolve()
        if output in {pdf, notes_file, *recordings}:
            raise ValueError("Output must not replace an input file.")
        if output.exists() and not args.overwrite:
            raise ValueError(f"Output exists; preserved: {output}. Use --overwrite to replace.")
        ffmpeg, ffprobe = tool("ffmpeg", "FFMPEG"), tool("ffprobe", "FFPROBE")
        renderer = tool("pdftoppm", "PDFTOPPM")
        tts = tool("edge-tts", "EDGE_TTS_BIN") if args.engine == "edge" else None
        if recordings:
            for recording in recordings:
                probe(recording, ffprobe)
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".paper-video-", dir=output.parent) as tmp:
            work = Path(tmp)
            for index, entry in enumerate(notes, 1):
                stem = f"page-{index:04d}"
                run([renderer, "-f", str(index), "-l", str(index), "-singlefile",
                     "-scale-to-y", str(args.height), "-scale-to-x", "-1",
                     "-png", str(pdf), str(work / stem)])
                if tts:
                    text_file = work / f"{stem}.txt"
                    text_file.write_text(entry["text"], encoding="utf-8")
                    audio = work / f"{stem}.mp3"
                    run([tts, "--voice", args.voice, f"--rate={args.rate}",
                         "--file", str(text_file), "--write-media", str(audio)], timeout=180)
                else:
                    audio = recordings[index - 1]
                duration, _ = probe(audio, ffprobe)
                run([ffmpeg, "-nostdin", "-y", "-v", "error", "-loop", "1", "-framerate", "25",
                     "-i", str(work / f"{stem}.png"), "-i", str(audio),
                     "-map", "0:v:0", "-map", "1:a:0", "-vf",
                     f"scale=-2:{args.height},setsar=1", "-c:v", "libx264", "-tune", "stillimage",
                     "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "aac",
                     "-ar", "48000", "-ac", "2", "-t", str(duration),
                     str(work / f"{stem}.mp4")], timeout=3600)
                print(f"Page {index}/{len(notes)} complete", flush=True)
            concat = work / "concat.txt"
            concat.write_text("".join(f"file 'page-{i:04d}.mp4'\n"
                                      for i in range(1, len(notes) + 1)), encoding="utf-8")
            candidate = work / "presentation.mp4"
            run([ffmpeg, "-nostdin", "-y", "-v", "error", "-f", "concat", "-safe", "1",
                 "-i", str(concat), "-c", "copy", "-movflags", "+faststart", str(candidate)],
                timeout=3600)
            _, streams = probe(candidate, ffprobe)
            if "video" not in streams:
                raise ValueError("Final MP4 has no video stream.")
            if args.overwrite:
                os.replace(candidate, output)
            else:
                # Atomic no-clobber publication on the same filesystem.
                os.link(candidate, output)
        print(output)
        return 0
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        parser.exit(1, f"ERROR: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
