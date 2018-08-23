import speech_recognition as sr
import pyttsx
import os.path
import sys
import sys 
import json


try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

CLIENT_ACCESS_TOKEN = 'd4bc6129ec4c453b8be93bf6abd96859' 

ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)

request = ai.text_request()

#request.lang = 'en'  # optional, default value equal 'en'

request.session_id = "1234"

mic_name = "USB PnP Sound Device: Audio (hw:1,0)"
sample_rate = 48000
chunk_size = 1047
r = sr.Recognizer()
mic_list = sr.Microphone.list_microphone_names()
 
for i, microphone_name in enumerate(mic_list):
    if microphone_name == mic_name:
        device_id = i
 
with sr.Microphone(device_index = device_id, sample_rate = sample_rate, 
                        chunk_size = chunk_size) as source:
     
    r.adjust_for_ambient_noise(source)
    print("Say Something")
  
    audio = r.listen(source)
         
    try:
        text = r.recognize_google(audio)
        print("you said: ", text)
        #engine = pyttsx.init()
	#voices = engine.getProperty('voices')
	#for voice in voices:
   	#    engine.setProperty('voice', voice.id)
        #    engine.say(text)

 	#engine.say(text)
	#engine.runAndWait()
	
	request.query = str(text.lower())
    	response = request.getresponse()
    	a = response.read()
    	#my_json = a.decode('utf8').replace("'", '"')
    	#print(my_json) 
    	#print('- ' * 20)

    	# Load the JSON to a Python list & dump it back out as formatted JSON
    	data = json.loads(a)
	#print data
	if data['result']['fulfillment']['speech'] != '':
        	print data['result']['fulfillment']['speech']
    	else:
        	print "No response"	
 
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
     
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
