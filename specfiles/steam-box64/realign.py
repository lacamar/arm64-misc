# Pad a 4K-aligned aarch64 ELF so it loads on 16K-page kernels; addresses stay the same.
import struct, sys

PAGE = 0x4000
src, dst = sys.argv[1:3]
b = bytearray(open(src, "rb").read())
phoff, shoff = struct.unpack_from("<QQ", b, 0x20)
phentsize, phnum, shentsize, shnum = struct.unpack_from("<HHHH", b, 0x36)

ph = [list(struct.unpack_from("<IIQQQQQQ", b, phoff + i * phentsize)) for i in range(phnum)]
loads = sorted((p for p in ph if p[0] == 1), key=lambda p: p[2])
inserts, shift = [], 0
for prev, p in zip(loads, loads[1:]):
    assert (prev[3] + prev[6] + PAGE - 1) // PAGE <= p[3] // PAGE, "segments share a page"
    pad = (p[3] - (p[2] + shift)) % PAGE
    if pad:
        inserts.append((p[2], pad))
        shift += pad

def moved(off):
    return off + sum(n for at, n in inserts if off >= at)

for p in ph:
    if p[0] == 1:
        p[7] = PAGE
    if p[2] or p[0] == 1:
        p[2] = moved(p[2])
for i, p in enumerate(ph):
    struct.pack_into("<IIQQQQQQ", b, phoff + i * phentsize, *p)
for i in range(shnum):
    o = shoff + i * shentsize + 0x18
    (off,) = struct.unpack_from("<Q", b, o)
    if off:
        struct.pack_into("<Q", b, o, moved(off))
struct.pack_into("<Q", b, 0x28, moved(shoff))
for at, n in reversed(inserts):
    b[at:at] = bytes(n)
open(dst, "wb").write(b)
