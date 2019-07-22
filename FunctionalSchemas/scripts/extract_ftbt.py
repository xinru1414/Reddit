'''
python extract_ftbt.py -in_f /usr2/qinlans/SCSM/data/CSM-movie-S5-FT10-BT5-FA0.1-BA1.0-B0.001-SG1.0-AG0.1-E0.8-N0.9-SEQ/I1000-DThetaF.csv -in_g /usr2/qinlans/SCSM/data/movie.csv -in_b /usr2/qinlans/SCSM/data/CSM-movie-S5-FT10-BT5-FA0.1-BA1.0-B0.001-SG1.0-AG0.1-E0.8-N0.9-SEQ/I1000-InstAssign.csv -out /usr2/qinlans/SCSM/data/CSM-movie-S5-FT10-BT5-FA0.1-BA1.0-B0.001-SG1.0-AG0.1-E0.8-N0.9-SEQ/
'''
import pandas as pd
import click


def extract_bt(df: pd.DataFrame, output):
    for i in df.BTopic.unique().tolist():
        df_new = df.loc[df.BTopic == i]
        df_new = df_new[['SeqId', 'InstNo', 'Author', 'Text']]
        df_new.to_csv(f'{output}BT{i}.csv')


def extract_ft(df: pd.DataFrame, df2: pd.DataFrame, output):
    for col in df.columns[2:]:
        df1 = df.loc[df[col] == df[col].max(), ['SeqId','InstNo']]
        s1 = pd.merge(df1, df2, how='inner', on=['SeqId', 'InstNo'])
        s2 = s1[['SeqId', 'InstNo', 'Author', 'Text']]
        s2.to_csv(f'{output}{col}.csv')


@click.command()
@click.option('-in_f', '--ft_input', 'input1', type=str)
@click.option('-in_g', '--general_input', 'input2', type=str)
@click.option('-in_b', '--bt_input', 'input3', type=str)
@click.option('-out', '--output', 'output', type=str)
def main(input1, input2, input3, output):
    df1 = pd.read_csv(input1)
    df2 = pd.read_csv(input2)
    df3 = pd.read_csv(input3)

    extract_ft(df=df1, df2=df2, output=output)
    extract_bt(df=df3, output=output)


if __name__ == '__main__':
    main()