import os, subprocess, zipfile, hashlib
from pathlib import Path
import traceback
from shutil import rmtree
from dir_maker import makedirs
from typing import Optional, Union
try:
    from colorama import just_fix_windows_console
    just_fix_windows_console()
except ImportError: pass


curdir = Path(__file__).parent
NUITKA = ['python', '-m', 'nuitka']


def print_styled(
        *args,
        display_mode: Union[str, int] = '',
        color_fg: Union[str, int] = '',
        color_bg: Union[str, int] = '',
        **kwargs
):
    sep = kwargs.get('sep', " ")
    print(f'\033[{display_mode};{color_fg};{color_bg}m{sep.join(args)}\033[0m')

def log_process(*args, **kwargs):
    kwargs['color_fg'] = 36
    print_styled('-->>', *args, **kwargs)

def getlines(f: Path) -> list[str]:
    if not f.is_file(): return []
    with open(f) as f_fp:
        f_lines = [l.strip() for l in f_fp.readlines() if l]
    return f_lines

def setlines(f: Path, lines: list[str]):
    with open(f, 'w') as f_fp:
        f_fp.writelines([l+'\n' for l in lines])

# https://stackoverflow.com/questions/22058048/hashing-a-file-in-python
def sha256sum(filename: Path):
    h  = hashlib.sha256()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        while n := f.readinto(mv):
            h.update(mv[:n])
    return h.hexdigest()

def nuitka_build(file: Path, other_involved_files: Optional[list[Path]] = None):
    """other_involved_files should be all relative path to file.parent"""
    cwd = os.getcwd()
    os.chdir(file.parent)
    build_opts_path = file.parent / f'{file.stem}.build_opts'
    build_checksums_path = file.parent / f'{file.stem}.build_checksums'
    
    if (file.parent / f'{file.stem}.dist').is_dir():
        # check files and decide to build or not
        involved_files = [file.name, build_opts_path.name, *other_involved_files]
        last_checksum_lines = getlines(file.parent / f'{file.stem}.build_checksums')
        last_checksum_dict = {}
        for checksum_line in last_checksum_lines:
            k, v = checksum_line.split(',', 1)
            k = k.strip(); v = v.strip()
            last_checksum_dict[k] = v
        this_checksum_dict = {i_f:sha256sum(Path(i_f).resolve()) for i_f in involved_files}
        if last_checksum_dict == this_checksum_dict:
            print(f'Skip building {file} for no relative files changed.')
            return
        else:
            this_checksum_lines = [f'{k},{v}' for k, v in this_checksum_dict.items()]
            setlines(build_checksums_path, this_checksum_lines)
    
    build_opts = getlines(build_opts_path)
    subprocess.run([*NUITKA, str(file), *build_opts], check=True)
    os.chdir(cwd)

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

def retry_until_success(fn):
    while True:
        try:
            fn()
            break
        except BaseException as exc:
            print('An error happened:')
            traceback.print_exc()
            input('Press ENTER to retry. ')

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


os.chdir(curdir)
src_dir = curdir.parent / 'src'

log_process('Building helper ...')
nuitka_build(src_dir / 'helper.py', ['fake_image_class.py', 'proxy_setter.py'])
log_process('finished.')

log_process('Building hook_minimize_button ...')
subprocess.run([str(src_dir / 'hook_minimize_button' / 'cmake_build.bat'), 'x64'], shell=True, check=True)
log_process('finished.')

log_process('Building OpenWebview2Window ...')
subprocess.run([str(src_dir / 'OpenWebview2Window' / 'build.bat')], shell=True, check=True)
log_process('finished.')

log_process('Assembling dist ...')
dist_root = curdir / 'dist'
retry_until_success(lambda:
    rmtree(dist_root)
)
dist_root.mkdir(exist_ok=True)
with open(curdir / 'dir_tree.dirs') as dir_tree_fp: makedirs(dist_root, dir_tree_fp.read())
retry_until_success(lambda:
    copy_tree_overwrite(curdir.parent / 'src' / 'helper.dist',
                        curdir / 'dist' / 'chore-worker')
)
retry_until_success(lambda:
    copy_tree_overwrite(curdir.parent / 'src' / 'hook_minimize_button' / 'dist' / 'x64',
                        curdir / 'dist' / 'chore-worker' / 'hook_minimize_button')
)
retry_until_success(lambda:
    copy_tree_overwrite(curdir.parent / 'src' / 'OpenWebview2Window' / 'x64' / 'Release',
                        curdir / 'dist' / 'chore-worker' / 'OpenWebview2Window')
)
retry_until_success(lambda:
    copy_tree_overwrite(curdir.parent / 'res',
                        curdir / 'dist' / 'chore-worker')
)
log_process('finished.')

log_process('Packing dist into zip ...')
zip_pack(curdir / 'dist')
log_process('finished.')