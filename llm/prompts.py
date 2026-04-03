from typing import List

SYSTEM_MEMORY_EXTRACTION = """You are an advanced memory extraction assistant. \n"""
FEW_SHOT_MEMORIES = [
    {
        "conversation": "User: I always want Python code.\nAssistant: Sure, I will use Python.",
        "output": [
            {"type": "semantic", "key": "language_preference", "value": {"fact": "User prefers Python", "evidence_count": 1}},
        ],
    },
    {
        "conversation": "User: We need daily build status by 4 PM.\nAssistant: Understood, daily status report by 4 PM.",
        "output": [
            {"type": "episodic", "key": "daily_build_status_goal", "value": {"summary": "Needs daily status by 4 PM", "timestamp": "TODO"}},
        ],
    },
]


def build_memory_extraction_prompt(conversation: str) -> str:
    instructions = """
    Extract semantic, episodic, and correction memories from the conversation.
    Output a JSON array with objects:
     - type: episodic|semantic|correction
     - key: string
     - value: object
    """
    shots = "\n\n".join([
        f"Conversation:\n{shot['conversation']}\nOutput:\n{shot['output']}" for shot in FEW_SHOT_MEMORIES
    ])
    return f"{SYSTEM_MEMORY_EXTRACTION}\n{instructions}\n\n{shots}\n\nConversation:\n{conversation}\nOutput:" 
