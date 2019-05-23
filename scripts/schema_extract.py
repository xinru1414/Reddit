'''
April 2019
Xinru Yan

python schema_extract.py -i /usr2/qinlans/SCSM/data/CSM-movie-S5-FT10-BT5-FA0.1-BA1.0-B0.001-SG1.0-AG0.1-E0.8-N0.9-SEQ/FT1.csv -i /usr2/qinlans/SCSM/data/CSM-movie-S5-FT10-BT5-FA0.1-BA1.0-B0.001-SG1.0-AG0.1-E0.8-N0.9-SEQ/FT4.csv -o /usr2/qinlans/SCSM/data/CSM-movie-S5-FT10-BT5-FA0.1-BA1.0-B0.001-SG1.0-AG0.1-E0.8-N0.9-SEQ/movie_schema_14.csv
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