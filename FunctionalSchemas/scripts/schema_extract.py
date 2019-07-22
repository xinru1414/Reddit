'''
April 2019
Xinru Yan

This script extracts the schema sentences from each post. 
Input files:
    Each input file should be a CSV file representing 1 functional structure and all input files together should represent one schema
Output file:
    The output file is schema file
Usage:
    python schema_extract.py -i FS_1.csv -i FS_4.csv -o SCHEMA_14.csv
'''
import pandas as pd
import click


@click.command()
@click.option('-i', '--input', 'input', type=str, multiple=True)
@click.option('-o', '--output', 'output', type=str)
def main(input, output):
    frames = []
    for item in input:
        df = pd.read_csv(item)
        frames.append(df)
    result = pd.concat(frames)
    result = result[result.columns[1:]]
    result = result.sort_values(by=['SeqId', 'InstNo'])
    result.to_csv(output, index=False)


if __name__ == '__main__':
    main()
