import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.parse_args()
    parser.add_argument("-e", "--export_defaults", action="store_true", help ="exports default instrumets, probes, and scripts before running gui")
