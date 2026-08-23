import pathlib, json
root = pathlib.Path(r'C:/Users/pc/cyber-rag/languages')
for p in sorted(root.glob('*.json')):
    text = p.read_text(encoding='utf-8')
    data = json.loads(text)
    print(f"{p.name}: lines={text.count(chr(10))+1}, phrases={len(data.get('phrases', {}))}")
