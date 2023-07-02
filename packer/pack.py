import os, subprocess, zipfile, hashlib
from pathlib import Path
from dir_maker import makedirs
from typing import Optional


curdir = Path(__file__).parent
NUITKA = ['python', '-m', 'nuitka']


def getlines(f: Path) -> list[str]:
    if not f.is_file: return []
    with open(f) as f_fp:
        f_lines = [l for l in f_fp.readlines() if l]
    return f_lines

def setlines(f: Path, lines: list[str]):
    with open(f, 'w') as f_fp:
        f_fp.writelines(lines)

# https://stackoverflow.com/questions/22058048/hashing-a-file-in-python
def sha256sum(filename: Path):
    h  = hashlib.sha256()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        while n := f.readinto(mv):
            h.update(mv[:n])
    return h.hexdigest()

def nuitka_compile(file: Path, other_involved_files: Optional[list[Path]] = None):
    """other_involved_files should be all relative path to file.parent"""
    cwd = os.getcwd()
    os.chdir(file.parent)
    
    # check files and decide to build or not
    involved_files = [file.name, *other_involved_files]
    last_checksum_lines = getlines(file.parent / f'{file.stem}.build_checksums')
    last_checksum_dict = {}
    for checksum_line in last_checksum_lines:
        k, v = checksum_line.split(',', 1)
        k = k.strip(); v = v.strip()
        last_checksum_dict[k] = v
    this_checksum_dict = {i_f:sha256sum(i_f) for i_f in involved_files}
    if last_checksum_dict == this_checksum_dict:
        print(f'Skip building {file} for no relative files changed.')
        return
    else:
        this_checksum_lines = [f'{k},{v}' for k, v in this_checksum_dict.items()]
        setlines(file.parent / f'{file.stem}.build_checksums', this_checksum_lines)
    
    build_opts = getlines(file.parent / f'{file.stem}.build_opts')
    subprocess.run([*NUITKA, str(file), *build_opts])
    os.chdir(cwd)

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


os.chdir(curdir)
src_dir = curdir.parent / 'src'
nuitka_compile(src_dir / 'helper.py', ['fake_image_class.py', 'proxy_setter.py'])
subprocess.run([str(src_dir / 'hook_minimize_button' / 'cmake_build.bat'), 'x64'], shell=True)
subprocess.run([str(src_dir / 'OpenWebview2Window' / 'build.bat')], shell=True)

dist_root = curdir / 'dist'; dist_root.mkdir(exist_ok=True)
with open(curdir / 'dir_tree.dirs') as dir_tree_fp: makedirs(dist_root, dir_tree_fp.read())
rename_overwrite(curdir.parent / 'src' / 'helper.dist',
                 curdir / 'dist' / 'chore-worker')
rename_overwrite(curdir.parent / 'src' / 'hook_minimize_button' / 'dist' / 'x64',
                 curdir / 'dist' / 'chore-worker' / 'hook_minimize_button')
rename_overwrite(curdir.parent / 'src' / 'OpenWebview2Window' / 'dist',
                 curdir / 'dist' / 'chore-worker' / 'OpenWebview2Window')

zip_pack(curdir / 'dist')