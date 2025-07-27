# random_number_2025.py – GUI app with graceful fallback   CPython ≥3.9
# ──────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ctypes
import logging
import os
import platform
import struct
import sys
import threading
from ctypes import CFUNCTYPE, POINTER, c_bool, c_uint64, wintypes

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except ModuleNotFoundError:
    raise SystemExit("Tk‑based GUI requires the tkinter package")

__all__ = ["RandomNumberGenerator", "RandomNumberGeneratorGUI"]

# -----------------------------------------------------------------------------
#  Logging
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(levelname)s • %(message)s")
_log = logging.getLogger("rng")

# -----------------------------------------------------------------------------
# 1 ▸ Core – cryptographically secure RNGs
# -----------------------------------------------------------------------------
class RandomNumberGenerator:
    """Library of RNG back‑ends.  Each call returns an **inclusive** integer."""

    # Windows GetSystemInfo feature flag (Win 8+)
    _PF_RDRAND_AVAILABLE = 33  # PF_RDRAND_INSTRUCTION_AVAILABLE

    # ──────────────────────────────────────────────────────────────────
    #  Public RNG APIs
    # ──────────────────────────────────────────────────────────────────
    def entropy_pool(self, lo: int, hi: int) -> int:
        self._check_range(lo, hi)
        rand64 = struct.unpack("Q", os.urandom(8))[0]
        return self._map(rand64, lo, hi)

    def crypto_api(self, lo: int, hi: int) -> int:
        """Windows advapi32!CryptGenRandom (FIPS)."""
        if platform.system() != "Windows":
            raise OSError("CryptGenRandom is Windows‑only")

        self._check_range(lo, hi)
        advapi32, kernel32 = ctypes.windll.advapi32, ctypes.windll.kernel32

        hprov = wintypes.HANDLE()
        # CRYPT_VERIFYCONTEXT | CRYPT_SILENT
        if not advapi32.CryptAcquireContextW(
            ctypes.byref(hprov), None, None, 1, 0xF0000000
        ):
            raise OSError(f"CryptAcquireContextW failed (0x{kernel32.GetLastError():08X})")

        try:
            buf = (ctypes.c_ubyte * 8)()
            if not advapi32.CryptGenRandom(hprov, 8, ctypes.byref(buf)):
                raise OSError(f"CryptGenRandom failed (0x{kernel32.GetLastError():08X})")
            rand64 = struct.unpack("Q", bytes(buf))[0]
        finally:
            advapi32.CryptReleaseContext(hprov, 0)

        return self._map(rand64, lo, hi)

    def rdrand(self, lo: int, hi: int) -> int:
        """64‑bit Intel/AMD RDRAND (x86‑64)."""
        if not self.supports_rdrand():
            raise OSError("RDRAND not supported on this CPU/OS")

        self._check_range(lo, hi)
        rdrand64_step = self._make_rdrand_asm()

        result = c_uint64()
        retries = 10
        for _ in range(retries):
            if rdrand64_step(ctypes.byref(result)):
                return self._map(result.value, lo, hi)
        raise RuntimeError("RDRAND returned CF=0 ten times")

    # ──────────────────────────────────────────────────────────────────
    #  Capability tests (used by GUI to disable buttons)
    # ──────────────────────────────────────────────────────────────────
    @staticmethod
    def supports_entropy() -> bool:
        return True  # always

    @staticmethod
    def supports_crypto_api() -> bool:
        return platform.system() == "Windows"

    @classmethod
    def supports_rdrand(cls) -> bool:
        if platform.system() != "Windows":
            return False
        return bool(ctypes.windll.kernel32.IsProcessorFeaturePresent(cls._PF_RDRAND_AVAILABLE))

    # ──────────────────────────────────────────────────────────────────
    #  Internals
    # ──────────────────────────────────────────────────────────────────
    @staticmethod
    def _check_range(lo: int, hi: int) -> None:
        if lo >= hi:
            raise ValueError("min must be < max")

    @staticmethod
    def _map(v: int, lo: int, hi: int) -> int:
        return lo + (v % (hi - lo + 1))

    _RDRAND_PROTO = CFUNCTYPE(c_bool, POINTER(c_uint64))

    @classmethod
    def _make_rdrand_asm(cls) -> _RDRAND_PROTO:
        code = b"\x48\x31\xC0\x0F\xC7\xF0\x48\x89\x01\x0F\x92\xC0\xC3"
        size = len(code)
        kernel32 = ctypes.windll.kernel32
        addr = kernel32.VirtualAlloc(None, size, 0x1000, 0x40)  # MEM_COMMIT, PAGE_EXECUTE_READWRITE
        if not addr:
            raise OSError("VirtualAlloc failed")
        ctypes.memmove(addr, code, size)
        return cls._RDRAND_PROTO(addr)


