"""
Unified LLM Provider — agent/llm_provider.py

Manages 5 free LLM providers with automatic fallback in priority order:

  1. Groq          — LLaMA 3.3 70B  (fastest free tier, 14,400 TPM)
  2. OpenRouter    — gemini-2.0-flash-exp:free / llama-3.3-70b:free
  3. NVIDIA NIM    — llama-3.3-70b-instruct (1,000 free build credits)
  4. Gemini        — gemini-2.0-flash (Google AI Studio, 1M TPM free)
  5. Cohere        — command-r (free developer key)

Usage:
    from agent.llm_provider import get_llm, get_llm_with_fallback

    # Get the best available LLM right now:
    llm = get_llm(temperature=0.2)

    # Build and run a chain with automatic fallback across all providers:
    result = get_llm_with_fallback(
        prompt_template=my_prompt,
        output_schema=MyPydanticModel,
        input_vars={"key": "value"},
        temperature=0.2,
    )
"""

import os
import logging
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


# ==================== PROVIDER CONFIGS ====================
# Each entry: (name, env_key, factory_fn, supports_structured_output)

def _try_groq(temperature: float):
    """Groq — LLaMA 3.3 70B versatile. Primary: fastest free inference."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key.startswith("your-"):
        return None
    from langchain_groq import ChatGroq
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=api_key,
        temperature=temperature,
    )


def _try_openrouter(temperature: float):
    """OpenRouter — gemini-2.0-flash-exp:free (OpenAI-compatible API)."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or api_key.startswith("your-"):
        return None
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model="google/gemini-2.0-flash-exp:free",
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=temperature,
        default_headers={
            "HTTP-Referer": "https://github.com/Aesthetic002/job-search-ai-agent",
            "X-Title": "Job Search AI Agent",
        },
    )


def _try_nvidia(temperature: float):
    """NVIDIA NIM — LLaMA 3.3 70B instruct (OpenAI-compatible API)."""
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key or api_key.startswith("your-"):
        return None
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model="meta/llama-3.3-70b-instruct",
        api_key=api_key,
        base_url="https://integrate.api.nvidia.com/v1",
        temperature=temperature,
    )


