#!/usr/bin/env python3
"""Renderiza o corte mestre a partir de cuts.json e remapeia a transcricao.

Uso:
    python cut.py cuts.json transcript.json -o master.mp4 \
        --transcript-out edited-transcript.json
"""
import argparse
import json
import os
import shutil
import subprocess
import tempfile


def keep_segments(edl):
    segs = [s for s in edl["segments"] if s["action"] == "keep" and s["end"] > s["start"]]
    return sorted(segs, key=lambda s: s["start"])


def render(source, segments, output):
    """Corta cada segmento (re-encode, precisao de frame) e concatena."""
    tmpdir = tempfile.mkdtemp(prefix="clean-cut-")
    parts = []
    for i, seg in enumerate(segments):
        part = os.path.join(tmpdir, f"part_{i:04d}.mp4")
        dur = seg["end"] - seg["start"]
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-ss", str(seg["start"]), "-i", source, "-t", str(dur),
                "-c:v", "libx264", "-preset", "fast", "-crf", "18",
                "-c:a", "aac", "-avoid_negative_ts", "make_zero",
                part,
            ],
            check=True,
            capture_output=True,
        )
        parts.append(part)

    concat_list = os.path.join(tmpdir, "concat.txt")
    with open(concat_list, "w") as f:
        for p in parts:
            f.write(f"file '{p}'\n")

    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list, "-c", "copy", output],
        check=True,
        capture_output=True,
    )
    return tmpdir


def remap_transcript(words, segments):
    """Mantem so palavras totalmente dentro de um segmento 'keep' e desloca seus tempos.

    Preserva quaisquer outros campos da palavra original (ex: 'probability'), so
    substituindo 'start'/'end' pelo tempo remapeado.
    """
    out, offset = [], 0.0
    for seg in segments:
        for w in words:
            if w["start"] >= seg["start"] and w["end"] <= seg["end"]:
                out.append(
                    {
                        **w,
                        "start": round(w["start"] - seg["start"] + offset, 3),
                        "end": round(w["end"] - seg["start"] + offset, 3),
                    }
                )
        offset += seg["end"] - seg["start"]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cuts_json")
    ap.add_argument("transcript_json")
    ap.add_argument("-o", "--output", default="master.mp4")
    ap.add_argument("--transcript-out", default="edited-transcript.json")
    ap.add_argument("--keep-parts", action="store_true", help="nao apagar os arquivos temporarios por-segmento")
    args = ap.parse_args()

    with open(args.cuts_json, encoding="utf-8") as f:
        edl = json.load(f)
    with open(args.transcript_json, encoding="utf-8") as f:
        words = json.load(f)["words"]

    segments = keep_segments(edl)
    if not segments:
        raise SystemExit("cuts.json nao tem nenhum segmento 'keep'.")

    tmpdir = render(edl["source"], segments, args.output)
    edited_words = remap_transcript(words, segments)

    with open(args.transcript_out, "w", encoding="utf-8") as f:
        json.dump({"source": args.output, "words": edited_words}, f, ensure_ascii=False, indent=2)

    if not args.keep_parts:
        shutil.rmtree(tmpdir, ignore_errors=True)

    total = sum(s["end"] - s["start"] for s in segments)
    print(f"{args.output}: {len(segments)} segmentos, {total:.1f}s")
    print(f"{args.transcript_out}: {len(edited_words)} palavras remapeadas")
    print("Rode verify_cut.py antes de considerar este corte pronto.")


if __name__ == "__main__":
    main()
