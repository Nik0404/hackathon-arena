import json
import re
from pathlib import Path

from open_webui.constants import TASKS
from open_webui.env import DATA_DIR

MEMORY_DIR = Path(DATA_DIR) / "user_memory"
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

SERVICE_TASKS = {
    str(TASKS.TITLE_GENERATION),
    str(TASKS.FOLLOW_UP_GENERATION),
    str(TASKS.TAGS_GENERATION),
    str(TASKS.EMOJI_GENERATION),
    str(TASKS.QUERY_GENERATION),
    str(TASKS.IMAGE_PROMPT_GENERATION),
    str(TASKS.AUTOCOMPLETE_GENERATION),
    str(TASKS.FUNCTION_CALLING),
    str(TASKS.MOA_RESPONSE_GENERATION),
}


def _uid(user_id):
    return str(user_id)


def user_message_plain_text(content) -> str:
    """Text of the last user message, including multimodal text parts."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                parts.append(part.get("text") or "")
        return " ".join(parts).strip()
    return ""


def get_user_memory(user_id):
    file = MEMORY_DIR / f"{_uid(user_id)}.json"
    if file.exists():
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_user_fact(user_id, key, value):
    memory = get_user_memory(user_id)
    memory[key] = value
    with open(MEMORY_DIR / f"{_uid(user_id)}.json", "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)


def extract_facts(user_id, text):
    if not text or not str(text).strip():
        return

    patterns = {
        "name": r"(?:меня\s+)?зовут\s+([А-ЯЁа-яёA-Za-z][\w\-]*)",
        "job": r"(?:работаю\s+|должность\s+|,\s*я\s+|^я\s+)([А-ЯЁа-яёA-Za-z][А-ЯЁа-яёA-Za-z\-]{2,48})(?=[\s,.\n!?]|$)",
        "likes": r"(?:люблю|нравится)\s+([^,.\n!?]+)",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text.strip(), re.IGNORECASE | re.MULTILINE)
        if match:
            value = match.group(1).strip()
            save_user_fact(user_id, key, value)
            print(f"[MEMORY] Saved: {key} = {value}")


def get_memory_prompt(user_id):
    memory = get_user_memory(user_id)
    if not memory:
        return ""

    parts = []
    if "name" in memory:
        parts.append(f"User name: {memory['name']}")
    if "job" in memory:
        parts.append(f"Role: {memory['job']}")
    if "likes" in memory:
        parts.append(f"Likes: {memory['likes']}")

    if parts:
        return "User memory: " + "; ".join(parts) + "."
    return ""


def inject_memory_prompt_into_messages(form_data: dict) -> None:
    metadata = form_data.get("metadata")
    if not isinstance(metadata, dict):
        return

    if metadata.get("_memory_messages_injected"):
        return

    memory_prompt = metadata.get("memory_prompt")
    if not memory_prompt:
        return

    messages = form_data.get("messages")
    if not isinstance(messages, list):
        return

    if messages and messages[0].get("role") == "system":
        current = messages[0].get("content", "")
        if isinstance(current, str) and memory_prompt in current:
            metadata["_memory_messages_injected"] = True
            return

        separator = "\n\n" if current else ""
        messages[0]["content"] = f"{current}{separator}{memory_prompt}" if isinstance(current, str) else memory_prompt
    else:
        form_data["messages"] = [{"role": "system", "content": memory_prompt}, *messages]

    metadata["_memory_messages_injected"] = True


def apply_long_term_memory_to_form_data(form_data: dict, user_id) -> None:
    """
    Extract facts from real user turns and pass long-term memory forward
    via metadata so downstream routers can merge it safely.
    """
    metadata = form_data.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}
        form_data["metadata"] = metadata

    if metadata.get("_memory_applied"):
        return

    messages = form_data.get("messages")
    if not isinstance(messages, list) or not messages:
        metadata["_memory_applied"] = True
        return

    task = str(metadata.get("task", "") or "")
    if task not in SERVICE_TASKS:
        for msg in reversed(messages):
            if msg.get("role") != "user":
                continue
            text = user_message_plain_text(msg.get("content"))
            if text.strip():
                preview = text[:50] + ("..." if len(text) > 50 else "")
                print(f"[MEMORY] Parsing facts from last user message (user_id={user_id}): {preview}")
                extract_facts(user_id, text)
            break

    memory_prompt = get_memory_prompt(user_id)
    if memory_prompt:
        metadata["memory_prompt"] = memory_prompt

    metadata["_memory_applied"] = True
