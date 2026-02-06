# Algorithm Technical Documentation

## Similarity Detection Algorithms

### 1. TF-IDF + Cosine Similarity

**Term Frequency (TF):**
```
TF(t, d) = (Number of times term t appears in document d) / (Total terms in d)
```

**Cosine Similarity:**
```
sim(A, B) = (A · B) / (||A|| × ||B||)
```

Where:
- A · B = dot product of TF vectors
- ||A|| = Euclidean norm of vector A

### 2. N-gram Overlap

Character and word n-grams capture local text patterns:

```
Jaccard_ngram(A, B) = |ngrams(A) ∩ ngrams(B)| / |ngrams(A) ∪ ngrams(B)|
```

Default n=3 for optimal balance of precision and recall.

### 3. Combined Similarity Score

Weighted ensemble for robust detection:

```
Combined_Sim = 0.5 × Cosine + 0.3 × N-gram + 0.2 × Jaccard
```

Weights determined empirically to minimize false positives while maintaining sensitivity.

## Paraphrasing Methodology

### Rule-Based Transformations

1. **Synonym Replacement**
   - Dictionary-based word substitution
   - Preserves grammatical structure
   - Maintains semantic equivalence

2. **Syntactic Restructuring**
   - Active ↔ Passive voice conversion
   - Clause reordering
   - Conjunction substitution

3. **Style Adaptation**
   - Academic: Formal vocabulary, complex structures
   - Formal: Conservative expressions, complete sentences
   - Casual: Contractions, conversational tone

## Originality Scoring

```
Originality = (1 - flagged_segments / total_segments) × 100%
```

Threshold interpretation:
- ≥90%: Very high originality
- 75-89%: Good originality, minor review needed
- 50-74%: Moderate concerns, revision recommended
- <50%: Significant issues, extensive rewrite required

## Limitations

1. **Local Analysis Only**: Cannot detect external source plagiarism
2. **Language Support**: Optimized for English and CJK languages
3. **Context Blind**: No semantic understanding beyond surface patterns
4. **Threshold Dependency**: Results sensitive to threshold selection

## References

- Salton, G., & Buckley, C. (1988). Term-weighting approaches in automatic text retrieval
- Broder, A. Z. (1997). On the resemblance and containment of documents
- Manning, C. D., & Schütze, H. (1999). Foundations of Statistical Natural Language Processing
