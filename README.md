# portuguese-corpus

## CBOW
```bash
python3.9 embeddings/cbow.py
```

## SVD
```bash
python3.9 embeddings/svd.py
```

## Структура репозитория:

- data
  - models
    - cbow.bin — модель word2vec, обученная в режиме CBOW
    - dictionary_cbow.pkl — словарь, ключами которого являются леммы, а значениями — их эмбеддинги, полученные с помощью CBOW
    - dictionary_svd.pkl — словарь, ключами которого являются леммы, а значениями — их эмбеддинги, полученные с помощью SVD
  - texts_preprocessed — токенизированные и лемматизированные тексты, разбитые на отрывки идущих подряд слов
  - texts_raw — литературные тексты на португальском языке с сайта [libgen.is](https://libgen.is/)
- downloading
  - authors.json — словарь, ключами которого являются имена всех авторов, а значениями — 1, если автор португальский или бразильский, и 0, если нет
  - books.json — список книг на португальском языке
  - chatgpt.py — обработка запросов к ChatGPT (модель от OpenAI) через API
  - download_books.py — скачивание книг на португальском языке
  - free_proxy.json — список бесплатных прокси
- embeddings
  - cbow.py — получение эмбеддингов с помощью CBOW
  - svd.py — получение эмбеддингов с помощью SVD
  - test.py — сравнение ближайших слов к данному, полученных с помощью CBOW и SVD
- preprocessing
  - preprocessing.py — токенизация и лемматизация текстов
- .gitignore
- requirements.txt