# -----------------------------------------------------------------------------
# 2 ▸ Tkinter GUI
# -----------------------------------------------------------------------------
class RandomNumberGeneratorGUI:
    """Interactive demo; unavailable back‑ends are greyed‑out."""

    def __init__(self) -> None:
        self._rng = RandomNumberGenerator()

        self.root = tk.Tk()
        self.root.title("Hardware‑grade Random Number Generator")
        self.root.geometry("960x280")

        style = ttk.Style(self.root)
        style.theme_use("clam" if "clam" in style.theme_names() else "default")

        self._build()

    # ── Build UI ─────────────────────────────────────────────────────
    def _build(self) -> None:
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill="both", expand=True)

        generators = [
            ("Entropy pool", self._rng.entropy_pool, self._rng.supports_entropy()),
            ("Windows CryptoAPI", self._rng.crypto_api, self._rng.supports_crypto_api()),
            ("Intel/AMD RDRAND", self._rng.rdrand, self._rng.supports_rdrand()),
        ]

        for col, (name, fn, supported) in enumerate(generators):
            self._make_panel(main, name, fn, supported).grid(row=0, column=col, sticky="nsew", padx=6)

        for c in range(len(generators)):
            main.columnconfigure(c, weight=1)

    # ── Single generator frame ───────────────────────────────────────
    def _make_panel(
        self,
        parent: ttk.Frame,
        title: str,
        func,
        supported: bool,
    ) -> ttk.Frame:
        frame = ttk.LabelFrame(parent, text=title)
        ttk.Label(frame, text=self._describe(title), wraplength=240, justify="left").grid(
            row=0, column=0, columnspan=2, padx=4, pady=(4, 8), sticky="w"
        )

        # Min / max inputs
        ttk.Label(frame, text="Min").grid(row=1, column=0)
        min_var = tk.IntVar(value=1)
        ttk.Entry(frame, textvariable=min_var, width=8).grid(row=1, column=1, sticky="ew")

        ttk.Label(frame, text="Max").grid(row=2, column=0)
        max_var = tk.IntVar(value=100)
        ttk.Entry(frame, textvariable=max_var, width=8).grid(row=2, column=1, sticky="ew")

        result_var = tk.StringVar(value="Result:")
        ttk.Label(frame, textvariable=result_var, wraplength=220).grid(
            row=3, column=0, columnspan=2, pady=(8, 4)
        )

        btn = ttk.Button(
            frame,
            text=("Generate" if supported else "Unavailable"),
            command=lambda: self._run(func, min_var, max_var, result_var, btn),
            state=("normal" if supported else "disabled"),
            width=12,
        )
        btn.grid(row=4, column=0, columnspan=2, pady=4)

        for r in range(5):
            frame.rowconfigure(r, weight=0)
        frame.columnconfigure(1, weight=1)
        return frame

    @staticmethod
    def _describe(name: str) -> str:
        texts = {
            "Entropy pool": "os.urandom / getrandom – kernel entropy.",
            "Windows CryptoAPI": "advapi32!CryptGenRandom (FIPS 140‑2).",
            "Intel/AMD RDRAND": "Hardware RNG instruction (x86‑64).",
        }
        return texts.get(name, "")

    # ── Threaded generation (keeps UI responsive) ────────────────────
    def _run(
        self,
        func,
        min_var: tk.IntVar,
        max_var: tk.IntVar,
        result: tk.StringVar,
        button: ttk.Button,
    ) -> None:
        def work() -> None:
            try:
                result.set("…")
                val = func(min_var.get(), max_var.get())
                result.set(f"Result: {val}")
            except Exception as exc:
                _log.exception("Generator failed")
                messagebox.showerror("Error", str(exc), parent=self.root)
                result.set("Error")
            finally:
                button.state(["!disabled"])

        button.state(["disabled"])
        threading.Thread(target=work, daemon=True).start()

    # ── Kick‑off ─────────────────────────────────────────────────────
    def run(self) -> None:
        self.root.mainloop()


# -----------------------------------------------------------------------------
# 3 ▸ Entry point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Headless self‑test first (useful in CI):
    rng = RandomNumberGenerator()
    for name, ok in (
        ("Entropy", rng.supports_entropy()),
        ("CryptoAPI", rng.supports_crypto_api()),
        ("RDRAND", rng.supports_rdrand()),
    ):
        if ok:
            print(f"{name:9}: {rng.entropy_pool(1, 9) if name=='Entropy' else '✓'}")
        else:
            print(f"{name:9}: (unsupported)")

    # Launch GUI
    RandomNumberGeneratorGUI().run()
