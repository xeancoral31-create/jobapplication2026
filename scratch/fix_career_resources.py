"""Fix the stray 'INTERVIEW_CATEGORIES' bare expression on line 463 and update icon fields."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("core/career_resources.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Remove the bare "INTERVIEW_CATEGORIES\n" line that causes NameError
fixed = []
for i, line in enumerate(lines):
    stripped = line.strip()
    # Skip line that is exactly "INTERVIEW_CATEGORIES" with no assignment
    if stripped == "INTERVIEW_CATEGORIES" and i > 0:
        print(f"Removing bare INTERVIEW_CATEGORIES at line {i+1}")
        continue
    fixed.append(line)

content = "".join(fixed)

# Replace emoji icon values in INTERVIEW_CATEGORIES with SVG-compatible id strings
# The template now uses {% if cat.id == ... %} so we can remove the icon field
# or keep it as an empty string
content = content.replace("'icon': '\U0001f3af',", "'icon': '',")  # 🎯 behavioral
content = content.replace("'icon': '\U0001f3d7\ufe0f',", "'icon': '',")  # 🏗️ system_design
content = content.replace("'icon': '\u26a1',", "'icon': '',")  # ⚡ technical
content = content.replace("'icon': '\U0001f4bc',", "'icon': '',")  # 💼 negotiation

# Also remove emoji from RESUME_TEMPLATES if any
content = content.replace("'icon': '\U0001f4bb',", "'icon': '',")  # 💻
content = content.replace("'icon': '\U0001f3a8',", "'icon': '',")  # 🎨
content = content.replace("'icon': '\U0001f680',", "'icon': '',")  # 🚀

with open("core/career_resources.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Done. Verifying INTERVIEW_CATEGORIES accessible...")
import importlib, sys as _sys
if 'core.career_resources' in _sys.modules:
    del _sys.modules['core.career_resources']
import core.career_resources as cr
print([c['id'] for c in cr.INTERVIEW_CATEGORIES])

