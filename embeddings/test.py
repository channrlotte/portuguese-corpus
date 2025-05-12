import pickle

import numpy as np

DICTIONARIES = ["cbow", "svd"]


def load_dictionary(file_name: str):
    with open(file_name, "rb") as inp:
        dictionary = pickle.load(inp)
    return {word: np.array(vector) for word, vector in dictionary.items()}


def find_similar_words(word, dictionary, top_n=5):
    if word not in dictionary:
        print(f"Слово '{word}' не найдено в словаре :(")
        return []

    return list(
        sorted(
            dictionary.keys(),
            key=lambda item: (
                np.linalg.norm(dictionary[item] - dictionary[word])
                if item != word
                else 0
            ),
        )
    )[:top_n]


def main():
    dictionaries = {
        name: load_dictionary(f"data/models/dictionary_{name}.pkl")
        for name in DICTIONARIES
    }
    while True:
        s = input("Enter word: ").lower().strip()
        for name in DICTIONARIES:
            words = find_similar_words(s, dictionaries[name], top_n=5)
            print(name, "->", "; ".join(words))


if __name__ == "__main__":
    main()
