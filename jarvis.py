#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

try:
    import apiai
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
    import apiai

import pyaudio

import time

import urllib2

import json

CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5

CLIENT_ACCESS_TOKEN = 'b4b5cae5ddd840fdac1cc501c3c40ea8'
SUBSCRIBTION_KEY = '957b512416574c509e7be7390498cb57'

google_translate_url = 'https://api.api.ai/v1/tts?v=20150512&text='
opener = urllib2.build_opener()
opener.addheaders = [('Authorization', 'Bearer b4b5cae5ddd840fdac1cc501c3c40ea8')]
opener.addheaders = [('ocp-apim-subscription-key', '957b512416574c509e7be7390498cb57')]
opener.addheaders = [('Accept-Language', 'en-US')]

kodiAPI = 'http://localhost:8080/jsonrpc?request='

openHAB_REST = 'http://10.0.50.40:8080/rest/'
openHAB_CMD = 'http://10.0.50.40:8080/CMD?'

def main():
    os.system('aplay activate.mp3')
    
    resampler = apiai.Resampler(source_samplerate=RATE)

    vad = apiai.VAD()

    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN, SUBSCRIBTION_KEY)

    request = ai.voice_request()

    def callback(in_data, frame_count, time_info, status):
        frames, data = resampler.resample(in_data, frame_count)
        state = vad.processFrame(frames)
        request.send(data)

        if (state == 1):
            return in_data, pyaudio.paContinue
        else:
            return in_data, pyaudio.paComplete

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS, 
                    rate=RATE, 
                    input=True,
                    output=False,
                    frames_per_buffer=CHUNK,
                    stream_callback=callback)

    stream.start_stream()

    try:
        while stream.is_active():
            time.sleep(0.1)
    except Exception:
        raise e
    except KeyboardInterrupt:
        pass

    stream.stop_stream()
    stream.close()
    p.terminate()

    response = request.getresponse()
    
    response = json.loads(response.read())
    
    speech = response['result']['fulfillment']['speech']
    
    action = response['result']['action']
    
    if speech:
    	print (speech)
    
    	response = opener.open(google_translate_url+speech.replace(' ','%20'))
    	ofp = open('speech.mp3','wb')
    	ofp.write(response.read())
    	ofp.close()
    
    	os.system('aplay speech.mp3')
    	
    elif action == "media.video_play":
    	if response['result']['parameters']['title']:
    		movie = response['result']['parameters']['title']
    	else:
    		movie = response['result']['parameters']['q']
    	movieSearch = '{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": { "filter": {"field": "title", "operator": "is", "value": "'+movie+'"}, "limits": { "start" : 0, "end": 75 }, "properties" : ["art", "rating", "thumbnail", "playcount", "file"], "sort": { "order": "ascending", "method": "label", "ignorearticle": true } }, "id": "libMovies"}'
    	request = opener.open(kodiAPI+movieSearch.replace(' ','%20'))
    	
    	response = json.loads(request.read())
    	
    	print response['result']['movies'][0]['file']
    	
    	movie = response['result']['movies'][0]['file']
    	moviePlay = '{"jsonrpc":"2.0","method":"Player.Open","id":1,"params":{"item":{"file":"'+movie+'"}}}'
    	request = opener.open(kodiAPI+moviePLay.replace(' ','%20'))
    elif action == "smarthome.lights_on":
    	opener.open(openHAB_CMD+'gLiving_Room_LL=ON')
    else:
    	os.system('aplay error.mp3')

if __name__ == '__main__':
    main()