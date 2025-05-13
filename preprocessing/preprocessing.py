import os
import json
import stanza

from tqdm import tqdm

INPUT_PATH = "data/texts_raw"
OUTPUT_PATH = "data/texts_preprocessed"

nlp = stanza.Pipeline(
    lang="pt",
    dir="stanza_resources",
    processors="tokenize,mwt,pos,lemma",
)

pos_dict = {"PROPN": "person1", "PRON": "pron1", "NUM": "ordinal1"}


def process(task):
    input_path, output_path = task

    try:
        with open(input_path, "rt", encoding="utf-8") as fin:
            content = fin.read()
        content = content.strip()

        while "\n\n" in content:
            content = content.replace("\n\n", "\n")
        while "  " in content:
            content = content.replace("  ", " ")

        tokens = []

        nlp_doc = nlp(content)
        for sentence in nlp_doc.sentences:
            for token in sentence.words:
                if token.lemma is None:
                    continue
                if token.upos in pos_dict:
                    tokens.append(pos_dict[token.upos])
                elif token.lemma.isdigit():
                    tokens.append("ordinal1")
                elif token.upos != "PUNCT":
                    tokens.append(token.lemma.lower())

        with open(output_path, "wt", encoding="utf-8") as out:
            json.dump(tokens, out, ensure_ascii=False)

    except Exception as ex:
        print(f"Something wrong with {input_path}")
        return False

    return True


def main():
    print("Initializing finished!", flush=True)
    tasks = []

    if not os.path.exists(INPUT_PATH):
        print(f"No such directory: {INPUT_PATH}")
        exit(-1)
    if not os.path.exists(OUTPUT_PATH):
        print(f"No such directory: {OUTPUT_PATH}")
        exit(-1)

    for file_name in sorted(
        os.listdir(INPUT_PATH),
        key=lambda file: os.path.getsize(os.path.join(INPUT_PATH, file)),
    ):
        input_path = os.path.join(INPUT_PATH, file_name)
        output_path = os.path.join(OUTPUT_PATH, file_name)
        if os.path.exists(output_path):
            continue
        tasks.append((input_path, output_path))

    print(f"Number of tasks: {len(tasks)}")

    for input_path, output_path in tqdm(tasks):
        process((input_path, output_path))


if __name__ == "__main__":
    main()
