"""Hybrid word/character TF-IDF with sentence-level reference evidence."""
import re
from datetime import datetime, timezone
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def sentences(text):
    return [part.strip() for part in re.findall(r'[^.!?\n]+[.!?]*', text) if part.strip()]


def hybrid(texts):
    normalized = [re.sub(r'\s+', ' ', text.lower()).strip() for text in texts]
    matrices = []
    for config in [dict(analyzer='word', ngram_range=(1, 2), token_pattern=r'(?u)\b\w+\b'),
                   dict(analyzer='char', ngram_range=(3, 5))]:
        try:
            vectors = TfidfVectorizer(**config).fit_transform(normalized)
            matrices.append(cosine_similarity(vectors))
        except ValueError as error:
            if 'empty vocabulary' not in str(error):
                raise
            import numpy as np
            matrices.append(np.zeros((len(texts), len(texts))))
    word, char = matrices
    return word, char, .65 * word + .35 * char


def analyze(document, references, threshold=.45):
    target = sentences(document)
    evidence = [(ref['name'], text) for ref in references for text in sentences(ref['text'])]
    if len(target) > 300 or len(evidence) > 1500:
        raise ValueError('Limit target to 300 sentences and references to 1,500 sentences.')
    word, char, scores = hybrid([document] + [r['text'] for r in references])
    sources = sorted([dict(name=r['name'], word=float(word[0, i+1]), char=float(char[0, i+1]),
                           score=float(min(1, max(0, scores[0, i+1]))))
                      for i, r in enumerate(references)], key=lambda r: -r['score'])
    passages = []
    if target:
        pw, pc, ps = hybrid(target + [text for _, text in evidence])
        for i, text in enumerate(target):
            best = max(range(len(evidence)), key=lambda j: ps[i, len(target)+j]) if evidence else None
            j = len(target) + best if best is not None else None
            score = float(min(1, max(0, ps[i, j]))) if j is not None else 0
            passages.append(dict(text=text, score=score, word=float(pw[i, j]) if j is not None else 0,
                                 char=float(pc[i, j]) if j is not None else 0,
                                 source=evidence[best][0] if best is not None else '',
                                 evidence=evidence[best][1] if best is not None else '', flagged=score >= threshold))
    similarity = sources[0]['score'] if sources else 0
    return dict(engine='Python / scikit-learn TF-IDF', createdAt=datetime.now(timezone.utc).isoformat(),
                threshold=threshold, similarity=similarity, complement=1-similarity,
                sources=sources, passages=passages,
                disclaimer='Similarity signals are not proof of plagiarism. Complement is not verified originality.')
