# -*- coding: utf-8 -*-
"""
Step 6c - Minimal BGZF + tabix reader over HTTP range requests.

FinnGen releases per-phenotype summary statistics as BGZF-compressed, tabix-indexed
files (e.g. 805 MB for H7_OPTNEURITIS).  Downloading whole files for every
endpoint is wasteful, so this module reads the .tbi index and then fetches only
the compressed byte ranges that cover the queried regions.

BGZF block layout (SAM specification, section 4.1)
    [gzip header 12 B][extra field XLEN=6, SI1=66 SI2=67, BSIZE][CDATA][CRC32][ISIZE]
    BSIZE + 1 = total block size; a virtual offset is (coffset << 16) | uoffset
    where coffset indexes the block start and uoffset the uncompressed position.

tabix index layout (SAM specification, section 5.2)
    magic "TBI\\1", n_ref, format, col_seq, col_beg, col_end, meta, skip,
    l_nm, names, then per reference: n_bin, {bin, n_chunk, chunk pairs},
    n_intv, linear index.
"""
from __future__ import annotations

import gzip
import io
import struct
import ssl
import time
import urllib.error
import urllib.request
import zlib
from pathlib import Path

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) research/1.0"}

_MAGIC = b"\x1f\x8b\x08\x04"


class HttpFile:
    """Seekable read-only file object backed by HTTP range requests, with a cache."""

    def __init__(self, url: str, timeout: int = 180, block: int = 1 << 18):
        self.url = url
        self.timeout = timeout
        self.block = block
        self.pos = 0
        self._cache: dict[int, bytes] = {}
        self.size = self._head()

    def _head(self) -> int:
        req = urllib.request.Request(self.url, headers=UA, method="HEAD")
        with urllib.request.urlopen(req, timeout=self.timeout, context=CTX) as r:
            return int(r.headers.get("Content-Length", 0))

    def _fetch(self, start: int, length: int) -> bytes:
        """
        Return exactly `length` bytes from `start` (or fewer at EOF).  The
        requested span is fetched in one range request so that a BGZF block is
        never split across two cached reads.
        """
        if length <= 0:
            return b""
        end = min(self.size - 1, start + length - 1)
        last = None
        for a in range(5):
            try:
                req = urllib.request.Request(
                    self.url, headers={**UA, "Range": f"bytes={start}-{end}"})
                with urllib.request.urlopen(req, timeout=self.timeout, context=CTX) as r:
                    blob = r.read()
                if blob:
                    return blob
            except Exception as exc:  # noqa: BLE001
                last = exc
                time.sleep(1.2 * (a + 1))
        raise RuntimeError(f"range fetch failed {start}-{end}: {last}")

    def read(self, n: int = -1) -> bytes:
        if n < 0:
            n = max(0, self.size - self.pos)
        blob = self._fetch(self.pos, n)
        self.pos += len(blob)
        return blob

    def seek(self, off: int, whence: int = 0) -> int:
        self.pos = off if whence == 0 else (self.pos + off if whence == 1 else self.size + off)
        return self.pos

    def tell(self) -> int:
        return self.pos


def read_bgzf_block(f: HttpFile) -> tuple[bytes, int]:
    """Read one BGZF block; return (uncompressed payload, block start offset)."""
    start = f.tell()
    head = f.read(12)
    if len(head) < 12 or head[:4] != _MAGIC:
        return b"", start
    xlen = struct.unpack("<H", head[10:12])[0]
    extra = f.read(xlen)
    bsize = None
    i = 0
    while i + 4 <= len(extra):
        si1, si2, slen = extra[i], extra[i + 1], struct.unpack("<H", extra[i + 2:i + 4])[0]
        if si1 == 66 and si2 == 67:
            bsize = struct.unpack("<H", extra[i + 4:i + 6])[0]
        i += 4 + slen
    if bsize is None:
        return b"", start
    total = bsize + 1
    remaining = total - 12 - xlen
    body = f.read(max(0, remaining))
    try:
        return gzip.decompress(head + extra + body), start
    except Exception:  # noqa: BLE001
        try:
            return zlib.decompress(body[:-8], -15), start
        except Exception:  # noqa: BLE001
            return b"", start


