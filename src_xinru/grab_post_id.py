"""
March 2019
Xinru Yan

This is a script for grabbing all post_ids in data/post and put them in a file as an input to pull_reddit_comment.py
Usage:
    python grab_post_id.py -i INPUTDIR -o OUTPUTFILE
"""
import os
import click
from tqdm import tqdm


@click.command()
@click.option('-i', '--input', 'input', type=str)
@click.option('-o', '--output', 'output', type=str)
def main(input, output):
    with open(output, 'w') as fp:
        for file in tqdm(os.listdir(input)):
            fp.write(file.split('.')[0] + '\n')


if __name__ == '__main__':
    main()