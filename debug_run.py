from threat_detector import analyze_threat

r = analyze_threat('Someone withdrew ₦20000 from my account without permission')
print('CATEGORY:', r.category)
print('SEVERITY:', r.severity)
print('CONF:', r.confidence)
print('ENTITIES:', r.entities)
print('MATCHES:', r.matched_keywords)