def read_from_voffset(f: "HttpFile", voffset: int, end_voffset: int | None = None,
                      max_bytes: int | None = None) -> bytes:
    """
    Decompress forward from a virtual offset.

    Two stop conditions, in order of precedence:

    * `end_voffset` - stop once the *uncompressed* position has passed the end of
      the tabix chunk.  This is the correct condition and the one to use: the
      earlier version of this function stopped after a fixed number of bytes, which
      silently truncated any chunk spanning more than that many uncompressed
      bases.  A query over a large genomic window (an instrument span of tens of
      megabases) therefore returned only the first few megabases of variants and
      almost no instruments were recovered.
    * `max_bytes`   - a safety cap for callers that have no end offset.

    Bytes are fetched in ~4 MB compressed windows so a chunk costs a handful of
    range requests rather than one per BGZF block.
    """
    coff, uoff = voffset >> 16, voffset & 0xFFFF
    hard_cap = max_bytes if max_bytes is not None else (1 << 31)
    window = 4 << 20
    out = bytearray()
    raw = f._fetch(coff, min(window, max(0, f.size - coff)))
    consumed = 0
    refills = 0

    while len(out) < hard_cap:
        if consumed >= len(raw):
            # advance the compressed cursor and refill
            coff += consumed
            consumed = 0
            if coff >= f.size:
                break
            raw = f._fetch(coff, min(window, max(0, f.size - coff)))
            refills += 1
            if refills > 4000 or not raw:      # ~16 GB compressed ceiling
                break
            continue
        blk = raw[consumed:]
        if len(blk) < 18 or blk[:4] != _MAGIC:
            break
        xlen = struct.unpack("<H", blk[10:12])[0]
        extra = blk[12:12 + xlen]
        bsize = None
        i = 0
        while i + 4 <= len(extra):
            si1, si2, slen = extra[i], extra[i + 1], struct.unpack("<H", extra[i + 2:i + 4])[0]
            if si1 == 66 and si2 == 67:
                bsize = struct.unpack("<H", extra[i + 4:i + 6])[0]
            i += 4 + slen
        if bsize is None:
            break
        total = bsize + 1
        if consumed + total > len(raw):
            coff += consumed
            consumed = 0
            if coff >= f.size:
                break
            raw = f._fetch(coff, min(window, max(0, f.size - coff)))
            refills += 1
            if refills > 4000 or not raw:
                break
            continue
        block = blk[:total]
        block_end_coff = coff + consumed + total
        consumed += total
        payload = b""
        try:
            payload = gzip.decompress(block)
        except Exception:  # noqa: BLE001
            try:
                payload = zlib.decompress(block[18:-8], -15)
            except Exception:  # noqa: BLE001
                payload = b""
        if not payload:
            break
        out += payload
        # stop as soon as the compressed cursor has passed the chunk end
        if end_voffset is not None and block_end_coff > (end_voffset >> 16):
            break
    data = bytes(out)
    return data[uoff:uoff + hard_cap] if uoff < len(data) else b""


