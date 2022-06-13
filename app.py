from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import speech_recognition as sr
from moviepy.editor import VideoFileClip
from datetime import timedelta
from deep_translator import GoogleTranslator
import srt
import os

def gerar_legenda(arquivo, idiomas):
    if not os.path.exists(f'audios/{arquivo}/'):
        os.mkdir(f'audios/{arquivo}/')

    video = VideoFileClip(f'videos/{arquivo}')
    print('Extraindo Áudio do Vídeo...')
    video.audio.write_audiofile(f'audios/{arquivo}/audio.wav')
    audio = AudioSegment.from_wav(f'audios/{arquivo}/audio.wav')
    silence_treshold = audio.dBFS * 1.75

    print('Detectando Silêncios...')
    sentence_times = detect_nonsilent(audio, min_silence_len=400, silence_thresh=silence_treshold)

    subs = {}
    r = sr.Recognizer()
    c = 0

    for sentence in sentence_times:
        length = sentence[1] - sentence[0]

        while length > 6000:
            sentence_times.insert(sentence_times.index(sentence) + 1, [sentence[0] + int(length/2), sentence[1]])
            sentence_times[sentence_times.index(sentence)] = [sentence[0],(sentence[0] + int(length/2))]

            sentence = sentence_times[sentence_times.index([sentence[0],(sentence[0] + int(length/2))])]

            length = sentence[1] - sentence[0]

    print('Reconhecendo Falas...')

    for sentence in sentence_times:
        if sentence_times.index(sentence) == 0:
            audio[sentence[0]:sentence[1] + 350].export(f'audios/{arquivo}/audio{c}.wav', format="wav")
        else:
            audio[sentence[0] - 350 :sentence[1] + 350].export(f'audios/{arquivo}/audio{c}.wav', format="wav")
        
        with sr.AudioFile(f"audios/{arquivo}/audio{c}.wav") as source:
            try:
                audiodata = r.listen(source)
                transcription = r.recognize_google(audiodata, language='pt-BR')

                start = timedelta(seconds=sentence[0] / 1000)
                end = timedelta(seconds=sentence[1] / 1000)

                for i in idiomas:
                    translated = GoogleTranslator(source='auto', target=i).translate(transcription)

                    print(i, ' - ', translated)

                    if i not in subs:
                        subs[i] = []
                    subs[i].append(srt.Subtitle(index=c, start=start, end=end, content=translated))

            except:
                pass
        
        c += 1

    return [srt.compose(subs[lang]) for lang in subs.keys()] 