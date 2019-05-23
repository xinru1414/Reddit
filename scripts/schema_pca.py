'''
March 2019
Xinru Yan

This script extract a set of correlated foreground topics to form a schema

Usage:
    python schema_pca.py -i /usr2/qinlans/SCSM/data/CSM-egz-S5-FT10-BT5-FA0.1-BA1.0-B0.001-SG1.0-AG0.1-E0.8-N0.9-SEQ/I1000-InstSentAssign.csv -o /usr2/qinlans/SCSM/data/CSM-egz-S5-FT10-BT5-FA0.1-BA1.0-B0.001-SG1.0-AG0.1-E0.8-N0.9-SEQ/FT-correlation.csv -tn 10 -pn 4
'''
import pandas as pd
from collections import Counter
from sklearn.decomposition import PCA
import click


def post_ft_count(df: pd.DataFrame, df_dev: pd.DataFrame, noft: int):
    df = df.loc[df.SeqId.isin(df_dev.MovieId)]
    group = df.groupby('SeqId')
    list_of_ft = [i for i in range(noft)]

    df2 = pd.DataFrame()

    for key in group.groups.keys():
        l = group.get_group(key).FTopic.tolist()
        d = dict(Counter(l))
        n = list(set(list_of_ft) - set(l))
        for item in n:
            d[item] = 0
        h = pd.DataFrame(d, index=[key, ])
        df2 = df2.append([h])

    return df2


def pca(n: int, df: pd.DataFrame, output: str):
    pca = PCA(n_components=n)
    pca.fit(df).transform(df)
    print(f'explained variance ratio (first {n} components): {pca.explained_variance_ratio_}')
    df_out = pd.DataFrame(pca.components_, columns=df.columns, index=[i for i in range(n)])
    df_out.to_csv(output)


@click.command()
@click.option('-i', '--input', 'input', type=str)
@click.option('-d', '--dev', 'dev', type=str)
@click.option('-o', '--output', 'output', type=str)
@click.option('-tn', '--number_of_ft_topics', 'noft', type=int)
@click.option('-pn', '--number_of_pc', 'nopc', type=int)
def main(input, dev, output, noft, nopc):
    df = pd.read_csv(input)
    df1 = pd.read_csv(dev, sep='\t')
    df2 = post_ft_count(df=df, df_dev=df1, noft=noft)
    pca(nopc, df2, output=output)


if __name__ == '__main__':
    main()