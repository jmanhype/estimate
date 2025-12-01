from pathlib import Path

model_files = {
    "src/models/user.py": ["Project", "Subscription"],
    "src/models/project.py": ["UserProfile", "ProjectPhoto", "ShoppingList"],
    "src/models/subscription.py": ["UserProfile"],
    "src/models/photo.py": ["Project"],
    "src/models/shopping_list.py": ["Project"],
}

for file_path, types_needed in model_files.items():
    p = Path(file_path)
    if not p.exists():
        continue

    content = p.read_text()

    # Check if already has TYPE_CHECKING
    if "TYPE_CHECKING" in content:
        continue

    # Find the position after __future__ imports
    lines = content.split("\n")
    insert_pos = 0
    for i, line in enumerate(lines):
        if line.startswith("from __future__"):
            insert_pos = i + 1
            break
        elif line.startswith("from ") or line.startswith("import "):
            insert_pos = i
            break

    # Create TYPE_CHECKING import block
    type_imports = "\n".join([f"    {t}" for t in types_needed])
    type_checking_block = f"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
{type_imports}
"""

    # Insert it
    lines.insert(insert_pos + 1, type_checking_block)
    p.write_text("\n".join(lines))

print("Fixed imports")
