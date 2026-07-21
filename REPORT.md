# AfriShield AI

## Technical Project Report

### Africa Deep Tech Challenge 2026

---

# 1. Executive Summary

AfriShield AI is an offline artificial intelligence cybersecurity assistant designed to provide accessible cybersecurity intelligence for individuals, organizations, and small businesses, especially in environments with limited internet connectivity.

The system combines local Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), cybersecurity knowledge bases, threat detection algorithms, scam detection capabilities, and incident response guidance.

Unlike traditional cloud-based AI security assistants, AfriShield AI performs analysis locally, improving privacy, reducing dependency on internet connectivity, and making cybersecurity assistance more accessible for African communities.

The project focuses on addressing common cybersecurity challenges affecting African digital users, including phishing attacks, online scams, identity theft, social engineering, account compromise, and malware-related incidents.

---

# 2. Project Overview

## Project Name

**AfriShield AI - Offline AI Cybersecurity Assistant for Africa**

## Project Description

AfriShield AI is an offline cybersecurity intelligence platform powered by artificial intelligence.

The system provides users with:

* Cybersecurity question answering
* Suspicious message analysis
* Threat classification
* Scam detection
* Incident response recommendations
* Security awareness assistance

The platform operates without external AI APIs or cloud dependency by using locally running AI models and locally stored cybersecurity knowledge.

---

# 3. Problem Statement

Cybersecurity threats continue to increase across Africa as digital adoption expands.

Individuals, businesses, and organizations face challenges including:

* Phishing attacks
* Financial scams
* Identity theft
* Account takeover attacks
* Malware infections
* Social engineering attacks
* Data breaches

Many users lack access to professional cybersecurity assistance because of:

* High cost of security solutions
* Limited cybersecurity awareness
* Poor internet availability in some regions
* Lack of technical expertise

AfriShield AI addresses these challenges by providing an affordable, offline, and accessible cybersecurity assistant.

---

# 4. Motivation

Many existing AI assistants and cybersecurity platforms depend on:

* Cloud infrastructure
* Continuous internet access
* Expensive security subscriptions
* External data processing

However, many African environments require solutions that can operate independently.

The motivation behind AfriShield AI is to build a privacy-focused cybersecurity assistant that:

* Works offline
* Processes information locally
* Protects user privacy
* Provides practical security recommendations
* Supports African cybersecurity needs

---

# 5. System Objectives

## Primary Objectives

The main objectives of AfriShield AI are:

* Build an offline cybersecurity AI assistant
* Provide intelligent threat analysis
* Detect cybersecurity scams
* Provide security knowledge assistance
* Generate incident response recommendations

## Secondary Objectives

Additional objectives include:

* Reducing dependency on cloud AI services
* Improving cybersecurity awareness
* Supporting low-resource environments
* Providing accessible security guidance

---

# 6. System Architecture

AfriShield AI consists of several integrated components.

```text
                         User
                           |
                           |
                  Streamlit Interface
                           |
        +------------------+------------------+
        |                  |                  |
        |                  |                  |
 Threat Detection    Scam Detection    Incident Response
        |                  |                  |
        +------------------+------------------+
                           |
                           |
                 RAG Retrieval Pipeline
                           |
                           |
                 Chroma Vector Database
                           |
                           |
          Cybersecurity Knowledge Base
                           |
                           |
                 Llama 3.2 Local LLM
                           |
                           |
                    AI Response
```

---

# 7. Artificial Intelligence Approach

## 7.1 Local Large Language Model

AfriShield AI uses:

**Model:** Llama 3.2 3B

**Runtime:** Ollama

The model operates locally on the user's machine without requiring external AI services.

Advantages:

* Offline operation
* Improved privacy
* Reduced cloud dependency
* Lower operational cost
* Suitable for low-resource environments

---

# 7.2 Retrieval-Augmented Generation (RAG)

AfriShield AI uses Retrieval-Augmented Generation to improve response accuracy.

Instead of depending only on the LLM's internal knowledge, the system retrieves relevant cybersecurity information from trusted documents before generating responses.

Knowledge sources include:

* OWASP Security Documentation
* NIST Cybersecurity Resources
* Incident Response Guides
* Cybersecurity educational materials

---

# 7.3 AI Processing Pipeline

The complete AI workflow:

```text
User Query

      |

Threat and Scam Analysis

      |

Query Processing

      |

Embedding Generation

      |

Similarity Search

      |

Chroma Vector Database

      |

Relevant Cybersecurity Context

      |

Llama 3.2 Local Generation

      |

Security Recommendation
```

---

# 8. Cybersecurity Intelligence Modules

## 8.1 Threat Detection Engine

The threat detection engine analyzes user messages and identifies possible cybersecurity risks.

Capabilities include:

* Threat classification
* Severity assessment
* Confidence scoring
* Security recommendations

Supported threat categories:

* Phishing attacks
* Account compromise
* Malware infection
* Ransomware
* Financial fraud
* Data breaches
* DDoS attacks

The system also includes African cybersecurity indicators such as:

* WhatsApp account takeover
* BVN scams
* NIN-related fraud
* SIM swap attacks
* Mobile payment fraud
* 419 scams

---

# 8.2 Scam Detection Engine

