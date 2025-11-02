"""Add leaderboard data to room static data files.

Usage:
    python3 scripts/add_leaderboard_to_rooms.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
STATIC_DATA_DIR = PROJECT_ROOT / "web" / "static_data"

# Define leaderboard data for each room
LEADERBOARDS = {
    "room1": [
        {"model": "Claude-3.5-Sonnet", "turns": 32},
        {"model": "GPT-4o", "turns": 45},
        {"model": "Gemini 2.5 Pro", "turns": 46},
    ],
    "room2": [
        {"model": "Claude-3.5-Sonnet", "turns": 28},
        {"model": "GPT-4o", "turns": 38},
        {"model": "Gemini 2.5 Pro", "turns": 42},
    ],
    "room3": [
        {"model": "Claude-3.5-Sonnet", "turns": 35},
        {"model": "GPT-4o", "turns": 40},
        {"model": "Gemini 2.5 Pro", "turns": 48},
    ],
}


def update_room_file(room_name: str) -> None:
    """Update a room's static data file to include leaderboard."""
    file_path = STATIC_DATA_DIR / f"{room_name}.js"
    
    if not file_path.exists():
        print(f"Warning: {room_name}.js not found, skipping...")
        return
    
    # Read the file
    with file_path.open("r", encoding="utf-8") as f:
        content = f.read()
    
    # Extract the JSON part
    # Pattern: (window.__VisEscapeGraphs = window.__VisEscapeGraphs || {})['roomN'] = {JSON};
    pattern = rf"\(window\.__VisEscapeGraphs = window\.__VisEscapeGraphs \|\| {{}}\)\['{room_name}'\] = ({{.*}});"
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print(f"Warning: Could not parse {room_name}.js, skipping...")
        return
    
    json_str = match.group(1)
    
    # Parse JSON
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"Warning: Could not parse JSON in {room_name}.js: {e}, skipping...")
        return
    
    # Add leaderboard if not exists or update it
    if room_name in LEADERBOARDS:
        data["leaderboard"] = LEADERBOARDS[room_name]
        print(f"Added leaderboard to {room_name}")
    else:
        print(f"Warning: No leaderboard data defined for {room_name}, skipping...")
        return
    
    # Re-serialize JSON
    new_json_str = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    
    # Reconstruct the file content
    new_content = (
        f"(window.__VisEscapeGraphs = window.__VisEscapeGraphs || {{}})['{room_name}'] = {new_json_str};\n"
    )
    
    # Write back
    with file_path.open("w", encoding="utf-8") as f:
        f.write(new_content)
    
    print(f"Updated {room_name}.js successfully")


def main() -> None:
    """Update all room files with leaderboard data."""
    for room_name in ["room1", "room2", "room3"]:
        update_room_file(room_name)


if __name__ == "__main__":
    main()

