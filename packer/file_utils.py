from shutil import rmtree
from pathlib import Path
import os, zipfile

def rename_tree_overwrite(src: Path, dst: Path):
    try:
        src.rename(dst)
    except:
        if src.is_dir():
            for sp in src.iterdir():
                dp = dst / sp.name
                rename_tree_overwrite(sp, dp)
            src.rmdir()
        elif src.is_file():
            os.replace(src, dst)

def copy_tree_overwrite(src: Path, dst: Path):
    if src.is_dir():
        dst.mkdir(exist_ok=True)
        for sp in src.iterdir():
            dp = dst / sp.name
            copy_tree_overwrite(sp, dp)
    elif src.is_file():
        dst.write_bytes(src.read_bytes())

def path_rlist_files(root: Path):
    for nroot, dirs, files in os.walk(root, topdown=False):
        for name in files:
            yield Path(nroot) / name
        for name in dirs:
            yield Path(nroot) / name

def zip_pack(root: Path):
    zip_path = root.parent / f'{root.name}.zip'
    if zip_path.is_file(): zip_path.unlink()
    with zipfile.ZipFile(zip_path, 'w') as archive:
        for file in path_rlist_files(root):
            archive.write(file, file.relative_to(root))
