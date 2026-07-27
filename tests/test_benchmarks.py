import time
import pytest
from pathlib import Path
from libansiscreen.screen import Screen
from libansiscreen.color.rgb import Color
from libansiscreen.screen_ops.clip import copy, paste
from tests.helpers import OUT_DIR

BENCHMARK_LOG = OUT_DIR / "benchmark_results.txt"


def _log_benchmark(text: str) -> None:
    """Prints benchmark output to stdout and appends to tests/out/benchmark_results.txt."""
    print(text)
    with BENCHMARK_LOG.open("a", encoding="utf-8") as f:
        f.write(text + "\n")


def build_populated_screen(width: int, height: int, use_binary: bool = False) -> Screen:
    """Helper creating a fully populated screen with text and colors."""
    scr = Screen(width=width, height=height, use_binary=use_binary)
    scr.set_foreground(Color(220, 180, 50))
    scr.set_background(Color(20, 40, 80))
    scr.cls()

    line = ("#" + "." * (width - 2) + "#\n") * height
    scr.put_text(line[: width * height])
    return scr


def test_benchmark_copy_paste_80x25():
    """
    Benchmark: Copy and paste an 80x25 framebuffer N times (Object and Binary storage).
    """
    width, height = 80, 25
    iterations = 300

    for use_binary in (False, True):
        mode_label = "Binary" if use_binary else "Object"
        src = build_populated_screen(width, height, use_binary=use_binary)
        dst = Screen(width=width, height=height, use_binary=use_binary)

        # 1. Benchmark Copy
        t0 = time.perf_counter()
        for _ in range(iterations):
            copied = copy(src)
        t1 = time.perf_counter()

        copy_time = t1 - t0
        copy_ops_sec = iterations / copy_time if copy_time > 0 else 0

        # 2. Benchmark Paste
        t2 = time.perf_counter()
        for _ in range(iterations):
            paste(dst, src)
        t3 = time.perf_counter()

        paste_time = t3 - t2
        paste_ops_sec = iterations / paste_time if paste_time > 0 else 0

        report = (
            f"\n[BENCHMARK 80x25 - {mode_label}] {iterations} Iterations:\n"
            f"  - Copy:  {copy_time:.4f}s ({copy_ops_sec:,.1f} ops/sec, {copy_time/iterations*1e6:.2f} µs/op)\n"
            f"  - Paste: {paste_time:.4f}s ({paste_ops_sec:,.1f} ops/sec, {paste_time/iterations*1e6:.2f} µs/op)"
        )
        _log_benchmark(report)

        assert copy_time < 3.0, f"80x25 Copy benchmark ({mode_label}) exceeded target time"
        assert paste_time < 3.0, f"80x25 Paste benchmark ({mode_label}) exceeded target time"
        assert dst.get_cell(0, 0).char == src.get_cell(0, 0).char


def test_benchmark_copy_paste_160x50():
    """
    Benchmark: Copy and paste a 160x50 framebuffer N times (Object and Binary storage).
    """
    width, height = 160, 50
    iterations = 100

    for use_binary in (False, True):
        mode_label = "Binary" if use_binary else "Object"
        src = build_populated_screen(width, height, use_binary=use_binary)
        dst = Screen(width=width, height=height, use_binary=use_binary)

        # 1. Benchmark Copy
        t0 = time.perf_counter()
        for _ in range(iterations):
            copied = copy(src)
        t1 = time.perf_counter()

        copy_time = t1 - t0
        copy_ops_sec = iterations / copy_time if copy_time > 0 else 0

        # 2. Benchmark Paste
        t2 = time.perf_counter()
        for _ in range(iterations):
            paste(dst, src)
        t3 = time.perf_counter()

        paste_time = t3 - t2
        paste_ops_sec = iterations / paste_time if paste_time > 0 else 0

        report = (
            f"\n[BENCHMARK 160x50 - {mode_label}] {iterations} Iterations:\n"
            f"  - Copy:  {copy_time:.4f}s ({copy_ops_sec:,.1f} ops/sec, {copy_time/iterations*1e6:.2f} µs/op)\n"
            f"  - Paste: {paste_time:.4f}s ({paste_ops_sec:,.1f} ops/sec, {paste_time/iterations*1e6:.2f} µs/op)"
        )
        _log_benchmark(report)

        assert copy_time < 3.0, f"160x50 Copy benchmark ({mode_label}) exceeded target time"
        assert paste_time < 3.0, f"160x50 Paste benchmark ({mode_label}) exceeded target time"
        assert dst.get_cell(0, 0).char == src.get_cell(0, 0).char


def test_benchmark_resize():
    """
    Benchmark: Resizing framebuffer grid between 80x25 and 160x50 N times (Object and Binary storage).
    """
    iterations = 500

    for use_binary in (False, True):
        mode_label = "Binary" if use_binary else "Object"
        scr = build_populated_screen(80, 25, use_binary=use_binary)

        t0 = time.perf_counter()
        for i in range(iterations):
            if i % 2 == 0:
                scr.resize(160, 50)
            else:
                scr.resize(80, 25)
        t1 = time.perf_counter()

        total_time = t1 - t0
        ops_sec = iterations / total_time if total_time > 0 else 0

        report = (
            f"\n[BENCHMARK RESIZE - {mode_label}] {iterations} Iterations (80x25 <-> 160x50):\n"
            f"  - Total: {total_time:.4f}s ({ops_sec:,.1f} resizes/sec, {total_time/iterations*1e6:.2f} µs/resize)"
        )
        _log_benchmark(report)

        assert total_time < 3.0, f"Resize benchmark ({mode_label}) exceeded target time"


def test_benchmark_cell_writing_650x400():
    """
    Benchmark: Writing 650x400 cells (260,000 cells) across Object and Binary storage modes.
    """
    width, height = 650, 400

    for use_binary in (False, True):
        mode_label = "Binary" if use_binary else "Object"
        scr = Screen(width=width, height=height, use_binary=use_binary)

        t0 = time.perf_counter()
        for y in range(height):
            for x in range(width):
                scr.put_cell(x, y, char="X", fg=Color(255, 0, 0))
        t1 = time.perf_counter()

        elapsed = t1 - t0
        cells_count = width * height
        cells_sec = cells_count / elapsed if elapsed > 0 else 0

        report = (
            f"\n[BENCHMARK WRITE 650x400 - {mode_label}]:\n"
            f"  - Total: {elapsed:.4f}s ({cells_sec:,.1f} cells/sec, {elapsed/cells_count*1e6:.2f} µs/cell)"
        )
        _log_benchmark(report)

        assert elapsed < 3.0, f"650x400 Cell writing ({mode_label}) exceeded target time"
