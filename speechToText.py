import subprocess
import sys

# resample
import torchaudio
import os

# convert_dir_mp3_to_wav
import glob
from pydub import AudioSegment

# vosk_wav
import wave

# Google_wav
import speech_recognition as sr

# Similarity
similarityModelPath = "/Users/Shaghayegh/Desktop/My Project/cc.fa.300.bin"

# Sentiment
import numpy as np
from tqdm.notebook import tqdm
from transformers import BertConfig, BertTokenizer
from transformers import BertModel
import torch
import torch.nn as nn
import torch.nn.functional as F

labels = ['negative', 'positive']
MODEL_NAME_OR_PATH = 'HooshvareLab/bert-fa-base-uncased'
sentimentFilename ="/Users/Shaghayegh/Desktop/My Project/output"
sentimentModelPath = '/content/drive/MyDrive/pytorch_model.bin'

# microsoft_from_file
subscription="<paste-your-speech-key-here>"
region="<paste-your-speech-location/region-here>"
filename="your_file_name.wav"


def convert_dir_mp3_to_wav(audio_path , singleFilePath = False):
    """ This function converts mp3 file/files to wav file/files. If singleFilePath sets False,
        that means audio_path should be path of one directory. But if it sets True, that means 
        audio_path should be path of one file """

    #if have one file
    if(singleFilePath):
        f_split = audio_path[:-4]
        src = audio_path
        dst = f_split + ".mp3.wav"
        print(src)
        sound = AudioSegment.from_mp3(src)
        sound.export(dst, format="wav")
        command = "It's ok"
        print(command)

    #if have multi files
    else:
        types = (audio_path + os.sep + '*.mp3',)
        files_list = []
        for files in types:
         files_list.extend(glob.glob(files))
        for f in files_list:       
            f_split = f[:-4]
            src = f
            dst = f_split + ".mp3.wav"
            print(src)
            sound = AudioSegment.from_mp3(src)
            sound.export(dst, format="wav")
            command = "It's ok"
            print(command)
    



def resample(directory_resample , sampleRate, singleFilePath = False):
    """ This function changes sample rate of file/files to sampleRate. If singleFilePath sets
        False, that means audio_path should be path of one directory. But if it sets True, that
        means audio_path should be path of one file """

    #if have one file
    if(singleFilePath):
        if directory_resample[-3:] == "wav":
            fullPath = directory_resample;
            waveform, sample_rate = torchaudio.load(fullPath)           
            print("***************")
            print(fullPath)
            metadata = torchaudio.info(fullPath)
            print(metadata)
            downsample_rate=sampleRate
            downsample_resample = torchaudio.transforms.Resample(
                sample_rate, downsample_rate, resampling_method='sinc_interpolation')
            down_sampled = downsample_resample(waveform)
            torchaudio.save(fullPath, down_sampled, downsample_rate)
            metadata = torchaudio.info(fullPath)
            print(metadata)

    #if have multi files
    else:
        arr = os.listdir(directory_resample)
        for file in arr:
            if file[-3:] == "wav":
                fullPath = directory_resample + "\\" + file;
                waveform, sample_rate = torchaudio.load(fullPath)
                print("***************")
                print(fullPath)
                metadata = torchaudio.info(fullPath)
                print(metadata)
                downsample_rate=sampleRate
                downsample_resample = torchaudio.transforms.Resample(
                    sample_rate, downsample_rate, resampling_method='sinc_interpolation')
                down_sampled = downsample_resample(waveform)
                torchaudio.save(fullPath, down_sampled, downsample_rate)
                metadata = torchaudio.info(fullPath)
                print(metadata)




