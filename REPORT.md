\# AfriShield AI

\## Technical Project Report



\### Africa Deep Tech Challenge 2026



\---



\# 1. Project Overview



\## Project Name



\*\*AfriShield AI - Offline AI Cybersecurity Assistant for Africa\*\*



\## Project Description



AfriShield AI is an offline artificial intelligence cybersecurity assistant designed to provide accessible cybersecurity intelligence for individuals, organizations, and small businesses.



The system combines:



\- Local Large Language Models (LLMs)

\- Retrieval-Augmented Generation (RAG)

\- Cybersecurity knowledge bases

\- Threat detection algorithms

\- Scam detection systems

\- Incident response assistance



The objective is to provide cybersecurity support without depending on internet connectivity or cloud-based AI services.



\---



\# 2. Problem Statement



Cybersecurity threats continue to increase across Africa as digital adoption grows.



Major challenges include:



\- Phishing attacks

\- Online financial scams

\- Identity theft

\- Social engineering attacks

\- Malware infections

\- Limited cybersecurity awareness



Many users and small organizations cannot access professional cybersecurity tools because of:



\- Cost limitations

\- Poor internet availability

\- Lack of technical expertise



AfriShield AI addresses these challenges through an offline and accessible AI-powered cybersecurity assistant.



\---



\# 3. Motivation



Traditional cybersecurity solutions often depend on:



\- Cloud services

\- Expensive security platforms

\- Continuous internet connectivity



However, many communities require solutions that can function independently.



The motivation behind AfriShield AI is to create a cybersecurity assistant that:



\- Works offline

\- Protects user privacy

\- Uses local AI processing

\- Provides practical security guidance

\- Supports African digital environments



\---



\# 4. System Objectives



The main objectives are:



\## Primary Objectives



\- Build an offline cybersecurity AI assistant

\- Provide threat analysis capabilities

\- Detect online scams

\- Provide cybersecurity knowledge assistance

\- Generate incident response recommendations



\## Secondary Objectives



\- Reduce dependency on cloud AI services

\- Improve cybersecurity awareness

\- Provide affordable security assistance



\---



\# 5. System Architecture



AfriShield AI consists of several major components:



&#x20;```text

&#x20;                   User

&#x20;                     |

&#x20;                     |

&#x20;           Streamlit Interface

&#x20;                     |

&#x20;                     |

&#x20;       +-------------+-------------+

&#x20;       |             |             |

&#x20;       |             |             |

&#x20;  Threat        Scam Detection   Incident

&#x20;Detection                        Response

&#x20;       |             |             |

&#x20;       +-------------+-------------+

&#x20;                     |

&#x20;                     |

&#x20;             RAG Retrieval System

&#x20;                     |

&#x20;                     |

&#x20;            Chroma Vector Database

&#x20;                     |

&#x20;                     |

&#x20;      Cybersecurity Knowledge Base

&#x20;                     |

&#x20;                     |

&#x20;             Llama 3.2 Local LLM

&#x20;                     |

&#x20;                     |

&#x20;                AI Response

