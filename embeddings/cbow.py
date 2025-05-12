import os
import glob
import json
import pickle

from tqdm import tqdm
from gensim.models import Word2Vec


def load_corpus(directory_name: str):
    documents = []
    for file_name in tqdm(
        glob.glob(os.path.join(directory_name, "*.txt")), "Loading corpus"
    ):
        with open(file_name, "rt", encoding="utf-8") as inp:
            documents.extend(json.load(inp))

    return documents


def main():
    documents = load_corpus("data/texts_preprocessed")
    print("Building model...")
    model = Word2Vec(sentences=documents, vector_size=100, min_count=7)
    print("Saving model...")
    model.save("data/models/cbow.bin")

    dictionary = {
        word: [float(x) for x in model.wv[word]]
        for word in model.wv.key_to_index.keys()
    }
    print(f"Number of words: {len(dictionary)}")

    with open("data/models/dictionary_cbow.pkl", "wb") as out:
        pickle.dump(dictionary, out)


if __name__ == "__main__":
    main()
