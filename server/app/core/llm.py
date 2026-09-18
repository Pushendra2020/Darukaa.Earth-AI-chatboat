from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def get_llm() -> BaseChatModel:
    provider = settings.LLM_PROVIDER.lower()
    if provider == "openrouter":
        return ChatOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            model=settings.OPENROUTER_LLM_MODEL,
        )
    elif provider == "nvidia":
        return ChatOpenAI(
            api_key=settings.NVIDIA_API_KEY,
            base_url="https://integrate.api.nvidia.com/v1",
            model=settings.NVIDIA_MODEL,
        )
    elif provider == "google":
        return ChatGoogleGenerativeAI(
            api_key=settings.GOOGLE_API_KEY,
            model=settings.GOOGLE_MODEL,
        )
    else:
        logger.warning(f"Unknown provider {provider}, falling back to openrouter")
        return ChatOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            model=settings.OPENROUTER_LLM_MODEL,
        )

def get_embeddings() -> Embeddings:
    return OpenAIEmbeddings(
        api_key=settings.NVIDIA_API_KEY,
        base_url="https://integrate.api.nvidia.com/v1",
        model="nvidia/nemotron-3-embed-1b"
    )

# Abstractions for LangGraph nodes to use
def generate_text(prompt: str) -> str:
    llm = get_llm()
    response = llm.invoke(prompt)
    return response.content

def generate_structured(prompt: str, schema) -> dict:
    llm = get_llm()
    structured_llm = llm.with_structured_output(schema)
    response = structured_llm.invoke(prompt)
    if hasattr(response, 'model_dump'):
        return response.model_dump()
    return response
