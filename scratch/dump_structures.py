import marshal
import pprint
import inspect

with open("core/__pycache__/career_resources.cpython-314.pyc", "rb") as f:
    f.seek(16)
    code = marshal.load(f)

mod_dict = {}
exec(code, mod_dict)

print("Keys in mod_dict:", [k for k in mod_dict.keys() if not k.startswith("__")])

with open("scratch/dumped_career_resources.py", "w", encoding="utf-8") as out:
    out.write('"""core/career_resources.py — Real ATS Resume Templates & Interview Mastery Content."""\n')
    out.write('import io\nimport zipfile\n\n')
    
    out.write('RESUME_TEMPLATES = ')
    pprint.pprint(mod_dict['RESUME_TEMPLATES'], stream=out, width=120)
    out.write('\n\n')
    
    out.write('INTERVIEW_CATEGORIES = ')
    pprint.pprint(mod_dict['INTERVIEW_CATEGORIES'], stream=out, width=120)
    out.write('\n\n')

print("Dumped data structures.")

