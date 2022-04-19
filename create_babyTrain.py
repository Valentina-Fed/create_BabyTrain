import os
import pandas as pd
import re
import datetime
import shutil
import urllib
import requests
import pylangacq
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from pathlib import Path
from os.path import isdir, join
from io import BytesIO
from zipfile import ZipFile
from bs4 import BeautifulSoup
import datalad.api as dl

    
def retrieve_links(url_path):
    page = requests.get(url_path).text
    content = BeautifulSoup(page, 'html.parser')
    for node in content.find_all('a'):
      if '/data/' in node.get('href'):
        cha_path = 'https://phonbank.talkbank.org' + node.get('href')
      elif '/media' in node.get('href'):
        rec_path = node.get('href')
      else:
        continue
    return cha_path, rec_path

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


def create_directory(parent_dir, dir, tree):
    if not os.path.isdir(parent_dir + dir):
        if tree:
            path = os.path.join(parent_dir, dir)
            os.makedirs(path)
        else:
            path = os.path.join(parent_dir, dir)
            os.mkdir(path)
    else:
        pass

def copy_files(source, target, substring):
    for filename in Path(source).glob('*.*'):
        if substring in str(filename):
            shutil.copy(filename, target)

def move_files(source, target, files, substring):
    if files:
        for filename in Path(source).glob('*.*'):
            if substring in str(filename):
                shutil.copy(filename, target)
                os.remove(filename)
    else:
        alldirs = os.listdir(source)
        for f in alldirs:
            shutil.move(source + f, target + f)

def remove_files (source, dir, files):
    if dir:
        for dirname in files:
            try:
                shutil.rmtree(source + f'/{dirname}')
            except OSError as e:
                print("Error: %s : %s" % (source + f'/{dirname}', e.strerror))
    else:
        os.remove(source + files)

def unzip(zipurl, path_corpus):
  with urlopen(zipurl) as zipresp:
    with ZipFile(BytesIO(zipresp.read())) as zfile:
      zfile.extractall(f'{path_corpus}')

def select_annotations(source):
    dirs = sorted([f for f in os.listdir(source) if isdir(join(source, f))])
    to_drop = {dir: [] for dir in dirs}
    for dir in dirs:
        files = sorted([f for f in os.listdir(source + '/' + dir)])
        for file in files:
            child = pylangacq.read_chat(source + dir + '/' + file)
            if child.headers()[0]['Participants']['CHI']['age'] == '':
                to_drop[f'{dir}'].append(file)
            for utt in child.utterances():
                if utt.time_marks == None:
                    to_drop[f'{dir}'].append(file)
                break
    return to_drop

def move_file(source, target, filename):
    shutil.copy(filename, target)
    os.remove(filename)

def compile_annotations(source):
    to_drop = select_annotations(source)
    dirs = sorted([f for f in os.listdir(source) if isdir(join(source, f))])
    for dir in dirs:
        files = sorted([f for f in os.listdir(source + '/' + dir)])
        for file in files:
            if file not in to_drop[f'{dir}']:
                move_file(source + '/' + dir, destination_cha, source + '/' + dir + '/' + file)
                os.rename(destination_cha + '/' + file, destination_cha + '/' + f'{name_corpus}_{dir}_{file}')

def to_list(dict):
  to_list = []
  for k,v in dict.items():
    for it in v:
      to_list.append(f'{k}_{it}')
  return to_list

def check_rec(list_rec, list_children, list_dates):
  copy_list = list_rec
  copy_children = list_children
  copy_dates = list_dates
  for i, rec_name in enumerate(list_rec):
      if rec_name in missing_rec:
          copy_list.remove(rec_name)
          del copy_children[i]
          del copy_dates[i]
  return copy_list, copy_children, copy_dates

