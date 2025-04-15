import argparse
from pathlib import Path

from adventofcode2023.day import search_day


argparser = argparse.ArgumentParser()
argparser.add_argument("day")
argparser.add_argument(
    "--part",
    "-p",
    default=0,
    type=int,
    choices=[1, 2],
    help="which part to run, by default all"
)
argparser.add_argument(
    "--infile",
    "-i",
    type=Path,
    help="path to input file, uses input.txt in the same directory as the solution by default"
)

args = argparser.parse_args()
day = search_day(args.day)
problem = day.problem_class.from_path(
    args.infile
    if args.infile
    else day.problem_class.default_input_file_path()
)
solution = day.solution_class()
parts = args.part
if parts == 0 or parts == 1:
    print(f"Part 1: {solution.p1(problem)}")
if parts == 0 or parts == 2:
    print(f"Part 2: {solution.p2(problem)}")