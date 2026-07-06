from retriever import search_documents

while True:

    question = input("\nAsk a question (or type exit): ")

    if question.lower() == "exit":
        break

    results = search_documents(question)

    print("\nTop Retrieved Chunks:")
    print("=" * 60)

    for i, chunk in enumerate(results, start=1):
        print(f"\nChunk {i}")
        print("-" * 40)
        print(chunk[:500])