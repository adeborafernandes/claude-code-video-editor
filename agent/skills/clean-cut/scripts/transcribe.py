#!/usr/bin/env python3
"""Transcreve um audio/video com timestamp por palavra (Whisper local).

Uso:
    python transcribe.py <video.mp4> [--model small] [--lang pt] -o transcript.json

Requer, na maquina onde o video existe (nao neste container):
  - ffmpeg no PATH
  - `pip install openai-whisper` OU `pip install faster-whisper`
"""
import argparse
import json
import sys


def transcribe_openai_whisper(path, model_name, lang):
    import whisper

    model = whisper.load_model(model_name)
    result = model.transcribe(path, language=lang, word_timestamps=True, verbose=False)
    words = []
    for segment in result["segments"]:
        for w in segment.get("words", []):
            words.append(
                {
                    "word": w["word"].strip(),
                    "start": round(w["start"], 3),
                    "end": round(w["end"], 3),
                    "probability": round(w["probability"], 3) if "probability" in w else None,
                }
            )
    return words


def transcribe_faster_whisper(path, model_name, lang):
    from faster_whisper import WhisperModel

    model = WhisperModel(model_name)
    segments, _ = model.transcribe(path, language=lang, word_timestamps=True)
    words = []
    for segment in segments:
        for w in segment.words or []:
            words.append(
                {
                    "word": w.word.strip(),
                    "start": round(w.start, 3),
                    "end": round(w.end, 3),
                    "probability": round(w.probability, 3) if w.probability is not None else None,
                }
            )
    return words


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source")
    ap.add_argument("--model", default="small", help="tiny/base/small/medium/large")
    ap.add_argument("--lang", default=None, help="ex: pt, en. Omitir para autodetectar.")
    ap.add_argument("-o", "--output", default=None)
    args = ap.parse_args()

    try:
        words = transcribe_openai_whisper(args.source, args.model, args.lang)
    except ImportError:
        try:
            words = transcribe_faster_whisper(args.source, args.model, args.lang)
        except ImportError:
            sys.exit(
                "Nenhum backend de transcricao encontrado. Instale um:\n"
                "  pip install openai-whisper\n"
                "  pip install faster-whisper"
            )

    out = {"source": args.source, "words": words}
    text = json.dumps(out, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"transcricao salva em {args.output} ({len(words)} palavras)")
    else:
        print(text)


if __name__ == "__main__":
    main()