def VOSK_wav(filename , directory_voice , directory_text):
    """ This function convers speech to text.
        filename is the name of file that we want convert it.
        directory_voice is the directory that our file is there.
        directory_text is the directory that output text saves there. """

    try:
        from vosk import Model, KaldiRecognizer, SetLogLevel
        print("module 'vosk' is installed")
    except ModuleNotFoundError:
        print("module 'vosk' is not installed")
        # or
        subprocess.check_call([sys.executable, "-m", "pip", "install", "vosk==0.3.30"])

    SetLogLevel(0)
    file_split = filename[:-4]

    if not os.path.exists("model"):
        print ("Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
        exit (1)

    wf = wave.open(directory_voice + "\\" + filename , "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print ("Audio file must be WAV format mono PCM.")
        exit (1)

    model = Model("model")
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)

    #clean file
    open(directory_text + "\\" + file_split + ".txt", 'w').close()
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            string = rec.Result()
            text = string[string.find('"text"')+10:-3] + " "
            f = open(directory_text + "\\" + file_split + ".txt", "ab")
            f.write(text.encode("utf-8"))
            f.close()

    string = rec.FinalResult()
    text = string[string.find('"text"')+10:-3].encode("utf-8")
    f = open(directory_text + "\\" + file_split + ".txt", "ab")
    f.write(text)
    f.close()
    print(filename + " is done")



def Google_wav(filename , directory_voice , directory_text):
    """ This function convers speech to text with Google.
        filename is the name of file that we want convert it.
        directory_voice is the directory that our file is there.
        directory_text is the directory that output text saves there."""

    #!/usr/bin/env python3

    # obtain path to "english.wav" in the same folder as this script
    AUDIO_FILE = (directory_voice + "\\" + filename)

    # use the audio file as the audio source
    r = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source)  # read the entire audio file

    # recognize speech using Google Speech Recognition
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`

        file_split = filename[:-4]

        #clean file
        open(directory_text + "\\" + file_split + ".txt", 'w').close()

        f = open(directory_text + "\\" + file_split + ".txt", "ab")
        f.write(r.recognize_google(audio,language ='fa-IR').encode("utf-8"))
        f.close()

        print(filename + " is done")
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))


#Microsoft Speech To Text
def microsoft_from_file(filename , subscription , region):

    try:
        import azure.cognitiveservices.speech as speechsdk
        print("module 'azure-cognitiveservices-speech' is installed")
    except ModuleNotFoundError:
        print("module 'azure-cognitiveservices-speech' is not installed")
        # or
        subprocess.check_call([sys.executable, "-m", "pip", "install", "azure-cognitiveservices-speech==1.20.0"])

    speech_config = speechsdk.SpeechConfig(subscription , region)
    audio_input = speechsdk.AudioConfig(filename)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, language="fa" , audio_config=audio_input)
    
    result = speech_recognizer.recognize_once_async().get()
    return result.text



# Similarity
def similarity(similarityModelPath):

    try:
        import fasttext
        print("module 'fasttext' is installed")
    except ModuleNotFoundError:
        print("module 'fasttext' is not installed")
        # or
        subprocess.check_call([sys.executable, "-m", "pip", "install", "fasttext==0.9.2"])

    m_model = fasttext.load_model(similarityModelPath)
    return m_model




# Sentiment

def sentiment(sentimentFilename , sentimentModelPath):
    
    device = setup_device()

    # general config
    MAX_LEN = 128
    TRAIN_BATCH_SIZE = 16
    VALID_BATCH_SIZE = 16
    TEST_BATCH_SIZE = 16

    EPOCHS = 3
    EEVERY_EPOCH = 1000
    LEARNING_RATE = 2e-5
    CLIP = 0.0
   
    os.makedirs(os.path.dirname(sentimentFilename), exist_ok=True)

    # create a key finder based on label 2 id and id to label
    label2id = {label: i for i, label in enumerate(labels)}
    id2label = {v: k for k, v in label2id.items()}

    print(f'label2id: {label2id}')
    print(f'id2label: {id2label}')


    # setup the tokenizer and configuration
    tokenizer = BertTokenizer.from_pretrained(MODEL_NAME_OR_PATH)
    config = BertConfig.from_pretrained(
        MODEL_NAME_OR_PATH, **{
            'label2id': label2id,
            'id2label': id2label,
        })

    x_model = SentimentModel(config=config)
    x_model = x_model.to(device)
    x_model.load_state_dict(torch.load(sentimentModelPath , map_location=torch.device('cpu')))#if gpu is ready delete map location arg

    return x_model , tokenizer
 
class SentimentModel(nn.Module):
    
    def __init__(self, config):
        super(SentimentModel, self).__init__()

        self.bert = BertModel.from_pretrained(MODEL_NAME_OR_PATH)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.classifier = nn.Linear(config.hidden_size, config.num_labels)
    
    def forward(self, input_ids, attention_mask, token_type_ids):
        _, pooled_output = self.bert(
            input_ids=input_ids, 
            attention_mask=attention_mask, 
            token_type_ids=token_type_ids, return_dict=False)
        
        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)
        return logits 

class TaaghcheDataset(torch.utils.data.Dataset):
    """ Create a PyTorch dataset for Taaghche. """

    def __init__(self, tokenizer, comments, targets=None, label_list=None, max_len=128):
        self.comments = comments
        self.targets = targets
        self.has_target = isinstance(targets, list) or isinstance(targets, np.ndarray)

        self.tokenizer = tokenizer
        self.max_len = max_len

        
        self.label_map = {label: i for i, label in enumerate(label_list)} if isinstance(label_list, list) else {}
    
    def __len__(self):
        return len(self.comments)

    def __getitem__(self, item):
        comment = str(self.comments[item])

        if self.has_target:
            target = self.label_map.get(str(self.targets[item]), str(self.targets[item]))

        encoding = self.tokenizer.encode_plus(
            comment,
            add_special_tokens=True,
            truncation=True,
            max_length=self.max_len,
            return_token_type_ids=True,
            padding='max_length',
            return_attention_mask=True,
            return_tensors='pt')
        
        inputs = {
            'comment': comment,
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'token_type_ids': encoding['token_type_ids'].flatten(),
        }

        if self.has_target:
            inputs['targets'] = torch.tensor(target, dtype=torch.long)
        
        return inputs

def setup_device():

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f'device: {device}')

    train_on_gpu = torch.cuda.is_available()

    if not train_on_gpu:
        print('CUDA is not available.  Training on CPU ...')
    else:
        print('CUDA is available!  Training on GPU ...')

    return device

def create_data_loader(x, y, tokenizer, max_len, batch_size, label_list):
    dataset = TaaghcheDataset(
        comments=x,
        targets=y,
        tokenizer=tokenizer,
        max_len=max_len, 
        label_list=label_list)
    
    return torch.utils.data.DataLoader(dataset, batch_size=batch_size)

def predict(model, comments, tokenizer, max_len=128, batch_size=32):
    device = setup_device()
    data_loader = create_data_loader(comments, None, tokenizer, max_len, batch_size, None)
    
    predictions = []
    prediction_probs = []

    
    model.eval()
    with torch.no_grad():
        for dl in tqdm(data_loader, position=0):
            input_ids = dl['input_ids']
            attention_mask = dl['attention_mask']
            token_type_ids = dl['token_type_ids']

            # move tensors to GPU if CUDA is available
            input_ids = input_ids.to(device)
            attention_mask = attention_mask.to(device)
            token_type_ids = token_type_ids.to(device)
            
            # compute predicted outputs by passing inputs to the model
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                token_type_ids=token_type_ids)
            
            # convert output probabilities to predicted class
            _, preds = torch.max(outputs, dim=1)

            predictions.extend(preds)
            prediction_probs.extend(F.softmax(outputs, dim=1))

    predictions = torch.stack(predictions).cpu().detach().numpy()
    prediction_probs = torch.stack(prediction_probs).cpu().detach().numpy()

    return predictions, prediction_probs
###
