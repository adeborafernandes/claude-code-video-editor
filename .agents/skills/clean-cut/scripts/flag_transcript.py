#!/usr/bin/env python3
"""Sinaliza palavras "estranhas" na transcricao para revisao humana ANTES de gerar
legenda -- o Whisper as vezes erra termo tecnico ou nome proprio (ex: "pre sales
engineer" saindo garbled) e isso so aparece queimado na legenda se ninguem checar
antes. Rodar depois de cut.py (em cima de edited-transcript.json), antes de
/embedded-captions.

Usa a confianca por palavra que o proprio Whisper ja calcula (campo 'probability',
capturado por transcribe.py) -- palavra abaixo do limiar e sinalizada. Sem esse
campo (transcricao antiga ou backend sem probabilidade), cai para uma heuristica de
forma da palavra (maiuscula isolada fora de sigla conhecida, caractere incomum,
token de 1 letra que nao e artigo/preposicao comum).

Uso:
    python flag_transcript.py work/edited-transcript.json -o work/caption-review.md

O relatorio nao corrige nada sozinho -- e uma lista para o humano conferir contra o
audio. Se uma palavra estiver errada, corrija o campo "word" no proprio arquivo de
transcricao no indice indicado, e so entao gere a legenda.
"""
import argparse
import json
import re
import sys

KNOWN_ACRONYMS = {
    "IA", "API", "MCP", "RAG", "LGPD", "MVP", "PM", "CTA", "SEO", "ROI",
    "UX", "UI", "CEO", "CTO", "SaaS", "BaaS", "AI", "EU",
}


def looks_odd(word):
    """Heuristica de forma, usada so quando nao ha 'probability' disponivel."""
    w = word.strip()
    if not w:
        return False
    if re.search(r"[^\w\sÀ-ÿ'-]", w):
        return True
    if w.isupper() and len(w) > 1 and w not in KNOWN_ACRONYMS:
        return True
    if len(w) == 1 and w.lower() not in {"a", "e", "o", "i", "u", "é", "à"}:
        return True
    return False


def flag_words(words, threshold=0.55, context=3):
    flags = []
    for i, w in enumerate(words):
        prob = w.get("probability")
        suspicious, reason = False, ""
        if prob is not None:
            if prob < threshold:
                suspicious, reason = True, f"confiança baixa ({prob})"
        elif looks_odd(w["word"]):
            suspicious, reason = True, "forma incomum (sem confiança disponível na transcrição)"

        if suspicious:
            lo, hi = max(0, i - context), min(len(words), i + context + 1)
            ctx = " ".join(x["word"] for x in words[lo:hi])
            flags.append(
                {"index": i, "word": w["word"], "start": w["start"], "reason": reason, "context": ctx}
            )
    return flags


def format_report(words, flags):
    lines = [f"# Revisão de legenda — {len(flags)} palavra(s) suspeita(s) de {len(words)} no total", ""]
    if not flags:
        lines.append("Nenhuma palavra abaixo do limiar de confiança. Pode seguir para /embedded-captions.")
        return "\n".join(lines)

    lines.append(
        "Confira cada uma contra o áudio antes de gerar a legenda final. Se estiver errada, "
        "corrija o campo `word` no arquivo de transcrição no índice indicado e rode de novo."
    )
    lines.append("")
    for f in flags:
        m, s = divmod(f["start"], 60)
        ts = f"{int(m)}:{s:05.2f}"
        lines.append(f"- **[{f['index']}] \"{f['word']}\"** em {ts} — {f['reason']}")
        lines.append(f"  contexto: …{f['context']}…")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("transcript")
    ap.add_argument("-o", "--output", default=None, help="markdown de revisão; se omitido, imprime no terminal")
    ap.add_argument("--threshold", type=float, default=0.55, help="abaixo disso, a palavra é sinalizada")
    ap.add_argument("--context", type=int, default=3, help="quantas palavras de contexto para cada lado")
    args = ap.parse_args()

    with open(args.transcript, encoding="utf-8") as f:
        words = json.load(f)["words"]

    flags = flag_words(words, args.threshold, args.context)
    report = format_report(words, flags)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"{args.output}: {len(flags)} palavra(s) suspeita(s) de {len(words)}")
    else:
        print(report)

    return 1 if flags else 0


if __name__ == "__main__":
    sys.exit(main())
