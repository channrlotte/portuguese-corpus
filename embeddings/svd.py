import os
import glob
import json
import pickle
import numpy as np

from tqdm import tqdm
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse.linalg import svds


def make_matrix(directory_name: str, min_df: int):
    documents = []
    for file_name in tqdm(
        glob.glob(os.path.join(directory_name, "*.txt")), "Loading corpus"
    ):
        file_content = []
        with open(file_name, "rt", encoding="utf-8") as inp:
            for line in json.load(inp):
                file_content.extend(line)
        documents.append(" ".join(file_content))

    vectorizer = TfidfVectorizer(analyzer="word", min_df=min_df)
    data_vectorized = vectorizer.fit_transform(documents)

    return (
        data_vectorized,
        vectorizer.get_feature_names_out(),
    )


def apply_svd(W, dimension: int):
    u, sigma, vt = svds(W, dimension)

    descending_order_of_inds = np.flip(np.argsort(sigma))
    u = u[:, descending_order_of_inds]
    vt = vt[descending_order_of_inds]
    sigma = sigma[descending_order_of_inds]

    assert sigma.shape == (dimension,)
    assert vt.shape == (dimension, W.shape[1])
    assert u.shape == (W.shape[0], dimension)

    return np.dot(np.diag(sigma), vt).T


def main():
    W, words = make_matrix("data/texts_preprocessed", 7)
    vv = apply_svd(W, 100)

    dictionary = {word: vector for word, vector in zip(words, vv)}
    print(f"Number of words: {len(dictionary)}")

    with open("data/models/dictionary_svd.pkl", "wb") as out:
        pickle.dump(
            {word: [float(x) for x in vector] for word, vector in dictionary.items()},
            out,
        )


if __name__ == "__main__":
    main()