```

\---



\# 6. Artificial Intelligence Approach



\## 6.1 Local Large Language Model



AfriShield AI uses:



\*\*Model: Llama 3.2 3B\*\*



The model runs locally using:



\*\*Ollama Runtime\*\*



Benefits:



\- Offline operation

\- Privacy protection

\- Reduced cloud dependency

\- Suitable for low-resource environments



\---



\# 6.2 Retrieval-Augmented Generation (RAG)



The system uses RAG to improve response accuracy.



Instead of relying only on the language model's internal knowledge, AfriShield AI retrieves relevant information from cybersecurity documents.



Knowledge sources include:



\- OWASP Security Documentation

\- NIST Cybersecurity Materials

\- Incident Response Guides





RAG Pipeline:



User Query

|

|

Embedding Generation

|

|

Similarity Search

|

|

Chroma Vector Database

|

|

Relevant Documents

|

|

Llama 3.2

|

|

Final Response





\---



\# 7. Cybersecurity Modules



\## 7.1 Threat Detection



The threat detection module analyzes suspicious content and identifies possible cyber risks.



Capabilities:



\- Phishing identification

\- Suspicious message analysis

\- Threat classification

\- Security recommendations



\---



\## 7.2 Scam Detection



The scam detection module identifies common fraud patterns.



Examples:



\- Fake banking messages

\- Fake investment opportunities

\- Fake job offers

\- Suspicious links

\- Social engineering attempts



\---



\## 7.3 Incident Response System



The incident response module provides recommended actions after a security event.



Examples:



\- Account compromise

\- Malware infection

\- Phishing incidents

\- Unauthorized access



\---



\# 8. Technology Stack



| Component | Technology |

|-|-|

| Programming Language | Python |

| Interface | Streamlit |

| AI Model | Llama 3.2 |

| AI Runtime | Ollama |

| Retrieval System | RAG |

| Vector Database | ChromaDB |

| Document Processing | PyPDF |

| Embeddings | Sentence Transformers |



\---



\# 9. Implementation Details



\## Data Processing



Cybersecurity documents are:



1\. Loaded from PDF sources

2\. Extracted into text

3\. Split into smaller chunks

4\. Converted into embeddings

5\. Stored in ChromaDB



\---



\## Knowledge Retrieval



When a user asks a question:



1\. The query is converted into an embedding

2\. Similar documents are retrieved

3\. Retrieved information is provided to the LLM

4\. The AI generates a security response



\---



\# 10. Offline Design



A major design decision was avoiding cloud dependency.



Advantages:



\- User data remains local

\- Works without internet

\- Lower operating cost

\- Suitable for African environments



\---



\# 11. Innovation



AfriShield AI introduces an offline-first cybersecurity assistance model that combines:



\- Local Large Language Models

\- Retrieval-Augmented Generation

\- Cybersecurity knowledge retrieval

\- Threat detection

\- Scam analysis

\- Incident response guidance



Unlike traditional cloud-based assistants, AfriShield AI can operate without internet connectivity, making it more suitable for underserved and low-connectivity environments.



\# 12. Current Limitations



Current limitations include:



\- Limited African-language support

\- No malware file analysis yet

\- Limited cybersecurity dataset size

\- Performance depends on available hardware



These limitations are planned areas for future development.



\# 13. Evaluation and Testing



Testing was performed on:



Hardware:



\- Intel Core i5 CPU

\- 8GB RAM



Software:



\- Python

\- Ollama

\- Llama 3.2 3B



Evaluation areas:



| Component | Status |

|-|-|

| Offline AI | Completed |

| RAG System | Completed |

| Knowledge Retrieval | Completed |

| Threat Detection | Completed |

| Scam Detection | Completed |

| Incident Response | Completed |

| Dashboard | Completed |



\---



\# 14. Challenges and Solutions



\## Challenge: Limited Hardware Resources



Solution:



Used lightweight local models and optimized retrieval.



\---



\## Challenge: Improving AI Accuracy



Solution:



Implemented RAG using trusted cybersecurity documents.



\---



\## Challenge: Internet Dependency



Solution:



Designed the entire system to operate offline.



\---



\# 15. Future Improvements



Future versions may include:



\- African language support

\- Malware analysis

\- Mobile deployment

\- Larger cybersecurity datasets

\- Advanced threat intelligence

\- Community security reporting



\---



\# 16. Conclusion



AfriShield AI demonstrates how offline artificial intelligence can provide practical cybersecurity assistance for African communities.



By combining local AI, RAG technology, and cybersecurity automation, the project provides an affordable and accessible security solution designed for environments with limited connectivity.



\---



\# Author



Mu'assir Ismail Dalhat (Midian)



Computer Science Student

Cybersecurity Analyst 

AI Enthusiast  

Aspiring AI Security Engineer











