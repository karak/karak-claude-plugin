import os, sys, time, stat
from concurrent.futures import ThreadPoolExecutor
REPARSE=0x400; RECALL=0x400000; OFFLINE=0x1000; SPARSE=0x200
def walk(root):
    total=0; n=0; skipped=0
    stack=[root]
    while stack:
        d=stack.pop()
        try:
            with os.scandir(d) as it:
                for e in it:
                    try:
                        st=e.stat(follow_symlinks=False)
                    except OSError:
                        skipped+=1; continue
                    a=st.st_file_attributes
                    if a & REPARSE:
                        skipped+=1; continue
                    if e.is_dir(follow_symlinks=False):
                        stack.append(e.path)
                    else:
                        n+=1
                        if a & (RECALL|OFFLINE): continue
                        total+=st.st_size
        except OSError:
            skipped+=1
    return total,n,skipped
home=os.path.expanduser('~')
targets=[p.format(h=home) for p in sys.argv[1:]]
t0=time.time()
with ThreadPoolExecutor(8) as ex:
    for p,(tot,n,sk) in zip(targets, ex.map(walk,targets)):
        print(f"{tot/2**30:7.2f} GB {n:8d} files skip={sk:5d} {p}")
print(f"elapsed {time.time()-t0:.1f}s")
