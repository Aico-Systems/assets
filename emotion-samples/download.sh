#!/usr/bin/env bash
# Curated CREMA-D subset for paralinguistic engine smoke tests.
#
# CREMA-D (Cao et al., 2014) — 7,442 clips, 91 actors, 6 emotions (angry,
# disgusted, fearful, happy, neutral, sad). Source:
#   https://github.com/CheyneyComputerScience/CREMA-D
#   ODbL 1.0 licence — attribution + share-alike on derived databases.
#
# We pull a tiny labelled subset (3 actors × 6 emotions × 2 sentences = 36
# clips, ~2 MB total) to drive `stt/test_emotion.py`. Files keep their
# upstream names so the ground-truth emotion is parseable from the path.
#
# Re-runnable + idempotent (curl with --create-dirs --continue-at -).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# CREMA-D stores WAVs through Git LFS — `raw.githubusercontent.com` returns
# only the LFS pointer text, not the audio. `media.githubusercontent.com/media`
# resolves the pointer and serves the actual binary blob.
RAW="https://media.githubusercontent.com/media/CheyneyComputerScience/CREMA-D/master/AudioWAV"

# Three actors (mix of genders), two carrier sentences, six emotions.
ACTORS=(1001 1002 1003)
SENTENCES=(DFA ITS)          # DFA: "Don't forget a jacket"; ITS: "I think I've seen this before"
EMOTIONS=(ANG DIS FEA HAP NEU SAD)

count_total=$(( ${#ACTORS[@]} * ${#SENTENCES[@]} * ${#EMOTIONS[@]} ))
count_ok=0
count_fail=0

echo "Downloading ${count_total} CREMA-D clips to ${HERE} ..."
for actor in "${ACTORS[@]}"; do
  for sentence in "${SENTENCES[@]}"; do
    for emotion in "${EMOTIONS[@]}"; do
      name="${actor}_${sentence}_${emotion}_XX.wav"
      out="${HERE}/${name}"
      if [ -f "${out}" ] && [ -s "${out}" ]; then
        count_ok=$(( count_ok + 1 ))
        continue
      fi
      if curl -fsSL --retry 3 --retry-delay 1 "${RAW}/${name}" -o "${out}"; then
        count_ok=$(( count_ok + 1 ))
      else
        rm -f "${out}"
        count_fail=$(( count_fail + 1 ))
        echo "  skip ${name} (404 or network)"
      fi
    done
  done
done

echo "Done. ${count_ok}/${count_total} files present, ${count_fail} missing."
