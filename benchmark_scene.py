"""Benchmark scene — renders nothing, just times the hash functions."""
from manim import *
import time
import struct
import zlib
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import manim_merkle_hash

class HashBenchmark(Scene):
    def construct(self):
        import numpy as np
        from manim.utils.hashing import get_hash_from_play_call as flat_hash
        
        results = []
        
        for N in [100, 500, 1000, 1400]:
            dots = VGroup(*[
                Dot(point=np.random.randn(3), color=RED, radius=0.02)
                for _ in range(N)
            ])
            
            class FakeScene:
                pass
            class FakeCamera:
                frame_center = np.array([0, 0, 0])
            class FakeAnim:
                mobject = dots[0]
                run_time = 1.0
                rate_func = linear
                def __str__(self):
                    return 'FakeAnim'
            
            scene = FakeScene()
            camera = FakeCamera()
            anims = [FakeAnim()]
            mobjects = list(dots.submobjects)
            
            # Time flat hash:
            times_flat = []
            for _ in range(3):
                t0 = time.perf_counter()
                try:
                    flat_hash(scene, camera, anims, mobjects)
                except Exception as e:
                    times_flat.append(0)
                    break
                times_flat.append(time.perf_counter() - t0)
            t_flat = sum(times_flat) / max(len(times_flat), 1)
            
            # Time Merkle hash:
            times_merkle = []
            for _ in range(3):
                t0 = time.perf_counter()
                manim_merkle_hash.get_hash_from_play_call(scene, camera, anims, mobjects)
                times_merkle.append(time.perf_counter() - t0)
            t_merkle = sum(times_merkle) / len(times_merkle)
            
            speedup = t_flat / t_merkle if t_merkle > 0 else float('inf')
            
            print(f"N={N:5d}: flat={t_flat*1000:8.1f}ms  merkle={t_merkle*1000:8.1f}ms  speedup={speedup:.1f}x")
        
        # Don't actually render anything:
        self.add(Text("Benchmark complete — see console output", font_size=24))
        self.wait(1)
