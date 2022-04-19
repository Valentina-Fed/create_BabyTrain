# create_BabyTrain
This set of scripts allows to download a PhonBank corpus (https://phonbank.talkbank.org/), to structure it according to the standardized ChildProject format 
and to generate required metadata.

The following command will launch the downloading. Please, indicate the source (url) and the destination (where you would like to build your corpus):

`python create_BabyTrain.py --corpus [destination] --url [source]`

To check the sample rate of corpus audio-files, launch the command:

`soxi [name of your audio-file]`

If you would like ro resample audio-files of your corpus to 16000 Hz, launch the command:

`python resample.py --path [path to the directory with audio-files to resample] --output [destination]`

If the audio-files of your corpus are not fully annotated, you can cut the annotated segment with the following command:

`python cut_recordings.py --corpus [path to the directory with audio-files to cut] --output [destination]`
