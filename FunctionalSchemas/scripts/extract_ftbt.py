'''
March 2019
Xinru Yan

This script extract FT and BT from CSM results
Usage: 
    python extract_ftbt.py -in_f INPUT_FT_FILE -in_g INPUT_GENERAL_FILE -in_b INPUT_BT_FILE -out OUTPUT

Inputs and Outputs:
    INPUT_FT_FILE is the I1000-DThetaF.csv file from the CSM model results
    INPUT_GENERAL_FILE is the input file that feeds into CSM
    INPUT_BT_FILE is the I1000-InstAssign.csv file from the CSM model results
    OUTPUT is the dir that contains the set of FT files and BT files generated from the script
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
