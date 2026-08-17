#!/usr/bin/env python3
"""Verifica um corte renderizado: drift de duracao e "ghost speech" na borda.

"Ghost speech" = uma palavra da transcricao ORIGINAL que atravessa a borda entre
um segmento 'cut' e um 'keep' vizinho -- ela vai sair cortada no meio no video
renderizado.

Uso:
    python verify_cut.py cuts.json transcript.json master.mp4
"""
import argparse
import json
import subprocess
import sys


def get_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        capture_output=True,
        text=True,
    ).stdout.strip()
    return float(out)


def check_duration(edl, rendered_path, tolerance_per_cut=0.08):
    segments = [s for s in edl["segments"] if s["action"] == "keep"]
    expected = sum(s["end"] - s["start"] for s in segments)
    actual = get_duration(rendered_path)
    tolerance = tolerance_per_cut * max(1, len(segments))
    drift = abs(actual - expected)
    return drift <= tolerance, expected, actual, drift, tolerance


def check_ghost_speech(edl, words, margin=0.06):
    boundaries = []
    segs = sorted(edl["segments"], key=lambda s: s["start"])
    for i in range(len(segs) - 1):
        a, b = segs[i], segs[i + 1]
        if a["action"] != b["action"]:
            boundaries.append(a["end"])  # == b["start"]

    problems = []
    for b in boundaries:
        for w in words:
            if w["start"] < b - margin and w["end"] > b + margin:
                problems.append({"boundary": b, "word": w["word"], "start": w["start"], "end": w["end"]})
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cuts_json")
    ap.add_argument("transcript_json", help="a transcricao ORIGINAL (pre-corte), nao a remapeada")
    ap.add_argument("rendered")
    args = ap.parse_args()

    with open(args.cuts_json, encoding="utf-8") as f:
        edl = json.load(f)
    with open(args.transcript_json, encoding="utf-8") as f:
        words = json.load(f)["words"]

    ok, expected, actual, drift, tol = check_duration(edl, args.rendered)
    ghosts = check_ghost_speech(edl, words)

    print(f"duracao esperada: {expected:.2f}s | renderizada: {actual:.2f}s | drift: {drift:.2f}s (tolerancia {tol:.2f}s)")
    print("OK" if ok else "FALHOU: drift de duracao acima da tolerancia")

    if ghosts:
        print(f"\n{len(ghosts)} palavra(s) cortada(s) em cima de uma borda de corte (ghost speech):")
        for g in ghosts:
            print(f"  '{g['word']}' ({g['start']:.2f}-{g['end']:.2f}s) atravessa o corte em {g['boundary']:.2f}s")
    else:
        print("\nnenhuma palavra cortada em cima de uma borda -- OK")

    sys.exit(0 if ok and not ghosts else 1)


if __name__ == "__main__":
    main()
