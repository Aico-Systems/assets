"""Fetch a few FLEURS test utterances per language, with their reference transcripts.

FLEURS (google/fleurs, CC BY 4.0) is the same set of read Wikipedia sentences in 102
languages, recorded by native speakers at 16 kHz, each with a raw and a normalized
transcript. That makes it a clean ground truth for "does the glove's microphone path
transcribe correctly", per language.

Only the start of each language's test archive is streamed (gzip is sequential): the first
clips in the archive are kept, the rest is never downloaded.

    python fetch.py                       # defaults below
    python fetch.py --langs de_de,it_it --per-lang 10
"""

import argparse
import csv
import io
import json
import os
import subprocess
import tarfile
import urllib.request
import wave

BASE = "https://huggingface.co/datasets/google/fleurs/resolve/main/data"
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LANGS = "de_de,en_us,fr_fr,es_419,pl_pl,tr_tr"
LOUDNESS_LUFS = -20


def transcripts(lang):
    """file_name -> row, from the split's TSV (id, file, raw, normalized, phonemes, samples, gender)."""
    with urllib.request.urlopen(f"{BASE}/{lang}/test.tsv", timeout=60) as r:
        text = r.read().decode("utf-8")
    rows = {}
    for cols in csv.reader(io.StringIO(text), delimiter="\t", quoting=csv.QUOTE_NONE):
        if len(cols) >= 7:
            rows[cols[1]] = {"id": cols[0], "raw": cols[2], "normalized": cols[3],
                             "samples": int(cols[5]), "gender": cols[6]}
    return rows


def fetch(lang, per_lang, min_s, max_s):
    rows = transcripts(lang)
    out_dir = os.path.join(HERE, lang)
    os.makedirs(out_dir, exist_ok=True)
    kept = []
    with urllib.request.urlopen(f"{BASE}/{lang}/audio/test.tar.gz", timeout=60) as r:
        with tarfile.open(fileobj=r, mode="r|gz") as tar:
            for member in tar:
                name = os.path.basename(member.name)
                row = rows.get(name)
                if not member.isfile() or row is None:
                    continue
                seconds = row["samples"] / 16000
                if not (min_s <= seconds <= max_s):
                    continue
                source = tar.extractfile(member)
                if source is None:
                    continue
                # FLEURS ships 32-bit float WAV; 16-bit PCM plays everywhere (phones,
                # browsers, `adb shell` players) and is what STT front ends expect.
                # Loudness-normalized too: the recordings range from speech at a
                # normal level to a peak of -44 dBFS, and a test played through a
                # speaker should vary the path, not the recording.
                path = os.path.join(out_dir, name)
                subprocess.run(
                    ["ffmpeg", "-v", "error", "-y", "-i", "pipe:0",
                     "-af", f"loudnorm=I={LOUDNESS_LUFS}:TP=-2:LRA=11",
                     "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", path],
                    input=source.read(), check=True,
                )
                with wave.open(path) as w:
                    rate, channels = w.getframerate(), w.getnchannels()
                kept.append({
                    "file": f"{lang}/{name}",
                    "lang": lang,
                    "seconds": round(seconds, 2),
                    "sample_rate": rate,
                    "channels": channels,
                    "text": row["raw"],
                    "normalized": row["normalized"],
                    "speaker_gender": row["gender"],
                    "fleurs_id": row["id"],
                })
                if len(kept) >= per_lang:
                    break
    return kept


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--langs", default=DEFAULT_LANGS)
    ap.add_argument("--per-lang", type=int, default=6)
    ap.add_argument("--min-seconds", type=float, default=5.0)
    ap.add_argument("--max-seconds", type=float, default=14.0)
    a = ap.parse_args()
    manifest = []
    for lang in a.langs.split(","):
        clips = fetch(lang, a.per_lang, a.min_seconds, a.max_seconds)
        print(f"{lang}: {len(clips)} clips, {sum(c['seconds'] for c in clips):.0f} s")
        manifest += clips
    with open(os.path.join(HERE, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump({"source": "google/fleurs (test split)", "license": "CC BY 4.0",
                   "clips": manifest}, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
