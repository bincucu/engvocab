from flask import Flask, render_template, request, jsonify
from googletrans import Translator
from functools import lru_cache
import nltk
from nltk.corpus import wordnet
import unicodedata

app = Flask(__name__)

# Kiểm tra và tải dữ liệu WordNet chỉ một lần
try:
    wordnet.synsets("example")
except LookupError:
    nltk.download("wordnet")

@lru_cache(maxsize=128)
def get_wordnet_data(word):
    synsets = wordnet.synsets(word)
    if not synsets:
        return None, None

    meanings = ""
    examples = ""
    for synset in synsets:
        pos = synset.pos()  # Part of speech
        definition = synset.definition()
        meanings += f"- [{pos}] {definition}\n"
        for example in synset.examples():
            examples += f"- {example}\n"

    return meanings.strip(), examples.strip()

translator = Translator()

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def detect_language(word):
    try:
        detection = translator.detect(word)
        return detection.lang
    except Exception as e:
        return None

@app.route('/translate', methods=['GET'])
def translate():
    word = request.args.get('word')
    langpair = request.args.get('langpair')
    src, dest = langpair.split('-')

    normalized_word = remove_accents(word)
    detected_lang = detect_language(normalized_word)

    if detected_lang == 'en' and langpair == 'vi-en':
        return jsonify({'error': 'Please change mode'})
    if detected_lang == 'vi' and langpair == 'en-vi':
        return jsonify({'error': 'Please change mode'})

    try:
        translation = translator.translate(word, src=src, dest=dest).text

        # Điều kiện báo lỗi cho chế độ Anh-Việt nếu từ gốc và từ dịch giống hệt nhau
        if src == 'en' and word == translation:
            return jsonify({'error': 'The word remains the same after translation'})

        english_meanings, examples = get_wordnet_data(translation) if src == 'vi' else get_wordnet_data(word)

        if not english_meanings and not examples:
            return jsonify({
                'word': word,
                'definitions': 'Definition not found',
                'examples': 'Examples not found',
                'translation': translation
            })
        elif not english_meanings:
            return jsonify({
                'word': word,
                'definitions': 'Definition not found',
                'examples': examples if examples else 'Examples not found',
                'translation': translation
            })
        elif not examples:
            return jsonify({
                'word': word,
                'definitions': english_meanings,
                'examples': 'Examples not found',
                'translation': translation
            })
        else:
            return jsonify({
                'word': word,
                'definitions': english_meanings,
                'examples': examples,
                'translation': translation
            })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

