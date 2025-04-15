import importlib
import io
import os
from pathlib import Path

class Problem(object):
    @classmethod
    def default_input_file_path(cls) -> Path:
        # https://stackoverflow.com/a/54142935
        m = importlib.import_module(cls.__module__)
        return Path(m.__file__).parent / "input.txt"
    
    @classmethod
    def from_path(cls, p: os.PathLike) -> "Problem":
        return cls.from_file(Path(p).open("r"))
    
    @classmethod
    def from_file(cls, f: io.TextIOWrapper) -> "Problem":
        return cls.from_str(f.read())
    
    @classmethod
    def from_str(cls, input: str) -> "Problem":
        raise NotImplemented