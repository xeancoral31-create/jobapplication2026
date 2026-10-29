"""Patch base.html modal tab buttons to use SVG icons instead of emoji."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("templates/base.html", "r", encoding="utf-8") as f:
    content = f.read()

nl = '\n'  # file uses LF

old_tech = (
    'modal-tab-tech" style="padding:0.45rem 0.85rem; border-radius:8px; font-size:0.8rem; font-weight:700; cursor:pointer; background:rgba(56, 189, 248, 0.15); border:1px solid rgba(56, 189, 248, 0.4); color:#38bdf8;">' + nl +
    '          \U0001f4bb Software Engineer' + nl +
    '        </button>' + nl +
    '        <button type="button" onclick="modalSwitchResume(\'design\')" id="modal-tab-design" style="padding:0.45rem 0.85rem; border-radius:8px; font-size:0.8rem; font-weight:700; cursor:pointer; background:rgba(255, 255, 255, 0.04); border:1px solid rgba(255, 255, 255, 0.1); color:#94a3b8;">' + nl +
    '          \U0001f3a8 UI/UX Designer' + nl +
    '        </button>' + nl +
    '        <button type="button" onclick="modalSwitchResume(\'manager\')" id="modal-tab-manager" style="padding:0.45rem 0.85rem; border-radius:8px; font-size:0.8rem; font-weight:700; cursor:pointer; background:rgba(255, 255, 255, 0.04); border:1px solid rgba(255, 255, 255, 0.1); color:#94a3b8;">' + nl +
    '          \U0001f680 Tech Lead &amp; Manager' + nl +
    '        </button>'
)

new_tech = (
    'modal-tab-tech" style="padding:0.45rem 0.85rem; border-radius:8px; font-size:0.8rem; font-weight:700; cursor:pointer; background:rgba(56, 189, 248, 0.15); border:1px solid rgba(56, 189, 248, 0.4); color:#38bdf8; display:inline-flex; align-items:center; gap:0.35rem;">' + nl +
    '          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>' + nl +
    '          Software Engineer' + nl +
    '        </button>' + nl +
    '        <button type="button" onclick="modalSwitchResume(\'design\')" id="modal-tab-design" style="padding:0.45rem 0.85rem; border-radius:8px; font-size:0.8rem; font-weight:700; cursor:pointer; background:rgba(255, 255, 255, 0.04); border:1px solid rgba(255, 255, 255, 0.1); color:#94a3b8; display:inline-flex; align-items:center; gap:0.35rem;">' + nl +
    '          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="10" r="3"/><path d="M7 20.662V19a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v1.662"/></svg>' + nl +
    '          UI/UX Designer' + nl +
    '        </button>' + nl +
    '        <button type="button" onclick="modalSwitchResume(\'manager\')" id="modal-tab-manager" style="padding:0.45rem 0.85rem; border-radius:8px; font-size:0.8rem; font-weight:700; cursor:pointer; background:rgba(255, 255, 255, 0.04); border:1px solid rgba(255, 255, 255, 0.1); color:#94a3b8; display:inline-flex; align-items:center; gap:0.35rem;">' + nl +
    '          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>' + nl +
    '          Tech Lead &amp; Manager' + nl +
    '        </button>'
)

# Also fix the Interview Mastery modal button emoji
old_interview_btn = '\U0001f39e Interview Mastery'
new_interview_btn = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg> Interview Mastery'

# Find and replace
found1 = old_tech in content
if found1:
    content = content.replace(old_tech, new_tech)
    print("SUCCESS: Replaced modal resume emoji buttons with SVG.")
else:
    print(f"WARNING: Could not find tech modal block. Emoji at positions:")
    for emoji in ['\U0001f4bb', '\U0001f3a8', '\U0001f680']:
        idx = content.find(emoji)
        print(f"  {repr(emoji)} at {idx}")

# Also replace any standalone emoji in base.html career resource modal area
# Replace 💡 in the interview mastery modal action footer
old_tip = '          \U0001f4a1'
new_tip = '          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>'

with open("templates/base.html", "w", encoding="utf-8") as f:
    f.write(content)
print("Written to templates/base.html")
