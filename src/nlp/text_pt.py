import re
import numpy as np
from collections import Counter
import pandas as pd

# Portuguese stopwords and dataset-specific terms are excluded from review text analysis.
STOPWORDS_PT = {
    "a", "ao", "aos", "as", "à", "às", "com", "como", "da", "das", "de", "do", "dos",
    "e", "ela", "elas", "ele", "eles", "em", "essa", "esse", "esta", "estas", "este",
    "estes", "estou", "está", "estão", "eu", "foi", "fui", "há", "isso", "isto", "já",
    "lhe", "mais", "mas", "me", "mesmo", "meu", "meus", "minha", "minhas", "muita",
    "muitas", "muito", "muitos", "na", "nas", "no", "nos", "num", "numa", "o", "os",
    "ou", "para", "pela", "pelo", "pelos", "por", "pra", "pro", "qual", "quando",
    "que", "se", "sem", "ser", "seu", "seus", "sua", "suas", "só", "também", "te",
    "tem", "ter", "teu", "tinha", "toda", "todas", "todo", "todos", "tudo", "um",
    "uma", "umas", "uns", "você", "vocês", "é", "era", "eram",
    "produto", "produtos", "compra", "comprei", "pedido", "item", "itens",
    "lannister",
}

def tokenize_pt(text: str) -> list[str]:
    """
    Extract lowercase tokens from a Portuguese review.

    Parameters
    ----------
    text : str
        Portuguese review text.

    Returns
    -------
    list of str
        Tokens of at least three characters, in their original order,
        excluding stopwords and dataset-specific terms.
    """    
    words = re.findall(r"[a-zà-ÿ]+", text.lower())
    return [w for w in words if w not in STOPWORDS_PT and len(w) > 2]


def distinctive_words(
    df: pd.DataFrame,
    text_col: str,
    group_col: str,
    group_a: str,
    group_b: str,
    n: int = 12,
    prior_weight: float = 1.0,
) -> dict:
    """
    Rank words by weighted log-odds z-scores using a prior based on pooled word counts.

    Parameters
    ----------
    df : pandas.DataFrame
        Review data containing the text and group columns.
    text_col : str
        Name of the column containing Portuguese review text.
    group_col : str
        Name of the column containing the group labels.
    group_a : str
        Label of the group favored by positive scores.
    group_b : str
        Label of the group favored by negative scores.
    n : int, default 12
        Maximum number of words to return per group.
    prior_weight : float, default 1.0
        How strongly overall word frequencies influence each group's scores.
    
    Returns
    -------
    dict
        Ranked (word, z_score) pairs for each group. 
        Descending for group_a and ascending for group_b.
    """
    counts = {}
    for group in (group_a, group_b):
        # Select reviews in this group that have text to tokenize.
        rows = df[df[group_col] == group].dropna(subset=[text_col])
        
        # Count every token occurrence, including repetitions within a review.
        tally = Counter()
        for text in rows[text_col]:
            tally.update(tokenize_pt(text))
        counts[group] = tally
    
    # Pool word counts to estimate the frequencies used for the prior.
    corpus = counts[group_a] + counts[group_b]
    corpus_total = sum(corpus.values())
    
    # Keep separate token totals to calculate word odds within each group.
    total_a, total_b = sum(counts[group_a].values()), sum(counts[group_b].values())

    # Maps each word to its signed log-odds z-score.
    scores = {}
    for word, corpus_count in corpus.items():
        # Allocate more of the prior to words that are common across both groups.
        prior = prior_weight * corpus_count / corpus_total
        count_a, count_b = counts[group_a][word], counts[group_b][word]

        # Compare each word's odds against all other words within the same group.
        odds_a = (count_a + prior) / (total_a + prior_weight - count_a - prior)
        odds_b = (count_b + prior) / (total_b + prior_weight - count_b - prior)
        delta = np.log(odds_a) - np.log(odds_b)

        # Rare words have higher uncertainty, so the same difference gets a smaller z-score.
        variance = 1 / (count_a + prior) + 1 / (count_b + prior)
        scores[word] = delta / np.sqrt(variance)
    
    # Lower scores favor group_b, and higher scores favor group_a.
    ranked = sorted(scores.items(), key=lambda kv: kv[1])
    return {group_b: ranked[:n], group_a: list(reversed(ranked[-n:]))}


def cluster_labels(
    df: pd.DataFrame,
    text_col: str,
    cluster_col: str,
    n: int = 7,
    min_count: int = 20,
) -> dict:
    """
    Label each cluster with words that are especially common within it.

    Parameters
    ----------
    df : pandas.DataFrame
        Review data containing the text and cluster columns.
    text_col : str
        Name of the column containing Portuguese review text.
    cluster_col : str
        Name of the column containing the cluster labels.
    n : int, default 7
        Maximum number of words to return per cluster.
    min_count : int, default 20
        Minimum times a word must appear across all clusters to be considered.

    Returns
    -------
    dict
        A list of words for each cluster, ordered from highest to lowest score.
    """
    # Count token occurrences within each cluster, skipping missing review text.
    tallies = {}
    for cluster, rows in df.groupby(cluster_col, observed=True):
        tally = Counter()
        for text in rows.dropna(subset=[text_col])[text_col]:
            tally.update(tokenize_pt(text))
        tallies[cluster] = tally

    # Pool the counts to estimate the overall frequency of each word across all clusters.
    corpus = Counter()
    for tally in tallies.values():
        corpus += tally
    corpus_total = sum(corpus.values())

    labels = {}
    for cluster, tally in tallies.items():
        cluster_total = sum(tally.values())
        scores = {}
        for word, count in tally.items():
            if corpus[word] < min_count:
                continue
            
            # Calculate the word's share of tokens inside and outside this cluster.
            rate_in = count / cluster_total
            rate_out = (corpus[word] - count) / (corpus_total - cluster_total)
            
            # A positive log ratio means the word is more common inside the cluster.
            # The small offset handles zero rates. The count weight gives more
            # influence to differences supported by repeated occurrences.
            log_ratio = np.log((rate_in + 1e-9) / (rate_out + 1e-9))
            scores[word] = log_ratio * np.sqrt(count)
        labels[cluster] = [w for w, _ in sorted(scores.items(), key=lambda kv: -kv[1])[:n]]

    return labels


def top_words_by_group(
    df: pd.DataFrame,
    text_col: str,
    group_col: str,
    n: int = 15,
    min_n: int = 200,
) -> dict:
    """
    Find the most frequent words in each group of reviews.

    Parameters
    ----------
    df : pandas.DataFrame
        Review data containing the text and group columns.
    text_col : str
        Name of the column containing Portuguese review text.
    group_col : str
        Name of the column containing the group labels.
    n : int, default 15
        Maximum number of words to return per group.
    min_n : int, default 200
        Minimum number of rows with nonmissing review text required per group.

    Returns
    -------
    dict
        A list of (word, count) pairs for each qualifying group 
        in descending order of frequency.
    """
    results = {}

    # Drop missing text before checking whether each group meets the row minimum.
    for group, rows in df.dropna(subset=[text_col]).groupby(group_col, observed=True):
        if len(rows) < min_n:
            continue
        
        # Count every occurrence, including repeated words within the same review.
        counts = Counter()
        for text in rows[text_col]:
            counts.update(tokenize_pt(text))
        results[group] = counts.most_common(n)

    return results