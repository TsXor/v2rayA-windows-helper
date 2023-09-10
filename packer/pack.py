import os, subprocess, hashlib
from pathlib import Path
import traceback
import file_utils
from dir_maker import makedirs
from typing import Optional, Union

try:
    from colorama import just_fix_windows_console
    just_fix_windows_console()
except ImportError: pass


curdir = Path(__file__).parent
NUITKA = ['python', '-m', 'nuitka']


class chdir_ctx:
    def __init__(self, path = None):
        self.original_path = os.getcwd()
        self.new_path = os.getcwd() if path is None else Path(path)
    def __enter__(self):
        os.chdir(self.new_path)
    def __exit__(self, exc_type, exc_value, exc_tb):
        os.chdir(self.original_path)

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
    with chdir_ctx(file.parent):
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

def cmake_build(folder: Path, generator: str, build_dir_name: str = 'cmake-build-pyscript'):
    build_path = folder / 'build' / build_dir_name
    build_path.mkdir(parents=True, exist_ok=True)
    with chdir_ctx(build_path):
        subprocess.run(['cmake', '-G', generator, str(folder)], check=True)
        subprocess.run(['cmake', '--build', '.', '--target', 'install', '--config', 'Release'], check=True)

def cython_build(file: Path):
    with chdir_ctx(file.parent):
        subprocess.run(['cythonize', '-3', '-i', str(file)], check=True)

def retry_until_success(fn):
    while True:
        try:
            fn()
            break
        except BaseException:
            print('An error happened:')
            traceback.print_exc()
            input('Press ENTER to retry. ')


os.chdir(curdir)
root_dir = curdir.parent
src_dir = root_dir / 'src'
res_dir = root_dir / 'res'
glued_dir = root_dir / 'glued'
dist_root = curdir / 'dist'

#log_process('Building extensions ...')
#cython_build(src_dir / 'cext' / 'get_process_hwnd.pyx')
#log_process('finished.')

log_process('Building helper ...')
nuitka_build(src_dir / 'helper.py', ['fake_image_class.py', 'proxy_setter.py'])
log_process('finished.')

log_process('Building OpenWebview2Window ...')
cmake_build(glued_dir / 'OpenWebview2Window', 'MinGW Makefiles')
log_process('finished.')

log_process('Assembling dist ...')
retry_until_success(lambda:
    file_utils.rmtree(dist_root)
)
dist_root.mkdir(exist_ok=True)
with open(curdir / 'dir_tree.dirs') as dir_tree_fp: makedirs(dist_root, dir_tree_fp.read())
retry_until_success(lambda:
    file_utils.copy_tree_overwrite(
        src_dir / 'helper.dist',
        dist_root / 'chore-worker'
    )
)
retry_until_success(lambda:
    file_utils.copy_tree_overwrite(
        glued_dir / 'OpenWebview2Window' / 'dist' / 'bin' / 'x64',
        dist_root / 'chore-worker' / 'OpenWebview2Window'
    )
)
retry_until_success(lambda:
    file_utils.copy_tree_overwrite(
        res_dir,
        dist_root / 'chore-worker'
    )
)
log_process('finished.')

log_process('Packing dist into zip ...')
file_utils.zip_pack(dist_root)
log_process('finished.')
