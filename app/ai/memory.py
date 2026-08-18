from typing import Dict, Any

class AIMemory:
    """
    Session memory for retaining user travel preferences and ongoing trip conversation state.
    """
    _memory_store = {}

    @classmethod
    def get_state(cls, user_id: int) -> Dict[str, Any]:
        return cls._memory_store.get(user_id, {})

    @classmethod
    def set_state(cls, user_id: int, state: Dict[str, Any]):
        cls._memory_store[user_id] = state

    @classmethod
    def clear_state(cls, user_id: int):
        if user_id in cls._memory_store:
            del cls._memory_store[user_id]
