"""
Airport Gate Assignment Problem (GAP) — Mixed-Integer Linear Programming.

Decision variables
    x[f, g] = 1 if flight f is assigned to gate g (or to the remote apron stand)

Objective
    Minimize total passenger walking distance
        sum_f sum_g passengers_f * distance_g * x[f, g]
    where the remote apron stand has a large "distance" (bus transfer penalty).

Constraints
    1. Every flight gets exactly one gate (or the apron).
    2. A flight can only use a gate that fits its aircraft size (S < M < L).
    3. No two flights may occupy the same gate at the same time,
       including a buffer (turnaround/clearance) between them.

Usage
    python gate_assignment.py [--buffer 15] [--apron-penalty 1000]
"""

import argparse
import csv
from pathlib import Path

import pulp

DATA = Path(__file__).parent / "data"
SIZE_RANK = {"S": 1, "M": 2, "L": 3}
APRON = "APRON"


def to_min(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def load(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def solve(flights, gates, buffer_min=15, apron_penalty=1000):
    gate_ids = [g["gate"] for g in gates] + [APRON]
    dist = {g["gate"]: float(g["walking_distance_m"]) for g in gates}
    dist[APRON] = float(apron_penalty)
    gate_size = {g["gate"]: SIZE_RANK[g["max_size"]] for g in gates}
    gate_size[APRON] = SIZE_RANK["L"]  # remote stand accepts any aircraft

    F = {f["flight"]: f for f in flights}
    start = {k: to_min(v["arrival"]) for k, v in F.items()}
    end = {k: to_min(v["departure"]) + buffer_min for k, v in F.items()}  # occupied until departure + buffer

    prob = pulp.LpProblem("Gate_Assignment", pulp.LpMinimize)

    # Only create variables for size-compatible (flight, gate) pairs -> constraint 2
    pairs = [(f, g) for f in F for g in gate_ids
             if SIZE_RANK[F[f]["aircraft_size"]] <= gate_size[g]]
    x = pulp.LpVariable.dicts("x", pairs, cat="Binary")

    # Objective: passenger-weighted walking distance
    prob += pulp.lpSum(int(F[f]["passengers"]) * dist[g] * x[f, g] for f, g in pairs)

    # 1. Each flight assigned exactly once
    for f in F:
        prob += pulp.lpSum(x[f, g] for g in gate_ids if (f, g) in x) == 1, f"assign_{f}"

    # 3. No overlap at a physical gate. For every flight start time t, the set of
    #    flights occupying the gate at t forms a clique -> at most one of them per gate.
    for t_flight, t in start.items():
        active = [f for f in F if start[f] <= t < end[f]]
        if len(active) < 2:
            continue
        for g in gate_ids:
            if g == APRON:
                continue
            vars_here = [x[f, g] for f in active if (f, g) in x]
            if len(vars_here) > 1:
                prob += pulp.lpSum(vars_here) <= 1, f"overlap_{t_flight}_{g}"

    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    status = pulp.LpStatus[prob.status]
    assignment = {f: g for f, g in pairs if x[f, g].value() > 0.5}
    return status, pulp.value(prob.objective), assignment


def gantt(flights, assignment, gate_order, step=10):
    t0 = min(to_min(f["arrival"]) for f in flights)
    t1 = max(to_min(f["departure"]) for f in flights)
    t0 -= t0 % 60
    cols = (t1 - t0) // step + 1
    header = "".join(f"{(t0 + i * step) // 60:02d}" if (t0 + i * step) % 60 == 0 else " "
                     for i in range(cols))
    lines = [f"{'':7}{header}"]
    for g in gate_order:
        row = [" "] * (cols + 2)
        for f in flights:
            if assignment.get(f["flight"]) != g:
                continue
            a = (to_min(f["arrival"]) - t0) // step
            d = (to_min(f["departure"]) - t0) // step
            for i in range(a, d + 1):
                row[i] = "█"
            label = f["flight"]
            for k, ch in enumerate(label[: max(0, d - a + 1)]):
                row[a + k] = ch
        lines.append(f"{g:<7}{''.join(row)}")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Airport gate assignment (MILP)")
    ap.add_argument("--buffer", type=int, default=15, help="minutes between consecutive flights at a gate")
    ap.add_argument("--apron-penalty", type=float, default=1000,
                    help="equivalent walking metres per passenger for the remote stand (bus)")
    args = ap.parse_args()

    flights = load(DATA / "flights.csv")
    gates = load(DATA / "gates.csv")
    status, obj, assignment = solve(flights, gates, args.buffer, args.apron_penalty)

    print(f"Solver status : {status}")
    print(f"Objective     : {obj:,.0f} passenger-metres\n")

    dist = {g["gate"]: float(g["walking_distance_m"]) for g in gates}
    print(f"{'Flight':<8}{'Arr':<7}{'Dep':<7}{'Size':<6}{'Pax':>5}  {'Gate':<6}{'Walk(m)':>8}")
    print("-" * 50)
    for f in sorted(flights, key=lambda r: r["arrival"]):
        g = assignment[f["flight"]]
        w = dist.get(g, "bus")
        print(f"{f['flight']:<8}{f['arrival']:<7}{f['departure']:<7}{f['aircraft_size']:<6}"
              f"{f['passengers']:>5}  {g:<6}{w!s:>8}")

    on_apron = [f for f, g in assignment.items() if g == APRON]
    total_pax = sum(int(f["passengers"]) for f in flights)
    apron_pax = sum(int(f["passengers"]) for f in flights if f["flight"] in on_apron)
    print(f"\nFlights at contact gates : {len(flights) - len(on_apron)}/{len(flights)}")
    print(f"Passengers bused (apron) : {apron_pax}/{total_pax}")

    print("\nGate timeline (10-minute slots):")
    print(gantt(flights, assignment, [g["gate"] for g in gates] + [APRON]))


if __name__ == "__main__":
    main()