class Tabix:
    def __init__(self, data_url: str, index_url: str):
        self.data = HttpFile(data_url)
        self.names: list[str] = []
        self.bins: list[dict[int, list[tuple[int, int]]]] = []
        self.linear: list[list[int]] = []
        self._load_index(index_url)
        self._parse()

    def _load_index(self, index_url: str) -> None:
        """
        A .tbi is itself BGZF-compressed, so it is fetched whole (a few MB) and
        decompressed; the data file stays range-accessed.
        """
        cache = Path(__file__).resolve().parents[1] / "data" / "raw" / "finngen"
        cache.mkdir(parents=True, exist_ok=True)
        local = cache / (index_url.rstrip("/").split("/")[-1])
        if local.exists() and local.stat().st_size > 0:
            blob = local.read_bytes()
        else:
            last = None
            for a in range(5):
                try:
                    req = urllib.request.Request(index_url, headers=UA)
                    with urllib.request.urlopen(req, timeout=300, context=CTX) as r:
                        blob = r.read()
                    local.write_bytes(blob)
                    break
                except Exception as exc:  # noqa: BLE001
                    last = exc
                    time.sleep(1.5 * (a + 1))
            else:
                raise RuntimeError(f"index download failed: {last}")
        raw = blob
        if raw[:2] == b"\x1f\x8b":
            try:
                raw = gzip.decompress(blob)
            except Exception:  # noqa: BLE001
                raw = zlib.decompress(blob, 31)
        self._raw = raw
        self.idx = io.BytesIO(raw)

    def _parse(self) -> None:
        f = self.idx
        f.seek(0)
        if f.read(4) != b"TBI\x01":
            raise RuntimeError("not a tabix index")
        n_ref, fmt, col_seq, col_beg, col_end, meta, skip, l_nm = struct.unpack(
            "<8i", f.read(32))
        self.names = f.read(l_nm).rstrip(b"\x00").decode("utf-8", "replace").split("\x00")
        for _ in range(n_ref):
            n_bin = struct.unpack("<i", f.read(4))[0]
            bins: dict[int, list[tuple[int, int]]] = {}
            for _ in range(n_bin):
                b = struct.unpack("<I", f.read(4))[0]
                n_chunk = struct.unpack("<i", f.read(4))[0]
                chunks = [struct.unpack("<2Q", f.read(16)) for _ in range(n_chunk)]
                bins[b] = chunks
            n_intv = struct.unpack("<i", f.read(4))[0]
            lin = list(struct.unpack("<%dQ" % n_intv, f.read(8 * n_intv))) if n_intv else []
            self.bins.append(bins)
            self.linear.append(lin)

    @staticmethod
    def _reg2bins(beg: int, end: int) -> list[int]:
        """
        UCSC/tabix binning scheme: bin 0 for the whole genome, then offset 1
        (2^29), 9 (2^26), 73 (2^23), 585 (2^20) and 4681 (2^14) for the successive
        levels, each level being 8x finer than the one above.

        CRITICAL: for an interval that spans more than one bin at a given level,
        EVERY bin between the start bin and the end bin must be requested, not
        just the two boundary bins.  The earlier version of this function returned
        only the boundaries, which silently reduced a 131 Mb query to a single
        16 kb bin and was the cause of the near-zero instrument recovery in the
        Mendelian randomisation step.

        `beg`/`end` are 0-based half-open.
        """
        if end <= beg:
            end = beg + 1
        end -= 1
        bins = {0}
        for offset, shift in ((1, 26), (9, 23), (73, 20), (585, 17), (4681, 14)):
            lo = offset + (beg >> shift)
            hi = offset + (end >> shift)
            bins.update(range(lo, hi + 1))
        return sorted(bins)

    def chrom_index(self, chrom: str) -> int | None:
        for want in (chrom, chrom.replace("chr", ""), "chr" + chrom.replace("chr", "")):
            if want in self.names:
                return self.names.index(want)
        return None

    def query(self, chrom: str, start: int, end: int) -> list[str]:
        """
        Return the tab-delimited lines overlapping the 1-based inclusive range
        [start, end].  tabix bins are keyed on 0-based half-open coordinates, so
        the bin lookup uses (start-1, end) while the returned lines are filtered
        against the original 1-based interval.
        """
        ci = self.chrom_index(chrom)
        if ci is None:
            return []
        bins = self.bins[ci]
        linear = self.linear[ci]
        want = self._reg2bins(max(0, start - 1), end)
        li = max(0, start - 1) >> 14
        min_off = linear[li] if (linear and li < len(linear) and linear[li]) else 0
        chunks: list[tuple[int, int]] = []
        for b in want:
            for (c_beg, c_end) in bins.get(b, []):
                if c_end > min_off:
                    chunks.append((max(c_beg, min_off), c_end))
        chunks.sort()
        merged: list[list[int]] = []
        for beg, end_ in chunks:
            if merged and beg <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], end_)
            else:
                merged.append([beg, end_])

        out: list[str] = []
        chrom_set = {chrom, chrom.replace("chr", ""), "chr" + chrom.replace("chr", "")}
        for beg, end_ in merged:
            data = read_from_voffset(self.data, beg, end_voffset=end_)
            for ln in data.split(b"\n"):
                if not ln:
                    continue
                s = ln.decode("utf-8", "replace")
                parts = s.split("\t")
                if len(parts) < 3:
                    continue
                try:
                    pos = int(parts[1])
                except ValueError:
                    continue
                if parts[0] in chrom_set and start <= pos <= end:
                    out.append(s)
        return out


def query_snps(url_gz: str, url_tbi: str, regions: dict[str, list[tuple[int, int]]]
               ) -> dict[str, str]:
    """Return {snp_id: line} for all requested chrom:pos regions."""
    tb = Tabix(url_gz, url_tbi)
    hits: dict[str, str] = {}
    for chrom, spans in regions.items():
        for (s, e) in spans:
            for ln in tb.query(chrom, s, e):
                parts = ln.split("\t")
                if len(parts) >= 3:
                    hits[parts[2]] = ln
    return hits


if __name__ == "__main__":
    import sys
    gz = "https://storage.googleapis.com/finngen-public-data-r12/summary_stats/release/finngen_R12_H7_OPTNEURITIS.gz"
    tbi = gz + ".tbi"
    t0 = time.time()
    print("opening index ...")
    tb = Tabix(gz, tbi)
    print(f"  refs={len(tb.names)} first={tb.names[:5]} ({time.time()-t0:.1f}s)")
    # OPA1 is at 3q29; MT-ND4 is mitochondrial (not in the index)
    for chrom, start, end in [("3", 193593000, 193700000), ("1", 155000000, 155300000)]:
        t1 = time.time()
        lines = tb.query(chrom, start, end)
        print(f"  chr{chrom}:{start}-{end} -> {len(lines)} variants "
              f"({time.time()-t1:.1f}s)")
        for ln in lines[:3]:
            print("     ", ln[:150])
