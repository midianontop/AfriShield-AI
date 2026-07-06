from retriever import search_documents

results = search_documents(
    "Who is Midian?"
)

for i, result in enumerate(results, start=1):
    print(f"\nResult {i}")
    print("-" * 50)
    print(result)