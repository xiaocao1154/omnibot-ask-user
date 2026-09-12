#!/usr/bin/env python3
"""Verify ask-user skill installation."""
import os, sys, re

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_MD = os.path.join(SKILL_DIR, "SKILL.md")
README = os.path.join(SKILL_DIR, "..", "..", "README.md")
GEN_FORM = os.path.join(SKILL_DIR, "scripts", "gen_form.py")

def check(path, name):
    if not os.path.exists(path):
        print(f"  ❌ {name}: {path}")
        return False
    size = os.path.getsize(path)
    print(f"  ✅ {name} ({size:,} bytes)")
    return True

print("=" * 50)
print("  ask-user Skill Verification")
print("=" * 50)

ok = True
print("\n[1/4] SKILL.md ...")
ok &= check(SKILL_MD, "SKILL.md")

print("\n[2/4] Frontmatter ...")
if os.path.exists(SKILL_MD):
    with open(SKILL_MD) as f:
        content = f.read()
    for field in ["name:", "description:"]:
        found = field in content
        print(f"  {'✅' if found else '❌'} {field.rstrip(':')}")
        ok &= found

print("\n[3/4] Scripts ...")
ok &= check(GEN_FORM, "gen_form.py")

print("\n[4/4] README.md ...")
ok &= check(README, "README.md")

print("\n" + "=" * 50)
if ok:
    print("  ✅ All checks passed!")
else:
    print("  ⚠️  Some files missing.")
print("=" * 50)
sys.exit(0 if ok else 1)
