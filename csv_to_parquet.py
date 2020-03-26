import pandas as pd
import sys
args = sys.argv
if len(args) < 3:
    print("Usage: python",args[0],"<infile.csv> <outfile.parquet> <OPTIONAL: compression type>")
    quit(-1)

infile = args[1]
outfile = args[2]
compression_type = 'gzip'
if len(args) > 3:
    compression_type = args[3]

df = pd.read_csv(infile)
df.to_parquet(outfile, compression=compression_type)
