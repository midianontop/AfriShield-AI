# AfriShield AI Benchmark Results

## Test Environment

| Component | Specification |
|------------|--------------|
| Operating System | Windows |
| CPU | Intel Core i5-7200U @ 2.50GHz |
| RAM | 8 GB |
| AI Model | Llama 3.2 3B |
| Runtime | Ollama |
| Interface | Streamlit |
| Vector Database | ChromaDB |

---

## Performance Results

| Metric | Result |
|----------|----------|
| Startup Time | 38.7 seconds |
| Average AI Response Time | 72.2 seconds |
| Offline Operation | Supported |
| Internet Required | No |
| Local Processing | Yes |
| Cloud API Dependency | None |

---

## Memory Usage

Python Process Statistics:

| Metric | Value |
|----------|----------|
| Working Set Memory | ~467 MB |
| Private Memory | ~856 MB |
| CPU Time During Test | 27.84 seconds |

---

## Functional Testing

| Component | Status |
|------------|----------|
| Offline AI Assistant | Passed |
| RAG Retrieval System | Passed |
| Threat Detection | Passed |
| Scam Detection | Passed |
| Incident Response Assistant | Passed |
| Streamlit Dashboard | Passed |

---

## Observations

AfriShield AI successfully operated in a fully offline environment using a local Llama 3.2 model and ChromaDB-based Retrieval-Augmented Generation (RAG).

The system was tested on an 8 GB RAM machine and demonstrated the ability to provide cybersecurity assistance without requiring cloud services or internet connectivity.

The primary performance bottleneck is LLM inference speed on low-resource hardware. Future optimization efforts may include:

- Quantized models
- Faster embedding models
- Retrieval optimization
- Response caching
- Hardware acceleration

---

## Conclusion

The benchmark results demonstrate that AfriShield AI can provide practical cybersecurity intelligence on affordable hardware while maintaining complete offline functionality.

This makes the platform suitable for educational institutions, small businesses, cybersecurity learners, and communities operating in low-connectivity environments.