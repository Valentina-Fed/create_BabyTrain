import os
from pydub import AudioSegment
import pandas as pd


def change_directory(path):
    try:
        os.chdir(path)
        print("Current working directory: {0}".format(os.getcwd()))
    except FileNotFoundError:
        print("Directory: {0} does not exist".format(path))
    except NotADirectoryError:
        print("{0} is not a directory".format(path))
    except PermissionError:
        print("You do not have permissions to change to {0}".format(path))


def cut_recordings(dataset, rec_name, onset, offset):
    for i, rec in enumerate(rec_name):
      if dataset[i].startswith('textgrid') or dataset[i].startswith('cha') or dataset[i].startswith('eaf'):
        if '/' in rec:
            rec_f = rec.split('/')
            rec_name = rec_f[1].split('_')
            change_directory(f'{output}/{name_corpus}/recordings/raw/{rec_f[0]}')
        else:
            rec_name = rec.split('_')
            change_directory(f'{output}/{name_corpus}/recordings/raw/')
        newAudio = AudioSegment.from_wav(f'{output}/{name_corpus}/recordings/raw/{"_".join(rec_name)}')
        newAudio = newAudio[onset[i]:offset[i]]
        name = "_".join(rec_name).replace('.wav', '')
        newAudio.export(f'{output}/{name_corpus}/recordings/raw/{name}_{str(onset[i])}_{str(offset[i])}.wav', format="wav")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--corpus',
                        required=True,
                        help='the whole path to the folder where you will take the data of your corpus: /...'
                        )
    parser.add_argument('--output',
                        required=True,
                        help='the whole path to the folder yoda where you would like to store your output: /...'
                        )

    args = parser.parse_args()
    output = args.output
    path_corpus = args.corpus
    dict_children = args.dict_children
    m = path_corpus.split('/')
    name_corpus = (m[len(m) - 1]).replace('.git', '')
    df = pd.read_csv(f'{output}/{name_corpus}/metadata/annotations.csv')
    rec_name = df['recording_filename']
    onset = df['range_onset']
    offset = df['range_offset']
    dataset = df['set']
    cut_recordings(dataset, rec_name, onset, offset)



