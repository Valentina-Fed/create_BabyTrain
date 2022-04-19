from pydub import AudioSegment as am
import os
if __name__ == "__main__":
  import argparse

  parser = argparse.ArgumentParser()
  parser.add_argument('--path',
                      required=True,
                      help='the whole path to the folder where you will take the data of your corpus: /...'
                      )
  parser.add_argument('--output',
                      required=True,
                      help='the whole path where you would like to save your resampled file: /...'
                      )
  args = parser.parse_args()
  filepath = args.path
  output = args.output

  for file in os.listdir(filepath):
      if file.endswith('.wav'):
        sound = am.from_file(f'{filepath}/{file}', format='wav', frame_rate=22050)
        sound = sound.set_frame_rate(16000)
        sound.export(f'{output}/{file}', format='wav')




