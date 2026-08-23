from translations import get_translator

translator = get_translator('languages')
examples = [
    'an yi min zamba',
    'AN YI MIN ZAMBA!!',
    'Na karbi sakon whatsapp na bogi',
    'asusun bankina an hacke',
]
for text in examples:
    print(f"{text} -> {translator.translate(text, 'hausa')}")
