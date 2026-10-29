import dis
import marshal
import sys

def decompile_pyc(pyc_path, out_path):
    with open(pyc_path, "rb") as f:
        # Magic number + header (16 bytes in Python 3.7+)
        f.seek(16)
        code = marshal.load(f)
    
    with open(out_path, "w", encoding="utf-8") as out:
        out.write(f"=== DISASSEMBLY OF {pyc_path} ===\n")
        out.write(f"co_consts:\n")
        for i, c in enumerate(code.co_consts):
            out.write(f"  [{i}]: {repr(c)[:300]}\n")
        out.write(f"\nco_names:\n")
        for i, n in enumerate(code.co_names):
            out.write(f"  [{i}]: {n}\n")
        out.write(f"\nco_varnames:\n")
        for i, v in enumerate(code.co_varnames):
            out.write(f"  [{i}]: {v}\n")
        out.write("\n--- DIS ---\n")
        dis.dis(code, file=out)
        
        # Also disassemble child code objects
        for const in code.co_consts:
            if hasattr(const, "co_code"):
                out.write(f"\n=== CHILD CODE OBJECT: {const.co_name} ===\n")
                out.write("co_consts:\n")
                for i, c in enumerate(const.co_consts):
                    out.write(f"  [{i}]: {repr(c)[:300]}\n")
                out.write("co_names:\n")
                for i, n in enumerate(const.co_names):
                    out.write(f"  [{i}]: {n}\n")
                out.write("co_varnames:\n")
                for i, v in enumerate(const.co_varnames):
                    out.write(f"  [{i}]: {v}\n")
                dis.dis(const, file=out)

decompile_pyc("core/__pycache__/urls.cpython-314.pyc", "scratch/urls_dis.txt")
decompile_pyc("core/__pycache__/views.cpython-314.pyc", "scratch/views_dis.txt")
decompile_pyc("core/__pycache__/career_resources.cpython-314.pyc", "scratch/career_resources_dis.txt")
decompile_pyc("core/__pycache__/tests.cpython-314.pyc", "scratch/tests_dis.txt")
print("Decompiled all successfully.")

