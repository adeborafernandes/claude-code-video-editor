#!/usr/bin/env python3
"""Gera um RASCUNHO de EDL (cuts.json) a partir da transcricao + deteccao de silencio.

Agrupa palavras em "linhas" (por pontuacao ou pausa > --line-gap), encontra linhas
repetidas (a mesma frase dita de novo) e marca todas menos a ULTIMA como "cut"
(motivo: superseded -- a mesma regra do relato da XDA: a ultima repeticao e a boa),
marca silencios/pausas longas como "cut", e preenche o resto como "keep".

O resultado e um RASCUNHO para revisao humana -- nunca rode cut.py direto em cima
dele sem olhar antes.

Uso:
    python detect_takes.py transcript.json video.mp4 -o cuts.json
"""
import argparse
import difflib
import json
import re
import subprocess


def normalize(text):
    return re.sub(r"[^\w\s]", "", text.lower()).strip()


def group_lines(words, line_gap=1.2):
    lines, cur = [], []
    for w in words:
        if cur and (
            w["start"] - cur[-1]["end"] > line_gap
            or cur[-1]["word"].strip().endswith((".", "?", "!"))
        ):
            lines.append(cur)
            cur = []
        cur.append(w)
    if cur:
        lines.append(cur)
    return [
        {"start": line[0]["start"], "end": line[-1]["end"], "text": " ".join(w["word"] for w in line)}
        for line in lines
    ]


def find_retakes(lines, threshold=0.72, lookback=6):
    """Marca linhas anteriores similares a uma linha posterior como supersedidas."""
    cut_ranges = []
    for i, line in enumerate(lines):
        norm_i = normalize(line["text"])
        if len(norm_i) < 6:
            continue
        for j in range(max(0, i - lookback), i):
            norm_j = normalize(lines[j]["text"])
            if len(norm_j) < 6:
                continue
            ratio = difflib.SequenceMatcher(None, norm_i, norm_j).ratio()
            if ratio >= threshold:
                cut_ranges.append((lines[j]["start"], lines[j]["end"], round(ratio, 2), lines[j]["text"]))
    return cut_ranges


def detect_silences(path, noise_db=-35, min_dur=0.7):
    """Roda `ffmpeg silencedetect` e devolve [(start, end), ...] de silencio."""
    cmd = ["ffmpeg", "-i", path, "-af", f"silencedetect=noise={noise_db}dB:d={min_dur}", "-f", "null", "-"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    starts = [float(m) for m in re.findall(r"silence_start:\s*([\d.]+)", proc.stderr)]
    ends = [float(m) for m in re.findall(r"silence_end:\s*([\d.]+)", proc.stderr)]
    return list(zip(starts, ends))


def build_segments(duration, cut_ranges, silences):
    cuts = [{"start": s, "end": e, "reason": f"superseded (sim={r})"} for s, e, r, _ in cut_ranges]
    cuts += [{"start": s, "end": e, "reason": "silence/pause"} for s, e in silences]
    cuts.sort(key=lambda c: c["start"])

    merged = []
    for c in cuts:
        if merged and c["start"] <= merged[-1]["end"] + 0.05:
            merged[-1]["end"] = max(merged[-1]["end"], c["end"])
            merged[-1]["reason"] += f" + {c['reason']}"
        else:
            merged.append(dict(c))

    segments, cursor = [], 0.0
    for c in merged:
        if c["start"] > cursor:
            segments.append({"start": cursor, "end": c["start"], "action": "keep", "reason": ""})
        segments.append({"start": c["start"], "end": c["end"], "action": "cut", "reason": c["reason"]})
        cursor = c["end"]
    if cursor < duration:
        segments.append({"start": cursor, "end": duration, "action": "keep", "reason": ""})
    return [s for s in segments if s["end"] - s["start"] > 0.02]


def get_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        capture_output=True,
        text=True,
    ).stdout.strip()
    return float(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("transcript")
    ap.add_argument("source_video")
    ap.add_argument("-o", "--output", default="cuts.json")
    ap.add_argument("--line-gap", type=float, default=1.2)
    ap.add_argument("--similarity", type=float, default=0.72)
    ap.add_argument("--noise-db", type=float, default=-35)
    ap.add_argument("--min-silence", type=float, default=0.7)
    args = ap.parse_args()

    with open(args.transcript, encoding="utf-8") as f:
        words = json.load(f)["words"]

    lines = group_lines(words, args.line_gap)
    retakes = find_retakes(lines, args.similarity)
    silences = detect_silences(args.source_video, args.noise_db, args.min_silence)
    duration = get_duration(args.source_video)
    segments = build_segments(duration, retakes, silences)

    edl = {"source": args.source_video, "duration": duration, "segments": segments}
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(edl, f, ensure_ascii=False, indent=2)

    kept = sum(s["end"] - s["start"] for s in segments if s["action"] == "keep")
    print(f"{args.output}: {len(segments)} segmentos, {kept:.1f}s mantidos de {duration:.1f}s brutos")
    print("REVISE este arquivo antes de rodar cut.py -- e um rascunho, nao a decisao final.")


if __name__ == "__main__":
    main()
