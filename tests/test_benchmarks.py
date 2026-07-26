import time
import pytest
from libansiscreen.screen import Screen
from libansiscreen.color.rgb import Color
from libansiscreen.screen_ops.clip import copy, paste


def build_populated_screen(width: int, height: int) -> Screen:
    """Helper creating a fully populated screen with text and colors."""
    scr = Screen(width=width, height=height)
    scr.set_foreground(Color(220, 180, 50))
    scr.set_background(Color(20, 40, 80))
    scr.cls()

    line = ("#" + "." * (width - 2) + "#\n") * height
    scr.put_text(line[: width * height])
    return scr


def test_benchmark_copy_paste_80x25():
    """
    Benchmark: Copy and paste an 80x25 framebuffer N times.
    """
    width, height = 80, 25
    iterations = 500
    src = build_populated_screen(width, height)
    dst = Screen(width=width, height=height)

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

    print(
        f"\n[BENCHMARK 80x25] {iterations} Iterations:\n"
        f"  - Copy:  {copy_time:.4f}s ({copy_ops_sec:,.1f} ops/sec, {copy_time/iterations*1e6:.2f} µs/op)\n"
        f"  - Paste: {paste_time:.4f}s ({paste_ops_sec:,.1f} ops/sec, {paste_time/iterations*1e6:.2f} µs/op)"
    )

    # Performance assertions
    assert copy_time < 2.0, "80x25 Copy benchmark exceeded target time"
    assert paste_time < 2.0, "80x25 Paste benchmark exceeded target time"
    assert dst.get_cell(0, 0).char == src.get_cell(0, 0).char


def test_benchmark_copy_paste_160x50():
    """
    Benchmark: Copy and paste a 160x50 framebuffer N times.
    """
    width, height = 160, 50
    iterations = 100
    src = build_populated_screen(width, height)
    dst = Screen(width=width, height=height)

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

    print(
        f"\n[BENCHMARK 160x50] {iterations} Iterations:\n"
        f"  - Copy:  {copy_time:.4f}s ({copy_ops_sec:,.1f} ops/sec, {copy_time/iterations*1e6:.2f} µs/op)\n"
        f"  - Paste: {paste_time:.4f}s ({paste_ops_sec:,.1f} ops/sec, {paste_time/iterations*1e6:.2f} µs/op)"
    )

    # Performance assertions
    assert copy_time < 2.0, "160x50 Copy benchmark exceeded target time"
    assert paste_time < 2.0, "160x50 Paste benchmark exceeded target time"
    assert dst.get_cell(0, 0).char == src.get_cell(0, 0).char


def test_benchmark_resize():
    """
    Benchmark: Resizing framebuffer grid between 80x25 and 160x50 N times.
    """
    iterations = 3000
    scr = build_populated_screen(80, 25)

    t0 = time.perf_counter()
    for i in range(iterations):
        if i % 2 == 0:
            scr.resize(160, 50)
        else:
            scr.resize(80, 25)
    t1 = time.perf_counter()

    total_time = t1 - t0
    ops_sec = iterations / total_time if total_time > 0 else 0

    print(
        f"\n[BENCHMARK RESIZE] {iterations} Iterations (80x25 <-> 160x50):\n"
        f"  - Total: {total_time:.4f}s ({ops_sec:,.1f} resizes/sec, {total_time/iterations*1e6:.2f} µs/resize)"
    )

    assert total_time < 2.0, "Resize benchmark exceeded target time"