The scam detection module identifies suspicious social engineering patterns.

Examples include:

* Fake banking messages
* Fake investment opportunities
* Fake job offers
* Suspicious links
* OTP requests
* Identity verification scams

The system warns users against sharing sensitive information including:

* Passwords
* OTP codes
* BVN
* NIN
* ATM PINs
* Bank details

---

# 8.3 Incident Response System

The incident response module provides recommended actions after detecting a security event.

Examples:

For account compromise:

* Change passwords
* Enable multi-factor authentication
* Review account activity

For phishing:

* Avoid suspicious links
* Report malicious messages
* Verify communication sources

For malware incidents:

* Disconnect affected devices
* Perform security checks
* Remove malicious software

---

# 9. Technology Stack

| Component            | Technology            |
| -------------------- | --------------------- |
| Programming Language | Python                |
| User Interface       | Streamlit             |
| AI Model             | Llama 3.2 3B          |
| AI Runtime           | Ollama                |
| Retrieval System     | RAG                   |
| Vector Database      | ChromaDB              |
| Document Processing  | PyPDF                 |
| Embeddings           | Sentence Transformers |
| Version Control      | Git/GitHub            |

---

# 10. Implementation Details

## Data Processing Pipeline

Cybersecurity documents are processed through the following steps:

1. Load PDF cybersecurity resources
2. Extract text content
3. Split documents into smaller chunks
4. Generate embeddings
5. Store embeddings in ChromaDB

---

## Knowledge Retrieval Process

When a user submits a query:

1. The query is converted into an embedding
2. Similar cybersecurity documents are retrieved
3. Relevant context is provided to the LLM
4. Llama 3.2 generates a security response

---

# 11. Offline Security Design

A major design decision was making AfriShield AI completely offline.

Benefits:

* User information remains on the device
* No external API dependency
* Improved privacy protection
* Works without internet connectivity
* Suitable for low-connectivity environments

Security-related data such as incident logs are stored locally.

---

# 12. Innovation

AfriShield AI introduces an offline-first cybersecurity intelligence approach by combining:

* Local AI models
* Retrieval-Augmented Generation
* Cybersecurity knowledge retrieval
* Threat intelligence analysis
* Scam detection
* Incident response automation

The project is specifically designed around African cybersecurity challenges, making it different from general-purpose AI assistants.

---

# 13. User Interface and Features

The Streamlit dashboard provides:

* AI cybersecurity chat interface
* Threat severity visualization
* Scam alerts
* Incident statistics
* AI engine status monitoring
* Chat export functionality

The interface allows users to interact with the cybersecurity assistant naturally.

---

# 14. Evaluation and Benchmarking

Testing was performed on:

## Hardware

* Intel Core i5-7200U Processor
* 8GB RAM

## Software Environment

* Python
* Ollama
* Llama 3.2 3B
* Streamlit
* ChromaDB

## Functional Evaluation

| Component           | Status    |
| ------------------- | --------- |
| Offline AI          | Completed |
| RAG System          | Completed |
| Knowledge Retrieval | Completed |
| Threat Detection    | Completed |
| Scam Detection      | Completed |
| Incident Response   | Completed |
| Dashboard           | Completed |

---

# 15. Performance Evaluation

Benchmark testing results:

| Metric                | Result                           |
| --------------------- | -------------------------------- |
| Startup Time          | 38.7 seconds                     |
| Average Response Time | 72.2 seconds                     |
| Offline Operation     | Supported                        |
| Internet Requirement  | None                             |
| Memory Usage          | Approximately 467 MB Working Set |

The response time is affected by CPU-only inference using a local Llama 3.2 model.

Future optimization areas include:

* Model quantization
* Faster embeddings
* Response caching
* Hardware acceleration

The system prioritizes privacy, offline capability, and accessibility.

---

# 16. Challenges and Solutions

## Challenge: Limited Hardware Resources

### Solution

Used lightweight local AI models and optimized retrieval methods.

---

## Challenge: Improving AI Accuracy

### Solution

Implemented RAG using trusted cybersecurity documentation.

---

## Challenge: Internet Dependency

### Solution

Designed the complete system to operate offline.

---

# 17. Current Limitations

Current limitations include:

* Limited African language support
* No malware file analysis capability
* Limited cybersecurity dataset size
* Performance depends on available hardware

These areas are planned for future development.

---

# 18. Future Improvements

Future versions may include:

* African language cybersecurity assistance
* Malware file analysis
* Mobile application deployment
* Larger cybersecurity datasets
* Advanced threat intelligence integration
* Community-based security reporting
* Faster AI inference optimization

---

# 19. Conclusion

AfriShield AI demonstrates how offline artificial intelligence can provide practical cybersecurity assistance for African communities.

By combining local AI, Retrieval-Augmented Generation, cybersecurity intelligence, and automated threat analysis, the project provides an accessible security solution designed for environments where privacy, affordability, and offline capability are important.

AfriShield AI represents a step toward building locally adaptable cybersecurity technology for Africa.

---

# Author

**Mu'assir Ismail Dalhat (Midian)**

Computer Science Student
Cybersecurity Researcher
AI Security Enthusiast
Aspiring AI Security Engineer
