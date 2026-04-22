import os
from dotenv import load_dotenv
from mem0 import MemoryClient
load_dotenv()

memory = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))
all_memories = memory.get_all(filters={"user_id": "mnemosyne_demo"})

if isinstance(all_memories, dict):
    mem_list = all_memories.get("results", [])
else:
    mem_list = all_memories

for m in mem_list:
    memory.delete(m["id"])

print(f"Cleared {len(mem_list)} memories. Clean slate.")