def _try_gemini(temperature: float):
    """Google Gemini — gemini-2.0-flash via Google AI Studio."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key.startswith("your-"):
        return None
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=api_key,
        temperature=temperature,
    )


def _try_cohere(temperature: float):
    """Cohere — command-r (free developer trial key)."""
    api_key = os.getenv("COHERE_API_KEY")
    if not api_key or api_key.startswith("your-"):
        return None
    from langchain_cohere import ChatCohere
    return ChatCohere(
        model="command-r",
        cohere_api_key=api_key,
        temperature=temperature,
    )


# Priority order — best free model first
_PROVIDER_FACTORIES = [
    ("Groq (LLaMA 3.3 70B)", _try_groq),
    ("OpenRouter (gemini-2.0-flash:free)", _try_openrouter),
    ("NVIDIA NIM (LLaMA 3.3 70B)", _try_nvidia),
    ("Gemini (gemini-2.0-flash)", _try_gemini),
    ("Cohere (command-r)", _try_cohere),
]


# ==================== PUBLIC API ====================

def get_llm(temperature: float = 0.2):
    """
    Return the first available LLM instance in priority order.

    Tries providers in order: Groq → OpenRouter → NVIDIA NIM → Gemini → Cohere.
    Skips any provider whose API key is missing or still set to the placeholder value.

    Raises:
        RuntimeError: If no provider is configured with a valid API key.
    """
    configured = []
    for name, factory in _PROVIDER_FACTORIES:
        try:
            llm = factory(temperature)
            if llm is not None:
                logger.info(f"[LLMProvider] Using: {name}")
                return llm
        except ImportError as e:
            logger.debug(f"[LLMProvider] {name} skipped — package not installed: {e}")
        except Exception as e:
            logger.debug(f"[LLMProvider] {name} init failed: {e}")
        configured.append(name)

    raise RuntimeError(
        "No LLM provider is configured. Add at least one API key to your .env file.\n"
        "Supported providers: GROQ_API_KEY, OPENROUTER_API_KEY, NVIDIA_API_KEY, GEMINI_API_KEY, COHERE_API_KEY\n"
        "Get free keys at:\n"
        "  Groq:       https://console.groq.com\n"
        "  OpenRouter: https://openrouter.ai/keys\n"
        "  NVIDIA NIM: https://build.nvidia.com\n"
        "  Gemini:     https://aistudio.google.com\n"
        "  Cohere:     https://dashboard.cohere.com"
    )


def get_llm_with_fallback(
    prompt_template: ChatPromptTemplate,
    output_schema: Type[BaseModel],
    input_vars: Dict[str, Any],
    temperature: float = 0.2,
) -> BaseModel:
    """
    Execute a structured LangChain chain with automatic fallback across all providers.

    On any error (rate limit, API error, network issue), automatically tries
    the next provider in the priority list.

    Args:
        prompt_template:  The ChatPromptTemplate to use.
        output_schema:    A Pydantic BaseModel class for structured output.
        input_vars:       Dict of variables to pass to the prompt template.
        temperature:      LLM temperature (default 0.2 for consistency).

    Returns:
        An instance of output_schema populated with the LLM's response.

    Raises:
        RuntimeError: If all configured providers fail.
    """
    errors = []

    for name, factory in _PROVIDER_FACTORIES:
        try:
            llm = factory(temperature)
            if llm is None:
                continue  # Key not configured, skip silently

            logger.info(f"[LLMProvider] Attempting with: {name}")
            structured_llm = llm.with_structured_output(output_schema)
            chain = prompt_template | structured_llm
            result = chain.invoke(input_vars)
            logger.info(f"[LLMProvider] Success with: {name}")
            return result

        except ImportError as e:
            logger.debug(f"[LLMProvider] {name} skipped — package missing: {e}")
        except Exception as e:
            error_msg = f"{name}: {type(e).__name__}: {str(e)[:120]}"
            logger.warning(f"[LLMProvider] {name} failed, trying next. Error: {e}")
            errors.append(error_msg)

    raise RuntimeError(
        f"All LLM providers failed. Errors:\n" + "\n".join(f"  - {e}" for e in errors)
    )


def list_configured_providers() -> List[str]:
    """
    Return a list of provider names that have valid (non-placeholder) API keys configured.
    Useful for health checks and debugging.
    """
    available = []
    for name, factory in _PROVIDER_FACTORIES:
        try:
            llm = factory(0.0)
            if llm is not None:
                available.append(name)
        except Exception:
            pass
    return available


# ==================== STANDALONE CHECK ====================

if __name__ == "__main__":
    print("Checking configured LLM providers...\n")
    providers = list_configured_providers()
    if providers:
        print(f"Available providers ({len(providers)}):")
        for p in providers:
            print(f"  - {p}")
        print(f"\nPrimary provider: {providers[0]}")
    else:
        print("No providers configured. Please add API keys to .env")

    print("\nRunning quick smoke test with primary provider...")
    from langchain_core.prompts import ChatPromptTemplate
    from pydantic import BaseModel, Field

    class TestResponse(BaseModel):
        answer: str = Field(description="A one-sentence answer")
        confidence: str = Field(description="high, medium, or low")

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Answer concisely."),
        ("human", "What is {topic}?"),
    ])

    try:
        result = get_llm_with_fallback(
            prompt_template=prompt,
            output_schema=TestResponse,
            input_vars={"topic": "LangChain"},
            temperature=0.1,
        )
        print(f"\nSmoke test PASSED:")
        print(f"  Answer: {result.answer}")
        print(f"  Confidence: {result.confidence}")
    except RuntimeError as e:
        print(f"\nSmoke test FAILED: {e}")
