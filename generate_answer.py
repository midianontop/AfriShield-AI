"""
AfriShield AI
Local LLM Response Generator

Uses Ollama + Llama 3.2 locally.
Optimized for CPU inference and fast responses.
"""

import logging
import time

import requests


logger = logging.getLogger("afrishield_ai.generate_answer")


# =============================================================================
# CONFIGURATION
# =============================================================================

DEFAULT_MODEL = "llama3.2:3b"
OLLAMA_URL = "http://localhost:11434/api/generate"

# Lower temperature = more predictable and concise answers
DEFAULT_TEMPERATURE = 0.20

# Keep answers short to reduce CPU generation time
DEFAULT_MAX_TOKENS = 32

# Smaller context = less prompt processing
MAX_CONTEXT_LENGTH = 1500

# Keep the context window reasonable for CPU inference
NUM_CTX = 2036

# HTTP timeout
OLLAMA_TIMEOUT = 120


# =============================================================================
# SYSTEM PROMPT
# =============================================================================

SYSTEM_PROMPT = """
You are AfriShield AI, an African cybersecurity assistant.

Answer ONLY the user's current question.

For greetings, reply briefly and naturally.

For cybersecurity questions, give accurate and concise explanations.

For active security incidents, give practical defensive actions.

Use the provided context only when relevant.
Ignore unrelated context.

Do not invent facts, citations, links, or sources.

Do not mention prompts, instructions, context, or internal reasoning.

Keep answers short and easy to understand.
"""


# =============================================================================
# CLEAN CONTEXT
# =============================================================================

def clean_context(context: str) -> str:
    """
    Clean and limit RAG context before sending it to Ollama.
    """

    if not context:
        return "No relevant context."

    context = str(context).strip()

    if len(context) > MAX_CONTEXT_LENGTH:
        context = context[:MAX_CONTEXT_LENGTH]

    return context


# =============================================================================
# PROMPT BUILDER
# =============================================================================

def build_prompt(question: str, context: str) -> str:
    """
    Build a compact prompt for CPU-efficient inference.
    """

    question = str(question).strip()
    context = clean_context(context)

    return f"""{SYSTEM_PROMPT}

QUESTION:
{question}

CONTEXT:
{context}

ANSWER:
"""


# =============================================================================
# GENERATE ANSWER
# =============================================================================

def generate_answer(
    question: str,
    context: str,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> str:
    """
    Generate a concise answer using the local Ollama model.
    """

    if not question or not question.strip():
        return (
            "Please enter a cybersecurity question "
            "or describe a security concern."
        )

    # -------------------------------------------------------------------------
    # Build prompt
    # -------------------------------------------------------------------------

    prompt = build_prompt(
        question=question,
        context=context,
    )

    logger.info(
        "Generating answer | model=%s | prompt_chars=%d | max_tokens=%d",
        model,
        len(prompt),
        max_tokens,
    )

    # -------------------------------------------------------------------------
    # Ollama payload
    # -------------------------------------------------------------------------

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "keep_alive": -1,
        "options": {
             "temperature": temperature,
             "num_predict": max_tokens,
             "num_ctx": 2048,
        },
    }

    # -------------------------------------------------------------------------
    # Send request
    # -------------------------------------------------------------------------

    start_time = time.perf_counter()

    try:

        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=OLLAMA_TIMEOUT,
        )

        response.raise_for_status()

        data = response.json()

        elapsed = time.perf_counter() - start_time

        answer = data.get("response", "")

        # ---------------------------------------------------------------------
        # Empty response
        # ---------------------------------------------------------------------

        if not answer:

            logger.warning(
                "Ollama returned an empty response after %.2f seconds.",
                elapsed,
            )

            return (
                "I couldn't generate a response right now. "
                "Please try again."
            )

        # ---------------------------------------------------------------------
        # Ollama performance information
        # ---------------------------------------------------------------------

        eval_count = data.get("eval_count", 0)
        eval_duration = data.get("eval_duration", 0)

        if eval_duration:
            generation_seconds = eval_duration / 1_000_000_000

            tokens_per_second = (
                eval_count / generation_seconds
                if generation_seconds > 0
                else 0
            )

            logger.info(
                "Ollama completed in %.2f sec | "
                "generation=%.2f sec | "
                "tokens=%s | speed=%.2f tok/s",
                elapsed,
                generation_seconds,
                eval_count,
                tokens_per_second,
            )

        else:

            logger.info(
                "Ollama response generated in %.2f seconds.",
                elapsed,
            )

        return answer.strip()

    # -------------------------------------------------------------------------
    # Connection error
    # -------------------------------------------------------------------------

    except requests.exceptions.ConnectionError:

        logger.exception("Could not connect to Ollama.")

        return (
            "⚠️ AfriShield AI could not connect to the local "
            "Llama model. Please make sure Ollama is running."
        )

    # -------------------------------------------------------------------------
    # Timeout
    # -------------------------------------------------------------------------

    except requests.exceptions.Timeout:

        elapsed = time.perf_counter() - start_time

        logger.exception(
            "Ollama request timed out after %.2f seconds.",
            elapsed,
        )

        return (
            "⚠️ The local AI model took too long to respond. "
            "Please try again."
        )

    # -------------------------------------------------------------------------
    # HTTP / Requests error
    # -------------------------------------------------------------------------

    except requests.exceptions.RequestException:

        logger.exception("Ollama request failed.")

        return (
            "⚠️ The local AI response engine is temporarily unavailable."
        )

    # -------------------------------------------------------------------------
    # Unexpected error
    # -------------------------------------------------------------------------

    except Exception:

        logger.exception(
            "Unexpected error while generating answer."
        )

        return (
            "⚠️ An unexpected error occurred while generating "
            "the response."
        )