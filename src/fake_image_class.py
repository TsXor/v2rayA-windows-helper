'''
Avoid importing PIL when using pystray.
Warning:
    1. You should save the image as an ico file.
    2. It is only designed for windows implementation of pystray.
    3. Instead of permitted usage of PIL.Image.open, you should give a pathlib.Path for parameter fp.
'''

from pathlib import Path
from io import BufferedWriter

class FakeImage:
    def __init__(self, fp: Path, *args) -> None:
        if not isinstance(fp, Path): raise ValueError
        if not fp.suffix.lower() == '.ico': raise ValueError
        self.fp = fp

    @classmethod
    def open(cls, *args):
        return cls(*args)
    
    def save(self, fp: BufferedWriter, *args, **kwargs) -> None:
        if not isinstance(fp, BufferedWriter): raise ValueError
        with open(self.fp, 'rb') as FI_fp: fp.write(FI_fp.read())