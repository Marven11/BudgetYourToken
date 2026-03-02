import subprocess
import os

results = []
for m in [1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 7.0, 10.0]:
    env = os.environ.copy()
    env["CACHE_MULTIPLIER"] = str(m)
    r = subprocess.run(
        ["python", "challenge.py", "solve.claude.solve_claude"],
        capture_output=True, text=True, env=env
    )
    line = r.stdout.strip().split("\n")[0]
    results.append((m, line))

for m, line in results:
    print(f"multiplier={m}: {line}")
