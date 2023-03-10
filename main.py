import requests
import genanki
import json
import time
import random
import re
from gtts import gTTS
import os

language = "sk"
wordlist = "sk_50k.txt"
sentencesPerWord = 5
generateAudio = True
amountOfWords = 1000
delay = 0


file = open(wordlist, 'r')

url="https://tatoeba.org/eng/api_v0/search?"
options="from=slk&to=eng&sort=relevance"

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



if generateAudio:
    if os.path.exists("recordings/"):
        for i in os.listdir("recordings"):
            os.remove('recordings/' +i)


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

    r = requests.get(query,
                            headers={'Accept': 'application/json'})

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
            gTTS(sentence, lang=language).save(path)
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






