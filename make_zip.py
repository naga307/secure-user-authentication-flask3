import os
import zipfile

root = os.path.abspath(os.path.dirname(__file__))
out = os.path.join(root, 'secure_auth_project.zip')
excludes = {'.venv', 'users.db', '__pycache__', '.git'}

with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip excluded directories
        rel_dir = os.path.relpath(dirpath, root)
        if rel_dir == '.':
            rel_dir = ''
        parts = rel_dir.split(os.sep) if rel_dir else []
        if any(p in excludes for p in parts):
            continue
        for fname in filenames:
            if fname.endswith('.pyc'):
                continue
            if fname == os.path.basename(out):
                continue
            if fname.endswith('.db') or fname.endswith('.sqlite3'):
                continue
            fullpath = os.path.join(dirpath, fname)
            arcname = os.path.join(rel_dir, fname) if rel_dir else fname
            z.write(fullpath, arcname)

print('Created ZIP:', out)
