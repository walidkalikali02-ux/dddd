"""
Check-in Counter Staffing — Queuing Theory (M/M/c, Erlang C).

For each hour, find the minimum number of open counters c such that the
average waiting time in queue Wq does not exceed a service-level target.

    lambda = passengers arriving per hour
    mu     = passengers one counter can serve per hour (60 / service_minutes)
    rho    = lambda / (c * mu)  must be < 1 for a stable queue

Erlang C (probability an arriving passenger must wait):
    C(c, a) = [a^c / c! * 1/(1-rho)] / [sum_{k=0}^{c-1} a^k/k! + a^c/c! * 1/(1-rho)],  a = lambda/mu
    Wq      = C(c, a) / (c*mu - lambda)   (hours)

Usage
    python checkin_counters.py [--service-min 2.5] [--target-wait 10] [--max-counters 40]
"""

import argparse
import csv
from math import factorial
from pathlib import Path

DATA = Path(__file__).parent / "data"


def erlang_c(c: int, a: float) -> float:
    rho = a / c
    if rho >= 1:
        return 1.0
    top = a ** c / factorial(c) / (1 - rho)
    bottom = sum(a ** k / factorial(k) for k in range(c)) + top
    return top / bottom


def metrics(lam: float, mu: float, c: int) -> dict:
    a = lam / mu
    rho = a / c
    if rho >= 1:
        return {"rho": rho, "p_wait": 1.0, "wq_min": float("inf"), "lq": float("inf")}
    pw = erlang_c(c, a)
    wq = pw / (c * mu - lam)  # hours
    return {"rho": rho, "p_wait": pw, "wq_min": wq * 60, "lq": lam * wq}


def min_counters(lam: float, mu: float, target_wait_min: float, max_c: int):
    for c in range(1, max_c + 1):
        m = metrics(lam, mu, c)
        if m["wq_min"] <= target_wait_min:
            return c, m
    return None, None


def main():
    ap = argparse.ArgumentParser(description="Check-in counter staffing (M/M/c)")
    ap.add_argument("--service-min", type=float, default=2.5, help="average minutes to serve one passenger")
    ap.add_argument("--target-wait", type=float, default=10, help="max average wait in queue (minutes)")
    ap.add_argument("--max-counters", type=int, default=40)
    args = ap.parse_args()

    mu = 60 / args.service_min
    with open(DATA / "checkin_demand.csv", newline="", encoding="utf-8") as f:
        demand = list(csv.DictReader(f))

    print(f"Service rate per counter : {mu:.1f} pax/hour ({args.service_min} min/pax)")
    print(f"Target average wait      : <= {args.target_wait} min\n")
    print(f"{'Hour':<7}{'Pax/h':>6}{'Counters':>10}{'Util':>7}{'P(wait)':>9}{'Wq(min)':>9}{'Queue':>7}")
    print("-" * 55)
    total = 0
    for row in demand:
        lam = float(row["passengers_per_hour"])
        c, m = min_counters(lam, mu, args.target_wait, args.max_counters)
        if c is None:
            print(f"{row['hour']:<7}{lam:>6.0f}  infeasible with {args.max_counters} counters")
            continue
        total += c
        print(f"{row['hour']:<7}{lam:>6.0f}{c:>10}{m['rho']:>7.0%}{m['p_wait']:>9.0%}"
              f"{m['wq_min']:>9.1f}{m['lq']:>7.1f}")
    print(f"\nTotal counter-hours required: {total}")


if __name__ == "__main__":
    main()
