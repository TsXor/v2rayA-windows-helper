import os, subprocess, zipfile
from pathlib import Path
from dir_maker import makedirs

dp0 = Path(__file__).parent

def rename_overwrite(src: Path, dst: Path):
    try:
        src.rename(dst)
    except:
        if src.is_dir():
            for sp in src.iterdir():
                dp = dst / sp.name
                rename_overwrite(sp, dp)
            src.rmdir()
        if src.is_file():
            os.replace(src, dst)

def path_rlist_files(root: Path):
    for nroot, dirs, files in os.walk(root, topdown=False):
        for name in files:
            yield Path(nroot) / name
        for name in dirs:
            yield Path(nroot) / name

def zip_pack(root: Path):
    zip_path = root.parent / f'{root.name}.zip'
    if zip_path.is_file: zip_path.unlink()
    with zipfile.ZipFile(zip_path, 'w') as archive:
        for file in path_rlist_files(root):
            archive.write(file, file.relative_to(root))

os.chdir(dp0.parent / 'src')
subprocess.run(['nuitka_build.py'], shell=True)
subprocess.run(['hook_minimize_button\cmake_build.bat', 'x64'], shell=True)

dist_root = dp0 / 'dist'; dist_root.mkdir(exist_ok=True)
with open(dp0 / 'dir_tree.dirs') as dir_tree_fp: makedirs(dist_root, dir_tree_fp.read())
rename_overwrite(dp0.parent / 'src' / 'open_webview.dist', dp0 / 'dist' / 'chore-worker')
rename_overwrite(dp0.parent / 'src' / 'helper.dist', dp0 / 'dist' / 'chore-worker')
rename_overwrite(dp0.parent / 'src' / 'hook_minimize_button' / 'dist' / 'Release', dp0 / 'dist' / 'chore-worker' / 'hook_minimize_button')

zip_pack(dp0 / 'dist')