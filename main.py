import requests
import genanki
import json
import time
import random
import re
#from gtts import gTTS
from google.cloud import texttospeech
import os

language = "de-DE"
wordlist = "de_50k.txt"
sentencesPerWord = 4
generateAudio = True
amountOfWords = 2500
delay = 0.1


client = texttospeech.TextToSpeechClient()
voice = texttospeech.VoiceSelectionParams(
    language_code=language, name="de-DE-Neural2-B"
)
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3
)



file = open(wordlist, 'r')

url="https://tatoeba.org/eng/api_v0/search?"
options="from=deu&to=eng&sort=relevance"


audio_model = genanki.Model(
  eval("random.randrange(1 << 30, 1 << 31)"),
  'Clozemaster Style',
  model_type=genanki.Model.CLOZE,
  fields=[
    {'name': 'Sentence'},
    {'name': 'Translation'},
    {'name': 'Ranking/Frequency'},
    {'name': 'TTS'}
  ],
  templates=[
    {
      'name': 'Card 1',
      'qfmt': '{{cloze:Sentence}}<div style=\'font-family: "Arial"; font-size: 15px;\'>({{Translation}}){{TTS}}</div>',
      'afmt': '{{cloze:Sentence}}<br><div style=\'font-family: "Arial"; font-size: 15px;\'>({{Translation}}){{TTS}}</div>',
    },
],
css='.card {\n font-family: arial;\n font-size: 20px;\n text-align: center;\n color: black;\n background-color: white;\n}\n\n'
      '.cloze {\n font-weight: bold;\n color: blue;\n}\n.nightMode .cloze {\n color: lightblue;\n}',
      )

non_audio_model = genanki.Model(
  eval("random.randrange(1 << 30, 1 << 31)"),
  'Clozemaster Style',
  model_type=genanki.Model.CLOZE,
  fields=[
    {'name': 'Sentence'},
    {'name': 'Translation'},
    {'name': 'Ranking/Frequency'}
  ],
  templates=[
    {
      'name': 'Card 1',
      'qfmt': '{{cloze:Sentence}}<div style=\'font-family: "Arial"; font-size: 15px;\'>({{Translation}})</div>',
      'afmt': '{{cloze:Sentence}}<br><div style=\'font-family: "Arial"; font-size: 15px;\'>({{Translation}})</div>',
    },
],
css='.card {\n font-family: arial;\n font-size: 20px;\n text-align: center;\n color: black;\n background-color: white;\n}\n\n'
      '.cloze {\n font-weight: bold;\n color: blue;\n}\n.nightMode .cloze {\n color: lightblue;\n}',
      )



#if generateAudio:
#    if os.path.exists("recordings/"):
#        for i in os.listdir("recordings"):
#            os.remove('recordings/' +i)


my_deck = genanki.Deck(
  eval("random.randrange(1 << 30, 1 << 31)"),
  wordlist)

package = genanki.Package(my_deck)
count = 0
progress = 0
total = amountOfWords * sentencesPerWord

for word_and_frequency in file.readlines():

    count = count + 1

    if count == amountOfWords:
        package.write_to_file(wordlist+'.apkg')
        print(package.media_files)
        for i in package.media_files:
          os.remove(i)

        os.rmdir("recordings")
        exit()

    word = word_and_frequency.split(' ')[0]
    query = url + options + "&query=" + word

    for attempt in range(10):
      try:
        r = requests.get(query,
                            headers={'Accept': 'application/json'})
      except:
        print("Error caught: " + query)
        time.sleep(3)
      else:
        break
    else:
      print("Failed: " + query)

    r = r.json()

    amountOfSentencesGrabbed = 0
    if len(r["results"]) < sentencesPerWord:
      amountOfSentencesGrabbed = len(r["results"])
      total -= sentencesPerWord - amountOfSentencesGrabbed
    else:
      amountOfSentencesGrabbed = sentencesPerWord

    for i in range(amountOfSentencesGrabbed):
        progress += 1
        sentence = r["results"][i]["text"]

        translationList = r["results"][i]["translations"]

        for j in range(len(translationList)):
            if len(translationList[j]) != 0:
                translatedSentence = translationList[j][0]["text"]
                break

        if generateAudio:
            path = "recordings/" + word + str(i) + ".mp3"
            if os.path.exists(path) == False:
              synthesis_input = texttospeech.SynthesisInput(text=sentence)
              response = client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
              )
              with open(path, "wb") as out:
                # Write the response to the output file.
                out.write(response.audio_content)

            #gTTS(sentence, lang=language).save(path)
            package.media_files.append(path)

        sentence = re.sub(word, "{{c1::"+word+"}}", sentence,  flags=re.I)
        
        if generateAudio:
            test_note = genanki.Note(
                model=audio_model,
                fields=[sentence, translatedSentence, str(count) + ": " + word_and_frequency.split(' ')[1] ,"[sound:"+ word + str(i)  + ".mp3]"]
            )
        else:
            test_note = genanki.Note(
                model=audio_model,
                fields=[sentence, translatedSentence ,str(count) + ": " + word_and_frequency.split(' ')[1] ]
            )

        my_deck.add_note(test_note)

        print(str(progress) + "/" + str(total))

    time.sleep(delay)






