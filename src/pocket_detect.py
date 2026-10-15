# -*- coding: utf-8 -*-
"""
Step 4c - Blind pocket detection (LIGSITE-style), vectorised.

Algorithm (Hendlich 1997 LIGSITE; Brady & Stouten 2000 Pass)
    The protein is mapped onto a cubic grid.  A grid point is a "protein point"
    if a 1.4 A probe placed there would clash with a heavy atom (distance <=
    r_vdW + r_probe).  For every solvent point the number of
    protein-solvent-protein (PSP) events is counted along 13 scan directions
    (3 axes, 6 face diagonals, 4 body diagonals).  Solvent points with
    PSP >= threshold are clustered by 6-connectivity; the largest clusters are
    the candidate binding pockets.

Implementation note: the PSP scan is expressed as a vectorised cumulative-sum
difference along each direction, so a 100^3 grid is processed in milliseconds
instead of the ~10^7 Python iterations a naive triple loop would need.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np

VDW = {"C": 1.70, "N": 1.55, "O": 1.52, "S": 1.80, "P": 1.80, "F": 1.47,
       "CL": 1.75, "BR": 1.85, "I": 1.98, "SE": 1.90, "H": 1.20}
DEFAULT_VDW = 1.70

DIRECTIONS = [
    (1, 0, 0), (0, 1, 0), (0, 0, 1),                       # axes
    (1, 1, 0), (1, -1, 0), (1, 0, 1), (1, 0, -1),
    (0, 1, 1), (0, 1, -1),                                  # face diagonals
    (1, 1, 1), (1, 1, -1), (1, -1, 1), (-1, 1, 1),          # body diagonals
]


def read_heavy_atoms(pdb: Path) -> tuple[np.ndarray, np.ndarray]:
    coords, radii = [], []
    for ln in pdb.read_text(errors="replace").splitlines():
        if not ln.startswith(("ATOM", "HETATM")):
            continue
        name = ln[12:16].strip()
        el = (ln[76:78].strip() or name[:1]).upper()
        if el == "H":
            continue
        try:
            coords.append([float(ln[30:38]), float(ln[38:46]), float(ln[46:54])])
        except ValueError:
            continue
        radii.append(VDW.get(el, DEFAULT_VDW))
    return np.array(coords, dtype=float), np.array(radii, dtype=float)


def _cum_forward(a: np.ndarray, axis: int) -> np.ndarray:
    """True where any earlier index along `axis` (strictly before) is True."""
    c = np.cumsum(a, axis=axis) > 0
    out = np.zeros_like(a, dtype=bool)
    sl_dst = [slice(None)] * a.ndim
    sl_src = [slice(None)] * a.ndim
    sl_dst[axis] = slice(1, None)
    sl_src[axis] = slice(None, -1)
    out[tuple(sl_dst)] = c[tuple(sl_src)]
    return out


def _cum_backward(a: np.ndarray, axis: int) -> np.ndarray:
    """True where any later index along `axis` (strictly after) is True."""
    rev = np.flip(a, axis=axis)
    c = np.cumsum(rev, axis=axis) > 0
    c = np.flip(c, axis=axis)
    out = np.zeros_like(a, dtype=bool)
    sl_dst = [slice(None)] * a.ndim
    sl_src = [slice(None)] * a.ndim
    sl_dst[axis] = slice(None, -1)
    sl_src[axis] = slice(1, None)
    out[tuple(sl_dst)] = c[tuple(sl_src)]
    return out


def _cum_forward_plane(a: np.ndarray, ax1: int, ax2: int,
                       sign: int) -> np.ndarray:
    """
    True where any strictly-earlier point along the (ax1, ax2) plane diagonal is
    True.  `sign` = +1 walks (i, i), -1 walks (i, -i).
    """
    b = a if sign > 0 else np.flip(a, axis=ax2)
    c = np.maximum.accumulate(b.astype(np.int8), axis=ax1)
    out = np.zeros_like(a, dtype=bool)
    sl_dst = [slice(None)] * a.ndim
    sl_src = [slice(None)] * a.ndim
    sl_dst[ax1] = slice(1, None)
    sl_src[ax1] = slice(None, -1)
    o = out
    tmp = np.zeros_like(b, dtype=bool)
    tmp[tuple(sl_dst)] = c[tuple(sl_src)] > 0
    o = tmp if sign > 0 else np.flip(tmp, axis=ax2)
    return o


def _cum_backward_plane(a: np.ndarray, ax1: int, ax2: int,
                        sign: int) -> np.ndarray:
    b = a if sign > 0 else np.flip(a, axis=ax2)
    rev = np.flip(b, axis=ax1)
    c = np.maximum.accumulate(rev.astype(np.int8), axis=ax1)
    c = np.flip(c, axis=ax1)
    tmp = np.zeros_like(b, dtype=bool)
    sl_dst = [slice(None)] * b.ndim
    sl_src = [slice(None)] * b.ndim
    sl_dst[ax1] = slice(None, -1)
    sl_src[ax1] = slice(1, None)
    tmp[tuple(sl_dst)] = c[tuple(sl_src)] > 0
    return tmp if sign > 0 else np.flip(tmp, axis=ax2)


def _psp_along(occ: np.ndarray, direction: tuple[int, int, int]) -> np.ndarray:
    """
    Vectorised PSP count along one scan direction.  A solvent point scores when a
    protein point lies on both sides of it along the scan line.
    """
    dx, dy, dz = direction
    nz = [abs(dx), abs(dy), abs(dz)].count(1)
    n_active = sum(1 for c in (dx, dy, dz) if c)
    if n_active == 1:
        axis = [i for i, c in enumerate((dx, dy, dz)) if c][0]
        fwd = _cum_forward(occ, axis)
        bwd = _cum_backward(occ, axis)
        return (fwd & bwd) & (~occ)
    if n_active == 2:
        ax1 = [i for i, c in enumerate((dx, dy, dz)) if c][0]
        ax2 = [i for i, c in enumerate((dx, dy, dz)) if c][1]
        s2 = 1 if (dy if ax2 == 1 else dz) > 0 else -1
        fwd = _cum_forward_plane(occ, ax1, ax2, s2)
        bwd = _cum_backward_plane(occ, ax1, ax2, s2)
        return (fwd & bwd) & (~occ)
    # ---------------------------------------------------------- body diagonal
    # Every grid point lies on exactly one diagonal of the form
    # (i0 + t, j0 + t, k0 + t) with t >= 0, indexed by (i0 - j0, k0).  The
    # diagonals are gathered with a sort, so the PSP walk is one cumulative sum
    # over the diagonal axis.
    inv = [i for i, c in enumerate((dx, dy, dz)) if c == -1]
    a = occ
    for ax in inv:
        a = np.flip(a, axis=ax)

    def _gather(vol: np.ndarray):
        """Group grid points into body diagonals; return (diagonals, valid, ...)."""
        nx_, ny_, nz_ = vol.shape
        i_flat = np.broadcast_to(np.arange(nx_)[:, None, None], vol.shape).ravel()
        j_flat = np.broadcast_to(np.arange(ny_)[None, :, None], vol.shape).ravel()
        k_flat = np.broadcast_to(np.arange(nz_)[None, None, :], vol.shape).ravel()
        m_flat = np.minimum(np.minimum(i_flat, j_flat), k_flat)
        i0_flat = i_flat - m_flat
        j0_flat = j_flat - m_flat
        keys, inv_idx = np.unique(np.stack([i0_flat - j0_flat, k_flat]),
                                  axis=1, return_inverse=True)
        t = i_flat - i0_flat                       # position along the diagonal
        order = np.lexsort((t, inv_idx))
        inv_sorted = inv_idx[order]
        starts = np.searchsorted(inv_sorted, np.arange(keys.shape[1]), side="left")
        counts = np.bincount(inv_sorted, minlength=keys.shape[1])
        max_len = int(counts.max()) if counts.size else 0
        out = np.zeros((keys.shape[1], max_len), dtype=vol.dtype)
        valid = np.zeros((keys.shape[1], max_len), dtype=bool)
        row = np.repeat(np.arange(keys.shape[1]), counts)
        pos = np.arange(order.size) - np.repeat(starts, counts)
        out[row, pos] = vol.ravel()[order]
        valid[row, pos] = True
        return out, valid, order, starts, counts, keys.shape[1]

    n_groups = 0
    d, valid, order, starts, counts, n_groups = _gather(a)
    fwd = np.zeros_like(d, dtype=bool)
    c = np.cumsum(d.astype(np.int8), axis=1) > 0
    fwd[:, 1:] = c[:, :-1] > 0
    rev = np.flip(d, axis=1)
    c2 = np.cumsum(rev.astype(np.int8), axis=1) > 0
    c2 = np.flip(c2, axis=1)
    bwd = np.zeros_like(d, dtype=bool)
    bwd[:, :-1] = c2[:, 1:] > 0
    hit = fwd & bwd & valid
    flat = np.zeros(order.size, dtype=bool)
    flat[order] = hit[np.repeat(np.arange(n_groups), counts),
                      np.arange(order.size) - np.repeat(starts, counts)]
    out = flat.reshape(a.shape)
    for ax in inv:
        out = np.flip(out, axis=ax)
    return out & (~occ)


def detect_pockets(pdb: Path, spacing: float = 1.0, probe: float = 1.4,
                   min_psp: int = 5, max_pockets: int = 8,
                   max_grid: int = 24_000_000) -> list[dict]:
    xyz, radii = read_heavy_atoms(pdb)
    if len(xyz) == 0:
        return []
    lo = xyz.min(axis=0) - 6.0
    hi = xyz.max(axis=0) + 6.0
    dims = np.ceil((hi - lo) / spacing).astype(int)
    while int(np.prod(dims)) > max_grid:
        spacing *= 1.25
        dims = np.ceil((hi - lo) / spacing).astype(int)
    nx, ny, nz = (int(d) for d in dims)

    # occupancy: dilate each atom by (r_vdW + r_probe) on the grid
    gi = np.floor((xyz - lo) / spacing).astype(int)
    occ = np.zeros((nx, ny, nz), dtype=bool)
    for (cx, cy, cz), r in zip(gi, radii):
        reach = (r + probe) / spacing
        rr = int(math.ceil(reach))
        x0, x1 = max(0, cx - rr), min(nx, cx + rr + 1)
        y0, y1 = max(0, cy - rr), min(ny, cy + rr + 1)
        z0, z1 = max(0, cz - rr), min(nz, cz + rr + 1)
        if x0 >= x1 or y0 >= y1 or z0 >= z1:
            continue
        gx = (np.arange(x0, x1) - cx) ** 2
        gy = (np.arange(y0, y1) - cy) ** 2
        gz = (np.arange(z0, z1) - cz) ** 2
        d2 = (gx[:, None, None] + gy[None, :, None] + gz[None, None, :]) * spacing ** 2
        occ[x0:x1, y0:y1, z0:z1] |= d2 <= (r + probe) ** 2

    solvent = ~occ
    psp = np.zeros((nx, ny, nz), dtype=np.int16)
    for d in DIRECTIONS:
        psp += _psp_along(occ, d).astype(np.int16)
    if psp.max() < min_psp:
        return []

    candidate = solvent & (psp >= min_psp)
    # 6-connected component labelling
    from scipy import ndimage
    structure = ndimage.generate_binary_structure(3, 1)
    labels, n_lab = ndimage.label(candidate, structure=structure)
    if n_lab == 0:
        return []

    pockets = []
    for lab in range(1, n_lab + 1):
        m = labels == lab
        npts = int(m.sum())
        if npts < 30:                       # ignore specks
            continue
        pts = np.argwhere(m).astype(float) * spacing + lo
        centre = pts.mean(axis=0)
        vals = psp[m]
        pockets.append({
            "label": lab,
            "n_grid_points": npts,
            "volume_A3": npts * spacing ** 3,
            "centre": centre,
            "mean_psp": float(vals.mean()),
            "max_psp": int(vals.max()),
            "extent": pts.max(axis=0) - pts.min(axis=0),
            "druggability_proxy": float(npts * (vals.mean() / max(psp.max(), 1))),
        })
    pockets.sort(key=lambda p: (-p["n_grid_points"], -p["mean_psp"]))
    return pockets[:max_pockets]


def pocket_box(pocket: dict, size: float | None = None) -> dict:
    c = pocket["centre"]
    if size is None:
        size = float(np.clip(np.max(pocket["extent"]) + 8.0, 18.0, 30.0))
    return {"center_x": float(c[0]), "center_y": float(c[1]), "center_z": float(c[2]),
            "size_x": size, "size_y": size, "size_z": size}


if __name__ == "__main__":
    import sys
    path = Path(sys.argv[1])
    pks = detect_pockets(path)
    print(f"{path.name}: {len(pks)} pockets")
    for pk in pks:
        print(f"  #{pk['label']:>2} pts={pk['n_grid_points']:>6} "
              f"vol={pk['volume_A3']:>8.0f} A3 meanPSP={pk['mean_psp']:5.1f} "
              f"centre={np.round(pk['centre'], 1)} "
              f"box={pocket_box(pk)['size_x']:.0f}")
