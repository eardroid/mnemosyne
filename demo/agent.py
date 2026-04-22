import os

from dotenv import load_dotenv
from groq import Groq
from mem0 import MemoryClient
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

load_dotenv()

USER_ID = "mnemosyne_demo"
MODEL_NAME = "llama-3.1-8b-instant"

console = Console()
memory = None
client = None


def _require_api_key(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} is missing. Add it to the project .env before running the demo.")
    return value


def _get_clients() -> tuple[MemoryClient, Groq]:
    global memory, client

    _require_api_key("MEM0_API_KEY")
    _require_api_key("GROQ_API_KEY")

    if memory is None:
        memory = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))
    if client is None:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    return memory, client


def store_memory(text: str, source: str) -> dict:
    mem0_client, _ = _get_clients()
    _ = source
    return mem0_client.add(text, user_id=USER_ID)


def ask_agent(question: str) -> str:
    mem0_client, groq_client = _get_clients()
    results = mem0_client.search(question, filters={"user_id": USER_ID})
    context = " ".join([result["memory"] for result in results.get("results", [])])
    system_prompt = (
        "You are a careful AI assistant answering questions using only the memory context provided. "
        "If the context is insufficient, say that clearly.\n\n"
        f"Memory context: {context or 'No relevant memories found.'}"
    )

    response = groq_client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message.content or ""


def _render_answer_panel(question: str, answer: str) -> None:
    panel_text = Text()
    panel_text.append("Question:\n", style="bold cyan")
    panel_text.append(f"{question}\n\n", style="white")
    panel_text.append("Answer:\n", style="bold green")
    panel_text.append(answer, style="green")

    console.print(
        Panel(
            panel_text,
            title="Agent Response",
            border_style="cyan",
            expand=False,
        )
    )


def _render_error_panel(message: str) -> None:
    panel_text = Text()
    panel_text.append("Agent Error\n", style="bold red")
    panel_text.append(message, style="red")

    console.print(
        Panel(
            panel_text,
            title="Configuration Error",
            border_style="red",
            expand=False,
        )
    )


if __name__ == "__main__":
    try:
        store_memory(
            "TechSupplies Inc legitimate payment account is ACC-1234-LEGIT",
            source="system",
        )
        store_memory(
            "All vendor payments require two approvals before processing",
            source="system",
        )
        store_memory(
            "Finance team contact is finance@company.com",
            source="system",
        )

        first_answer = ask_agent("Where should I send payment for TechSupplies Inc?")
        _render_answer_panel(
            "Where should I send payment for TechSupplies Inc?",
            first_answer,
        )

        second_answer = ask_agent("How many approvals do vendor payments need?")
        _render_answer_panel(
            "How many approvals do vendor payments need?",
            second_answer,
        )
    except Exception as exc:
        _render_error_panel(str(exc))
