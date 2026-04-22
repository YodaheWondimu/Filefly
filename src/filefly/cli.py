# Made by Yodahe Wondimu
# A simple CLI to run the filefly monitor or generate a report.

import argparse
from reporter import generate_report

def main():
    parser = argparse.ArgumentParser(prog="filefly")
    parser.add_argument("command", choices=["monitor", "report"])

    args = parser.parse_args()

    if args.command == "report":
        generate_report()