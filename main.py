import argparse
from SERVER.server import BaubuddyAPIHandler

parser = argparse.ArgumentParser(description="Transmit CSV to server and generate Excel file.")
parser.add_argument("csv_file", help="Path to the CSV file")
parser.add_argument("-k", "--keys", nargs="+", help="Additional keys to include in Excel")
parser.add_argument("-c", "--colored", action="store_true", help="Enable colored rows")

args = parser.parse_args()

processor = BaubuddyAPIHandler()
processor.process_csv(args.csv_file, args.keys, args.colored)