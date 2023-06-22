from pathlib import Path

SPACE = ' '

def makedirs(root: Path, config: str, space_per_indent=4):
    config = config.replace('\t', SPACE*space_per_indent)
    lines = config.split('\n')
    parts = []
    for i, line in enumerate(lines):
        n_spaces = 0
        while line[n_spaces] == ' ': n_spaces += 1
        name = line[n_spaces:]
        
        n_indents, left = divmod(n_spaces, space_per_indent)
        if left: raise ValueError('Inappropriate indents!')
        
        l_parts = len(parts)
        if n_indents == l_parts: parts.append(name)
        elif n_indents < l_parts: parts = parts[:n_indents]; parts.append(name)
        else: raise ValueError(f'Inappropriate directory tree at line {i+1}!')
        
        root.joinpath(*parts).mkdir(parents=True, exist_ok=True)

if __name__ == '__main__':
    import sys
    with open(sys.argv[2]) as config_fp:
        makedirs(Path(sys.argv[1]), config_fp.read())