def rename(list_rec):
  copy_list = []
  for rec in list_rec:
    copy_list.append(f'{name_corpus}_{rec}')
  return copy_list

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--corpus',
                        required=True,
                        help='the whole path to the folder where you would like to create your corpus: /...'
                        )
    parser.add_argument('--url',
                        required=True,
                        help='a link to the website with your corpus'
                        )
    args = parser.parse_args()
    path_corpus = args.corpus
    url_path = args.url
    m = url_path.split('/')
    name_corpus = m[len(m) - 1].replace('.html', '')

    name_experiment = f'{name_corpus}'
    print(f'Your corpus will be created in {path_corpus}/{name_experiment}')
    cha_path, rec_path = retrieve_links(url_path)

    # Create the main folder with the name of the experiment
    dl.create(f'{path_corpus}/{name_experiment}')
    # Create subfolders
    create_directory(f'{path_corpus}/{name_experiment}/', 'metadata', False)
    create_directory(f'{path_corpus}/{name_experiment}/recordings/', 'raw', True)
    create_directory(f'{path_corpus}/{name_experiment}/annotations/cha/', 'raw', True)
    create_directory(f'{path_corpus}/{name_experiment}/', 'extra', False)

    # Download files *.cha from a zipped file
    unzip(cha_path, f'{path_corpus}/{name_experiment}/annotations/cha/raw')

    # Move metadata and other files into the folders METADATA and EXTRA
    source = f'{path_corpus}/{name_experiment}/annotations/cha/raw/{name_corpus}/'
    destination_metadata = f'{path_corpus}/{name_experiment}/metadata/'
    destination_extra = f'{path_corpus}/{name_experiment}/extra/'
    destination_cha = f'{path_corpus}/{name_experiment}/annotations/cha/raw/'

    source2 = f'{path_corpus}/{name_experiment}/annotations/cha/raw/{name_corpus}'
    move_files(source2, destination_metadata, True, 'metadata')
    move_files(source2, destination_extra, True, '.txt')
    print('The metadata files have been moved to metadata folder')

    #downloading and processing annotations
    change_directory(source)
    compile_annotations(source)
    shutil.rmtree(f'{path_corpus}/{name_experiment}/annotations/cha/raw/{name_corpus}')
    print('The annotations have been uploaded.')

    change_directory(destination_cha)
    recording_date = []
    recording_name = {}
    children_rec = []
    corr_age_rec = {}
    files = sorted([f for f in os.listdir(destination_cha)])
    file_set = set([f[:8] for f in files])
    filename = '%%%%%%%'
    for file in files:
        child = pylangacq.read_chat(destination_cha + '/' + file)
        if child.headers()[0]['Participants']['CHI']['name'] == "Sheng":
            children_rec.append('HYS')
            recording_name['HYS'].append(child.headers()[0]['Media'])
        else:
            children_rec.append(child.headers()[0]['Participants']['CHI']['name'])
            if child.headers()[0]['Participants']['CHI']['name'] not in recording_name:
                recording_name[child.headers()[0]['Participants']['CHI']['name']] = [child.headers()[0]['Media']]
            else:
                recording_name[child.headers()[0]['Participants']['CHI']['name']].append(child.headers()[0]['Media'])
        recording_date.append((child.dates_of_recording().pop()).isoformat())
        if filename not in file:
            corr_age_rec[child.headers()[0]['Participants']['CHI']['age']] = child.headers()[0]['Date']
            m = re.search('(?<=\_)(.*?)(?=\_)', file)
            filename = m.group(1)

    child_dob = []
    for age, date in corr_age_rec.items():
        nb_days = int(age.split(';')[0]) * 365 + int(age.split(';')[1].split('.')[0]) * 30 + int(age.split('.')[1])
        child_dob.append(str(date.pop() - datetime.timedelta(days=nb_days))[:10])
    child_experiment = [f'{name_corpus}'] * len(child_dob)
    dob_criterion = ['extrapolated'] * len(child_dob)
    dob_accuracy = ['week'] * len(child_dob)
    children = sorted(set(children_rec))

    recording_name_wav = {}
    recording_name_mp3 = {}
    for k, v in recording_name.items():
        recording_name_wav[k] = [rec.replace(', audio', '.wav') for rec in v]
        recording_name_mp3[k] = [rec.replace(', audio', '.mp3') for rec in v]
    change_directory(f'{path_corpus}/{name_experiment}/recordings/raw/')
    missing_rec = []
    for name, value in recording_name_mp3.items():
        for rec in value:
            rec1 = rec.replace('.mp3', '.cha')
            if os.path.exists(f'{path_corpus}/{name_experiment}/annotations/cha/raw/{name_corpus}_{name}_{rec1}'):
                req = Request(rec_path + '/' + name + '/' + rec)
                try:
                    urllib.request.urlretrieve(rec_path + '/' + name + '/' + rec, f'{name_corpus}_{name}_{rec}')
                except HTTPError as e:
                    print(f'{name}_{rec} is missing')
                    missing_rec.append(f'{name}_{rec}')
    for name, value in recording_name_wav.items():
        for rec in value:
            rec1 = rec.replace('.wav', '.cha')
            if f'{name_corpus}_{name}_{rec1}':
                req = Request(rec_path + '/' + name + '/0wav/' + rec)
                try:
                    urllib.request.urlretrieve(rec_path + '/' + name + '/0wav/' + rec, f'{name_corpus}_{name}_{rec}')
                except HTTPError as e:
                    print(f'{name}_{rec} is missing')
                    missing_rec.append(f'{name}_{rec}')

    print('The recordings have been uploaded.')
    recording_name_wav_list = to_list(recording_name_wav)
    recording_name_mp3_list = to_list(recording_name_mp3)
    rec_name_wav, child_wav, date_wav = check_rec(recording_name_wav_list, children_rec, recording_date)
    rec_name_mp3, child_mp3, date_mp3 = check_rec(recording_name_mp3_list, children_rec, recording_date)
    recording_names = rename(rec_name_wav) + rename(rec_name_mp3)
    children_recordings = child_wav + child_mp3
    recording_date = date_wav + date_mp3
    rec_experiment = [f'{name_corpus}'] * len(children_recordings)
    recording_device = ['usb'] * len(children_recordings)
    start_time = ['00:00'] * len(children_recordings)

    # create .csv
    recordings = {'experiment': rec_experiment, 'child_id': children_recordings, 'date_iso': recording_date,
                  'start_time': start_time, 'recording_device_type': recording_device,
                  'recording_filename': recording_names}
    children = {'experiment': child_experiment, 'child_id': children, 'child_dob': child_dob,
                'dob_criterion': dob_criterion, 'dob_accuracy': dob_accuracy}
    df_recordings = pd.DataFrame(data=recordings)
    df_children = pd.DataFrame(data=children)
    df_children.to_csv(f'/{path_corpus}/{name_experiment}/metadata/children.csv', index=False)
    df_recordings.to_csv(f'{path_corpus}/{name_experiment}/metadata/recordings.csv', index=False)

    # recordings should be put directly to 'recordings/raw' without intermediate folders

    change_directory(f'{path_corpus}/{name_corpus}')
    print(f'Your corpus {name_corpus} has been created.')
