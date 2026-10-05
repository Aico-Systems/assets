# FLEURS speech samples

Read speech with exact reference transcripts, for testing what the glove's microphone path
(and any other capture path) makes of real voices, per language.

- 6 clips per language, 5–13 s each, from the FLEURS **test** split: `de_de`, `en_us`,
  `fr_fr`, `es_419`, `pl_pl`, `tr_tr`.
- 16 kHz, mono, 16-bit PCM WAV, loudness-normalized to -20 LUFS (FLEURS ships 32-bit float
  at levels from normal speech down to a -44 dBFS peak).
- `manifest.json`: per clip the file, language, duration, the raw transcript (`text`, as
  read) and FLEURS' normalized one (`normalized`: lower case, no punctuation -- compare
  against this for a word error rate), speaker gender and the FLEURS id.
- `fetch.py` regenerates or extends the set (`--langs de_de,it_it --per-lang 10`); it
  streams only the start of each language's archive.

Source: [google/fleurs](https://huggingface.co/datasets/google/fleurs), Conneau et al.,
"FLEURS: Few-shot Learning Evaluation of Universal Representations of Speech" (2022).
Licensed CC BY 4.0 -- keep this attribution with the files.
