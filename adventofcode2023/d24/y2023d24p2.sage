#!/usr/bin/env sage

from sage.all import *
import sys

if len(sys.argv) != 19:
    raise ValueError("Needs 18 arguments, 6 for each sample hailstone")

(
    apx, apy, apz, avx, avy, avz,
    bpx, bpy, bpz, bvx, bvy, bvz, 
    cpx, cpy, cpz, cvx, cvy, cvz
) = tuple(int(s) for s in sys.argv[1:])

rpx = var("rpx")
rpy = var("rpy")
rpz = var("rpz")
rvx = var("rvx")
rvy = var("rvy")
rvz = var("rvz")
ta = var("ta")
tb = var("tb")
tc = var("tc")

solutions = solve([
    apx + avx * ta == rpx + rvx * ta,
    apy + avy * ta == rpy + rvy * ta,
    apz + avz * ta == rpz + rvz * ta,
    bpx + bvx * tb == rpx + rvx * tb,
    bpy + bvy * tb == rpy + rvy * tb,
    bpz + bvz * tb == rpz + rvz * tb,
    cpx + cvx * tc == rpx + rvx * tc,
    cpy + cvy * tc == rpy + rvy * tc,
    cpz + cvz * tc == rpz + rvz * tc,
], rpx, rpy, rpz, rvx, rvy, rvz, ta, tb, tc)

print(solutions[0][0]+solutions[0][1]+solutions[0][2])