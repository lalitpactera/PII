# Import Libraries and modules
from gingerit.gingerit import GingerIt
import csv
import pandas as pd
import spacy
import nltk
from nltk.corpus import stopwords
stop = stopwords.words('english')
import speech_recognition as sr
from os import path
import sys
import requests
from pprint import pprint
import json
import objectpath
import re
import string

# Microsoft Text Analytics API nad subscription key to use service
subscription_key = "db21c89ab98f4a278dd953d7c4e69ad9"
text_analytics_base_url = "https://westus.api.cognitive.microsoft.com/text/analytics/v2.1/"

#Microsoft Named Entity Recognition service
entities_url = text_analytics_base_url + "entities"


#PII(Personally identifiable information) Tagging and Masking
def mspii(inputtext):
	text=inputtext
	xt=''
	documents = {"documents" : [{"id": "1", "text": inputtext}]}
	headers   = {"Ocp-Apim-Subscription-Key": subscription_key}
	response  = requests.post(entities_url, headers=headers, json=documents)
	entities = response.json()

	item=[]
	dic1={}
	dic2={}
	names=[]
	nl=[]
	el=[]
	sl=[]
	for items in entities['documents']:
		item=list(items['entities'])
	for i in item:
		name=i['name']
		main_entity=i['type']
		if ('subType' in i):
			sub_entity=i['subType']
		else:
			sub_entity="**"
		nl.append(name)
		el.append(main_entity)
		sl.append(sub_entity)
		dic1=dict(zip(nl,el))
		dic2=dict(zip(nl,sl))


	#List of Tags that need to be masked
	l=["Person","Organization","URL","Email","Number","Date"]
	
	if(len(item)==0):
		return text
	else:
		for i in dic1.keys():
			if dic2[i]=="Number":
				if(ord(i[0])>48 and ord(i[0])<58):
					if(len(i)>4):
						xt=text.replace(i,"**PHI**")
						text=xt
					text=xt
			else:
				if dic1[i] in l:
					xt=text.replace(i,"**PHI**")
					text=xt
				if dic2[i] in l:
					xt=text.replace(i,"**PHI**")
					text=xt
		return text

# PII Method to read from file and print to file
def pii(name_file):
	df_1=pd.read_csv(name_file)
	df = pd.DataFrame(df_1)
	at=[]
	ct=[]
	for row in df['text']:
		k=output(row)
		ct.append(k)
	df['corrected_text']=ct
	for row in df['corrected_text']:
		task=mspii(row)
		at.append(task)
	df['annotated_text']=at
	df.to_csv(r'result.csv')

# Auto Correction Method
def correction(text):
	parser = GingerIt()
	pred=parser.parse(text)
	return pred['result']

def output(text):
	return correction(text)

# Speech to text 
def speechpii():
	r = sr.Recognizer()                 
	with sr.Microphone() as source:     
	    print("Speak Anything :")
	    audio = r.listen(source)        
	    try:
	        text = r.recognize_google(audio)    
	        with open("speech.csv",'w') as f:
	        	f.write(format(text))
	        pii("speech.csv")
	    except:
	        print("Sorry could not recognize your voice")

# Audio file to text
def audiofile(AUDIO_FILE):                                      
	r = sr.Recognizer()
	df_aud = pd.DataFrame(columns=['text'])
	x=[]
	with sr.AudioFile(AUDIO_FILE) as source:
		audio = r.record(source)
		text = r.recognize_google(audio)
		x.append(format(text))
	print(x)
	df_aud['text']= x
	df_aud.to_csv('speech.csv')
	pii("speech.csv")

def main(argv):
	filename            = argv[1]
	print(filename)
	if filename[-3:] == 'csv':
		pii(filename)
	if filename[-3:] == 'wav':
		audiofile(filename)
	
if __name__ == "__main__":
	main(sys.argv)
	