import speech_recognition as sr
import random
import pyttsx
import os.path
import sys
import sys
import json
import apiai
import os
import requests
from pymongo import MongoClient
client = MongoClient()
db = client.user
cd = client.order
db_data = db.user
order = cd.order
order_data = order.find_one()['order']
print order_data
intwa = random.randint(0,1000)
engine = pyttsx.init()
rate = engine.getProperty('rate')
engine.setProperty('rate', rate-5)
CLIENT_ACCESS_TOKEN = '7c86e3798087447c91135d0d19d8b1c8'
ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
r = sr.Recognizer()
bill = 0
feedback = ''
order = ''

def get_resp(text, name):
       	global feedback, order, bill 
	request = ai.text_request()
	request.query = str(text.lower())
	request.lang = 'en'  # optional, default value equal 'en'
	request.session_id = str(intwa)
	response = request.getresponse()
        a = response.read()
        data = json.loads(a)
	intent =  data['result']['metadata']['intentName']

	if intent == 'Get_Order':
		order = text.lower()
		all = order.split(" ")
		if len(all) == 2:
			quant = int(all[0])
			if all[1] in order_data.keys():
				price = order_data[all[1]]
			bill = quant * price
		else: 
			bill = random.randint(0,200)
	if intent == 'Feedback_Trigger':
		os.system("espeak 'Your bill is {}'".format(str(bill)))
	if intent == 'Get_feedback':
		feedback = text.lower()	
	if feedback != '' and order != '':
   		sen_req = requests.post("http://text-processing.com/api/sentiment/", data="text={}".format(feedback))
	        asa = sen_req.text
        	sentiment = json.loads(asa)['label']
		if sentiment == 'neutral':
			sentiment = 'pos'
		mongo_save(order, name, sentiment, feedback, bill)
	#print data['result']['fulfillment']['speech']
	return data['result']['fulfillment']['speech']

def mongo_save(order, name, sentiment, feedback, bill):
	print "db insert"
	ins_dict = {"name": name, 'order' : order, 'sentiment': sentiment, 'feedback': feedback, 'bill': bill}
	print ins_dict
	db_data.insert(ins_dict)
	#print db_data.find_one()

mic_name = "USB PnP Sound Device: Audio (hw:1,0)"
sample_rate = 48000
chunk_size = 1047
mic_list = sr.Microphone.list_microphone_names()
for i, microphone_name in enumerate(mic_list):
	if microphone_name == mic_name:
        	device_id = i

with sr.Microphone(device_index = device_id, sample_rate = sample_rate, chunk_size = chunk_size) as source:
    os.system("espeak '{}'".format("What is your name?"))
    r.adjust_for_ambient_noise(source)
    print('Say Something!')
    audio = r.listen(source)
    name = r.recognize_google(audio)
    print name
    while 1:
        r.adjust_for_ambient_noise(source)
	print('Say Something!')
	audio = r.listen(source)
	print ("getting your speech")
	text = r.recognize_google(audio)
        print("you said: {}".format(text))
	check = get_resp(text, name)
	if bool(check):
		os.system("espeak '{}'".format(check))
	else:
                print "No response"
