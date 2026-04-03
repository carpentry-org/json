import json
import time

def make_large_arr(n):
    return json.dumps([{"id": i, "name": f"item_{i}", "active": True, "score": 3.14} for i in range(n)])

def make_num_arr(n):
    return json.dumps(list(range(n)))

def make_str_arr(n):
    return json.dumps([f"item_{i}" for i in range(n)])

def make_flat_obj(n):
    return json.dumps({f"key_{i}": i for i in range(n)})

def bench_parse(input_str, runs=50):
    best = float('inf')
    for _ in range(runs):
        t0 = time.perf_counter_ns()
        json.loads(input_str)
        t1 = time.perf_counter_ns()
        best = min(best, t1 - t0)
    return best

def bench_serialize(obj, runs=50):
    best = float('inf')
    for _ in range(runs):
        t0 = time.perf_counter_ns()
        json.dumps(obj)
        t1 = time.perf_counter_ns()
        best = min(best, t1 - t0)
    return best

def fmt_time(ns):
    if ns < 1000:
        return f"{ns}ns"
    elif ns < 1_000_000:
        return f"{ns/1000:.2f}µs"
    else:
        return f"{ns/1_000_000:.2f}ms"

print("=== Python json module ===")
print()

# Parse benchmarks
print("--- Parse ---")
cases = [
    ("Primitive (42)", "42"),
    ("Short string", '"hello world"'),
    ("Small object (2 keys)", '{"name":"carp","version":1}'),
]
for name, inp in cases:
    t = bench_parse(inp)
    print(f"  {name}: {fmt_time(t)}")

for n in [100, 1000]:
    inp = make_large_arr(n)
    t = bench_parse(inp, runs=20 if n >= 1000 else 50)
    print(f"  Array ({n} objects, {len(inp)} bytes): {fmt_time(t)}")

for n in [5000]:
    inp = make_num_arr(n)
    t = bench_parse(inp, runs=20)
    print(f"  Array ({n} numbers, {len(inp)} bytes): {fmt_time(t)}")

for n in [500]:
    inp = make_flat_obj(n)
    t = bench_parse(inp, runs=50)
    print(f"  Object ({n} keys, {len(inp)} bytes): {fmt_time(t)}")

nested = '{"a":{"b":{"c":{"d":{"e":{"f":{"g":{"h":true}}}}}}}}'
t = bench_parse(nested)
print(f"  Nested object (8 deep): {fmt_time(t)}")

escaped = r'["hello\nworld","tab\there","quote\"inside","back\\slash","unicode\u0041\u00e9"]'
t = bench_parse(escaped)
print(f"  Escaped strings: {fmt_time(t)}")

print()

# Serialize benchmarks
print("--- Serialize ---")
small_obj = {"name": "carp", "version": 1}
t = bench_serialize(small_obj)
print(f"  Small object: {fmt_time(t)}")

med_arr = json.loads(make_large_arr(100))
t = bench_serialize(med_arr)
print(f"  Array (100 objects): {fmt_time(t)}")

large_arr = json.loads(make_large_arr(1000))
t = bench_serialize(large_arr, runs=20)
print(f"  Array (1000 objects): {fmt_time(t)}")

print()

# Roundtrip
print("--- Roundtrip ---")
inp = make_large_arr(100)
best = float('inf')
for _ in range(50):
    t0 = time.perf_counter_ns()
    obj = json.loads(inp)
    json.loads(json.dumps(obj))
    t1 = time.perf_counter_ns()
    best = min(best, t1 - t0)
print(f"  Parse + serialize (100 objects): {fmt_time(best)}")
