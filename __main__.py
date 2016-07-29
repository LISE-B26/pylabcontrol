import argparse
from PyLabControl.src.tools.export_default import export

def main():
    parser = argparse.ArgumentParser()
    parser.parse_args()
    parser.add_argument("-e", "--export", nargs='+', help ="exports default instrumets, probes, and scripts before running gui")
    args = parser.parse_args()
    if args.export:
        if len(args.export == 1):
            export(args.export[0])
        elif len(args.export == 2):
            export(args.export[0], class_type=args.export[1])
        else:
            parser.error('The -e or --export keyword must be given one or two arguments')