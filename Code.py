import pyttsx3
import speech_recognition as sr
import webbrowser 
import sys
import os
import time
import re
import datetime
import wikipedia
import subprocess
import smtplib
import requests
import psutil
import configparser
import socket
import urllib.request
import urllib.parse
import yaml
import sqlite3
import random
import aiml
from random import randint
from bs4 import BeautifulSoup as soup
from PyDictionary import PyDictionary
from apscheduler.schedulers.background import BackgroundScheduler

BRAIN_FILE="./pretrained_model/aiml_pretrained_model.dump"
k = aiml.Kernel()

if os.path.exists(BRAIN_FILE):
    print("Loading from brain file: " + BRAIN_FILE)
    k.loadBrain(BRAIN_FILE)
else:
    print("Parsing aiml files")
    k.bootstrap(learnFiles="./pretrained_model/learningFileList.aiml", commands="load aiml")
    print("Saving brain file: " + BRAIN_FILE)
    k.saveBrain(BRAIN_FILE)

engine = pyttsx3.init()
dictionary=PyDictionary()

var = []

count = 0
f = 0

with open("config.yaml") as file:
	config = yaml.full_load(file)
	dbpath = config["db"]
	conn = sqlite3.connect(dbpath)
	c = conn.cursor()
	user = config["user"]["name"]

def write_to_file(message):
	f = open("./assistant/interface/variable.py",'w')
	f.write("var = "+str(message))
	f.close()

def speak(msg):
	var.append({'answer': msg})
	write_to_file(var)
	engine.say(msg)
	engine.runAndWait()

def speakButNotPost(msg):
	engine.say(msg)
	engine.runAndWait()	

def post(msg):
	var.append({'answer': msg})
	write_to_file(var)

def writeToDB(query,category,table,isWebsite = 0,url = ""):
	t = datetime.datetime.now().strftime("%H")
	ID = random.randint(1,1000000)
	user = config["user"]["name"]
	if category == "open":
		params = (ID,user,query,t,isWebsite,url)
		c.execute("INSERT INTO open VALUES (?,?,?,?,?,?)",params)
		conn.commit()
		

def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour>=0 and hour<12:
        speak("Good Morning")

    elif hour>=12 and hour<18:
        speak("Good Afternoon")   

    else:
        speak("Good Evening")

def textInput():
	txt = input("Please enter your command : \n")
	return txt

def openCommand(query):
	reg_ex = re.search('open (.+)', query)
	l = os.listdir(".")
	file_flag = 0
	for item in l:
		if(item in query):
			file_flag = 1
			try:
				subprocess.Popen(['subl',str(item)], stderr=subprocess.PIPE, shell=False).communicate()
				speak("opening file "+str(item))
			except Exception as e:
				speak("I'm sorry, I can't open the requested file")

	if(file_flag == 0):
		if ("prime" or "amazon prime") in query:
			speak("Opening Amazon prime")
			url = "https://www.primevideo.com"
			writeToDB(query,"open","open",1,url)
			try:
				webbrowser.open(url)
			except Exception as e:
				speak("I'm sorry I couldn't open Amazon Prime")

		elif "amazon music" in query:
			speak("opening amazon music")
			url = "https://music.amazon.in/"
			t = datetime.datetime.now().strftime("%H")
			writeToDB(query,"open","open",1,url)
			try:
				webbrowser.open(url)
			except Exception as e:
				speak("I'm sorry I couldn't open Amazon Music")

		elif "chrome" in query:
			params = (user)
			c.execute("select website from open group by website having count(*) = ( select count(*) as c from open where user='vijay' and isWebsite=1 group by website order by c desc limit 1);")
			try:
				rows = c.fetchall()
				print(rows[1][0])
				webbrowser.open("https://"+rows[1][0])
				speak("opening google chrome")
			except Exception as e:
				speak("I'm sory I couldn't open google chrome")		

		elif "terminal" in query:
			t = datetime.datetime.now().strftime("%H")
			ID = random.randint(1,1000000)
			isWebsite = 0
			params = (ID,user,query,t,isWebsite,"None")
			c.execute("INSERT INTO open VALUES (?,?,?,?,?,?)",params)
			conn.commit()
			try:
				subprocess.Popen(['gnome-terminal'], stderr=subprocess.PIPE, shell=False).communicate()
				speak("opening a new terminal")
			except Exception as e:
				speak("I'm sorry, I can't open the bash terminal")
				
		elif "intelligent" in query:
			loc = config["application"]["intellij"]
			t = datetime.datetime.now().strftime("%H")
			ID = random.randint(1,1000000)
			isWebsite = 0
			params = (ID,user,query,t,isWebsite,"None")
			c.execute("INSERT INTO open VALUES (?,?,?,?,?,?)",params)
			conn.commit()
			try:
				subprocess.Popen(['sudo',loc])
				speak("opening intell i j")
			except Exception as e:
				speak("I'm sorry I couldn't open Intellij IDEA")

		elif "sublime" in query:
			t = datetime.datetime.now().strftime("%H")
			ID = random.randint(1,1000000)
			isWebsite = 0
			params = (ID,user,query,t,isWebsite,"None")
			c.execute("INSERT INTO open VALUES (?,?,?,?,?,?)",params)
			conn.commit()
			try:
				subprocess.Popen(['subl'])
				speak("Opening Sublime")
			except Exception as e:
				speak("I'm sorry I couldn't open sublime")
		
		elif "file explorer" in query:
			t = datetime.datetime.now().strftime("%H")
			ID = random.randint(1,1000000)
			isWebsite = 0
			params = (ID,user,query,t,isWebsite,"None")
			c.execute("INSERT INTO open VALUES (?,?,?,?,?,?)",params)
			conn.commit()
			try:
				subprocess.Popen(['xdg-open','.'])
				speak("opening file explorer")
			except Exception as e:
				speak("I'm sorry, I couldn't open file explorer")

		elif ("note pad" in query) or ("notepad" in query):
			t = datetime.datetime.now().strftime("%H")
			ID = random.randint(1,1000000)
			isWebsite = 0
			params = (ID,user,query,t,isWebsite,"None")
			c.execute("INSERT INTO open VALUES (?,?,?,?,?,?)",params)
			conn.commit()
			try:
				speak("opening g edit")
				subprocess.Popen(['gedit','&'], stderr=subprocess.PIPE, shell=False).communicate()
			except FileNotFoundError:
				speak("You don't have g edit installed")
				time.sleep(2)
				print("Install gedit with the following command: 'sudo apt-get install gedit'")

		elif reg_ex:
			domain = reg_ex.group(1)
			speak("Opening"+domain)
			url = 'https://www.' + domain
			t = datetime.datetime.now().strftime("%H")
			ID = random.randint(1,1000000)
			isWebsite = 1
			params = (ID,user,query,t,isWebsite,url)
			c.execute("INSERT INTO open VALUES (?,?,?,?,?,?)",params)
			conn.commit()
			try:
				webbrowser.open(url)
			except Exception as e:
				speak("I'm sorry I couldn't open "+domain)

def wiki(query):
	speak('Searching Wikipedia...')
	query = query.replace("wikipedia", "")
	results = wikipedia.summary(query, sentences=2)
	speak("Wikipedia says")
	print(results)
	speak(results)

def joke():
	res = requests.get('https://icanhazdadjoke.com/',headers={"Accept":"application/json"})
	if res.status_code == requests.codes.ok:
		print(str(res.json()['joke']))
		speak(str(res.json()['joke']))
	else:
		speak("I'm sorry, I ran out of jokes")

def parentDir():
	try:
		subprocess.Popen(['cd','..'])
	except Exception as e:
		speak("I'm sory I couldn't go to the parent directory")		

def dirContents():
	l = os.listdir(".")
	print("-------------------------------------------------------------------------------")
	speak("The contents in your directory :")
	for item in l:
		print(item)
		post(item)
	print("-------------------------------------------------------------------------------")	

def close(query):
	if "chrome" in query:
		try:
			l = [p.info for p in psutil.process_iter(attrs=['pid', 'name']) if 'chrome' in p.info['name']]
			pid = l[0]['pid']
			subprocess.Popen(['kill',str(l[0]['pid'])])
			speak("closing google chrome")
		except Exception as e:
			speak("I'm sorry, either chrome isn't open or I am unable to close it")

	elif "sublime" in query:
		try:
			l = [p.info for p in psutil.process_iter(attrs=['pid', 'name']) if 'sublime_text' in p.info['name']]
			pid = l[0]['pid']
			subprocess.Popen(['kill',str(l[0]['pid'])])
			speak("closing sublime text")
		except Exception as e:
			speak("I'm sorry, either sublime isn't open or I am unable to close it")
	elif "file explorer" in query:
		try:
			l = [p.info for p in psutil.process_iter(attrs=['pid', 'name']) if 'nautilus' in p.info['name']]
			pid = l[0]['pid']
			subprocess.Popen(['kill',str(l[0]['pid'])])
			speak("closing file explorer")
		except Exception as e:
			speak("I'm sorry, either file explorer isn't open or I am unable to close it")
	elif ("notepad" in query) or ("note pad" in query):
		try:
			l = [p.info for p in psutil.process_iter(attrs=['pid', 'name']) if 'gedit' in p.info['name']]
			pid = l[0]['pid']
			subprocess.Popen(['kill',str(l[0]['pid'])])
			speak("closing note pad")
		except Exception as e:
			speak("I'm sorry, either file explorer isn't open or I am unable to close it")

	

def getMeaning(query):
	wordList = query.split(" ")
	word = wordList[2]
	d = dictionary.meaning(word)
	fw = 0
	meaning = "I'm sorry, I don't know what that means"
	try:
		if 'Noun' in d:
			meaning = d['Noun'][0]
			fw = 1
		elif 'Verb' in d:
			meaning = d['Verb'][0]
			fw = 1
	except:
		print("")
	if(fw==1):
		print("\n\n"+word +" : "+meaning)
	else:
		print(meaning)
	speak(meaning)

def playMusic(query):
	loc = config["music"]
	l = os.listdir(loc)
	words = query.split(" ")
	if "list" in query:
		t = datetime.datetime.now().strftime("%H")
		ID = random.randint(1,1000000)
		category = "list_songs"
		params = (ID,user,query,category,t)
		c.execute("INSERT INTO commands VALUES (?,?,?,?,?)",params)
		conn.commit()
		print("\nYour Songs : \n")
		speak("Your songs :")
		for song in l:
			print(song)
			post(song)

	elif "play all" in query:
		for song in l:
			try:
				subprocess.Popen(['mpg123', '-q', loc+song]).wait()
			except Exception as e:
				speak("I'm sorry, I'm not able to play the songs")

	elif "play songs" in query:
		c.execute("select song from music group by song having count(*) = ( select count(*) as c from music where user='vijay' group by song order by c desc limit 1);")
		row = c.fetchall()
		conn.commit()
		song = row[0][0]
		try:
			subprocess.Popen(['sudo','nice','-n','-10','mpg123', '-q', loc+song+".mp3"])
		except Exception as e:
			speak("I'm sorry, I'm not able to play songs")

	else:
		song = words[1]
		if(len(words)>2):
			for i in range(2,len(words)):
				song += words[i]
		song = song.strip()
		t = datetime.datetime.now().strftime("%H")
		ID = random.randint(1,1000000)
		params = (ID,user,query,t,song)
		c.execute("INSERT INTO music VALUES (?,?,?,?,?)",params)
		conn.commit()
		try:
			subprocess.Popen(['mpg123', '-q', loc+song+".mp3"])
		except Exception as e:
			speak("I'm sorry, I'm not able to play the song you requested")

def pauseMusic():
	try:
		l = [p.info for p in psutil.process_iter(attrs=['pid', 'name']) if 'mpg123' in p.info['name']]
		pid = l[0]['pid']
		subprocess.Popen(['sudo''kill','-STOP',str(l[0]['pid'])])
	except Exception as e:
		speak("I'm sorry, either music isn't playing or I am unable to pause it")

def resumeMusic():
	try:
		l = [p.info for p in psutil.process_iter(attrs=['pid', 'name']) if 'mpg123' in p.info['name']]
		pid = l[0]['pid']
		subprocess.Popen(['sudo','kill','-CONT',str(l[0]['pid'])])
	except Exception as e:
		speak("I'm sorry, either music isn't paused or I am unable to resume it")

def stopMusic():
	try:
		l = [p.info for p in psutil.process_iter(attrs=['pid', 'name']) if 'mpg123' in p.info['name']]
		pid = l[0]['pid']
		subprocess.Popen(['sudo','kill',str(l[0]['pid'])])
	except Exception as e:
		speak("I'm sorry, either music isn't playing or I am unable to close it")


def getTime():
	strTime = datetime.datetime.now().strftime("%H:%M")
	speak("The time is " + str(strTime))

def getWeather(api_key, location):
	if(location == "here"):
		location = config["user"]["location"]
	try:
		url = "https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}".format(location, api_key)
		r = requests.get(url)
		temperature = r.json()
		speak("The temperature in "+str(location)+" is "+str(temperature['main']['temp'])+" degree celsius")
		print("temperature description : " + str(temperature['weather']))
	except Exception as e:
		speak("Sorry I am not able to give you the current temperature in "+str(location))

def getHostName():
	hostname = socket.gethostname()
	speak("Your hostname is "+hostname)
	print("Your hostname is : "+hostname)

def openYoutubeVideo(query):
	try:
		search_term = query.replace("youtube","")
		query_string = urllib.parse.urlencode({"search_query" : search_term})
		html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
		search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
		link = ("http://www.youtube.com/watch?v=" + search_results[0])
		webbrowser.open(link)
		speak("Opening the requested video on youtube")
	except Exception as e:
		speak("I'm sorry I could not open your requested video on youtube")

def install(query):
	words = query.split(" ")
	package = words[1]
	packageManager = words[3]
	if(packageManager == "Ubuntu"):
		try:
			subprocess.Popen(['sudo','apt-get','install',package], stderr=subprocess.PIPE, shell=False).communicate()
			speak("Installed "+package)
		except Exception as e:
			speak("Sorry I am not able to install" +package)
			print("Error installing "+package)
	elif(packageManager == "pip" or packageManager == "python"):
		try:
			subprocess.Popen(['sudo','pip3','install',package], stderr=subprocess.PIPE, shell=False).communicate()
			speak("Installed "+package)
		except Exception as e:
			speak("Sorry I am not able to install" +package)
			print("Error installing "+package)
	else:

		speak("Sorry I am not able to install" +package)
		print("Error installing "+package)

def create(query):
	words = query.split(" ");
	fileName = words[1]
	subprocess.Popen(["touch",str(fileName)])
	speak("creating file "+str(fileName))


def delete(query):
	words = query.split(" ");
	fileName = words[1]
	subprocess.Popen(["rm",str(fileName)])
	speak("deleting file " + str(fileName))

def sendEmail(query):
	words = query.split(" ")
	reciever_name = words[4]
	content = textInput()
	email_server = config["email"]["server"]
	sen_username = config["email"]["sender_username"]
	sen_password = config["email"]["sender_password"]
	rec_name = config["email"]["reciever_name"]
	rec_mail = config["email"]["reciever_mail"]
	try:
		if(reciever_name == rec_name):
		    mail = smtplib.SMTP(email_server, 587)
		    mail.ehlo()
		    mail.starttls()
		    mail.login(sen_username, sen_password)
		    mail.sendmail(sen_username, rec_mail, content)
		    mail.close()
		    speak("your email has been sent")
		else:
			speak("I'm sorry, I do not know " + reciever_name)
	except Exception as e:
		speak("I'm sorry, I couldn't send your email")
		print(e)

def speedTest():
	speak("This could take a while")
	try:
		process = subprocess.Popen(["speedtest-cli", "--simple"], stdout=subprocess.PIPE, shell=False)
		out, err = process.communicate()
		arr = str(out).split("\\n")
		print(arr[1])
		speak(arr[1].replace("Mbit/s","Mega bit per second"))
		print(arr[2])
		speak(arr[2].replace("Mbit/s","Mega bit per second"))
	except Exception as e:
		speak("I'm sorry I am unable to tell you your internet speed")

def getNews():
	try:
		news_url="https://news.google.com/news/rss"
		Client=urllib.request.urlopen(news_url)
		xml_page=Client.read()
		Client.close()
		soup_page=soup(xml_page,"xml")
		news_list=soup_page.findAll("item")
		speak("Here's your news : ")
		for news in news_list[:15]:
			print("-----------------")
			print(str(news.title.text.encode('utf-8')).replace("b'",""))
			post(str(news.title.text.encode('utf-8')).replace("b'",""))
	except Exception as e:
		print(e)

def spell(query):
	c.execute("select command from commands where category = 'spell';")
	rows = c.fetchall()
	conn.commit()
	words = query.split(" ")
	try:
		word = words[3]
		if word in rows[0][0]:
			speak("You have already learnt this word.")
			print("You have already learnt this word.")
		speak("The word "+word+" is spelled as")
		for letter in word:
			print("{0}".format(letter.upper()),end =" ")
			speakButNotPost(letter)
		s = ""
		for letter in word:
			s += str(letter.upper())
		var.append({'answer': s})
		write_to_file(var)
		print("\n")
	except Exception as e:
		speak("I'm sorry I cannot spell the word you requested")

def remind():
	#print("time : ",datetime.datetime.now().strftime("%H:%M:%S"))
	if(config["reminders"]["dinner"]==datetime.datetime.now().strftime("%H:%M:%S")):
		speak("It's dinner time, aren't you hungry?")
	elif(config["reminders"]["dinner"]==datetime.datetime.now().strftime("%H:%M:%S")):
		speak("It's time for your lunch, aren't you hungry?")
	elif(config["reminders"]["tea"]==datetime.datetime.now().strftime("%H:%M:%S")):
		speak("It's tea time, a cup of tea should be refreshing!")
	elif(config["reminders"]["friend"]==datetime.datetime.now().strftime("%H:%M:%S")):
		speak("I would suggest take a break and call a friend!")

def weatherCheck(api_key):
	location = config["user"]["location"]
	try:
		url = "https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}".format(location, api_key)
		r = requests.get(url)
		weather = r.json()
		weather_main = weather["weather"][0]["main"]
		if weather_main == 'Rain':
			speak("It seems like there's a rain out there. I would recommend you not to step out")
		elif weather_main == 'Drizzle':
			speak("It seems like there's a drizzle out there. I would recommend you to get back home early before it starts to rain")
		elif weather_main == 'Snow':
			speak("I would recommend you to avoid stepping out as I believe there's a snow fall, but please wear a sweater if you really must go out")
		elif weather_main == 'Thunderstorm':
			speak("Please do not step out, there are thunder storms outside")
		else:
			speak("Weather seems pleasant, you can step out of the house")

	except Exception as e:
		speak("Sorry I am not able to give you a weather check")


def playRockPaperScissors():

	t = ["rock", "paper", "scissors"]
	computer = t[randint(0,2)]
	speak("Alright let's play")
	while True:
		choiceList = takeCommandForGame()
		if("close" in choiceList):
			speak("Okay, let's stop the game")
			break
		try:
			choices = choiceList.split(" ")
			choice = choices[3]
			print("You chose : ",choice)
			if choice == computer:
				print("Tie!")
				speak("It's a tie")
			elif choice == "rock":
				if computer == "paper":
					print("You lose! ", computer, "covers", choice)
					speak("You lose! " + computer + "covers" + choice)
				else:
					print("You win! ", choice, "smashes", computer)
					speak("You win! " + choice + "smashes" + computer)
			elif choice == "paper":
				if computer == "scissors":
					print("You lose! ", computer, "cut", choice)
					speak("You lose! " + computer + "cut" + choice)
				else:
					print("You win! ", choice, "covers", computer)
					speak("You win! " + choice + "covers" + computer)
			elif choice == "scissors":
				if computer == "rock":
					print("You lose " + computer, "smashes", choice)
					speak("You lose " + computer + "smashes" + choice)
				else:
					print("You win!", choice, "cut", computer)
					speak("You win!" + choice + "cut" + computer)
			else:
				print("That's not a valid play, please repeat")
				speak("That's not a valid play, please repeat")
		except Exception as e:
			speak("Didn't get you")

		computer = t[randint(0,2)]

def getBotResponse(query):
    response = k.respond(query)
    if response:
    	if "Alice" in response:
    		response.replace("Alice","Thomas")
    	if "alice" in response:
    		response.replace("alice","thomas")
    	print(str(response))
    	speak(str(response))
    else:
        speak("I'm sorry I didn't get you")

def takeCommandForGame():
	r = sr.Recognizer()
	query = ""
	with sr.Microphone() as source:
		r.pause_threshold = 1
		audio = r.listen(source)
	try:
		query = r.recognize_google(audio, language='en-in')
	except Exception as e:
		speak("Say that again please")
	return query


def takeCommand():
	r = sr.Recognizer()
	global count
	textinput = False
	flag = 0
	if(textinput):
		query = textInput()
		flag = 1
	else:
		with sr.Microphone() as source:
			r.pause_threshold = 1
			audio = r.listen(source)
		try:
			query = r.recognize_google(audio, language='en-in')
			query = query.lower()
			var.append({'question': query})
			write_to_file(var)
			flag = 1
			count = 0

		except Exception as e:
			global f
			if(f==1):
				flag = 0
				if(count==0):
					print("Say that again please")
					count+=1
					return "None",flag
				if(count==1):
					count+=1
					return "None",flag
				if(count==2):
					textinput = "Hey" # Replace with textInput()
					count = 0
					return textinput,1
			return "None",flag

	return query,flag;


if __name__ == "__main__":

	wishMe()
	sched = BackgroundScheduler(daemon=True)
	sched.add_job(remind,'interval',seconds=1)
	sched.start()
	while True:
		query, flag = takeCommand()
		if(f==0):
			time.sleep(0.5)
			print("\n-------------------------------------------------------------------------------\n")
		query = query.lower()

		if(flag==1):

			f = 1
			if ("your name" or "who are you") in query:
				speak("I'm "+config["assistant"]["name"]+" your personal voice assistant")

			elif 'wikipedia' in query:
				if(config["assistant"]["name"] in query):
					query = query.lstrip(config["assistant"]["name"]+" ")
				t = datetime.datetime.now().strftime("%H")
				ID = random.randint(1,1000000)
				category = "wikipedia"
				params = (ID,user,query,category,t)
				c.execute("INSERT INTO commands VALUES (?,?,?,?,?)",params)
				conn.commit()
				wiki(query)

			elif "time" in query:
				if(config["assistant"]["name"] in query):
					query = query.lstrip(config["assistant"]["name"]+" ")
				t = datetime.datetime.now().strftime("%H")
				ID = random.randint(1,1000000)
				category = "time"
				params = (ID,user,query,category,t)
				c.execute("INSERT INTO commands VALUES (?,?,?,?,?)",params)
				conn.commit()
				getTime()

			elif "open" in query:
				if(config["assistant"]["name"] in query):
					query = query.lstrip(config["assistant"]["name"]+" ")
				t = datetime.datetime.now().strftime("%H")
				ID = random.randint(1,1000000)
				category = "open"
				params = (ID,user,query,category,t)
				c.execute("INSERT INTO commands VALUES (?,?,?,?,?)",params)
				conn.commit()
				openCommand(query)

			elif "joke" in query:
				if(config["assistant"]["name"] in query):
					query = query.lstrip(config["assistant"]["name"]+" ")
				t = datetime.datetime.now().strftime("%H")
				ID = random.randint(1,1000000)
				category = "joke"
				params = (ID,user,query,category,t)
				c.execute("INSERT INTO commands VALUES (?,?,?,?,?)",params)
				conn.commit()
				joke()

			elif "close" in query:
				if(config["assistant"]["name"] in query):
					query = query.lstrip(config["assistant"]["name"]+" ")
				t = datetime.datetime.now().strftime("%H")
				ID = random.randint(1,1000000)
				category = "close"
				params = (ID,user,query,category,t)
				c.execute("INSERT INTO commands VALUES (?,?,?,?,?)",params)
				conn.commit()
				close(query)

			elif "list contents" in query:
				if(config["assistant"]["name"] in query):
					query = query.lstrip(config["assistant"]["name"]+" ")
				t = datetime.datetime.now().strftime("%H")
				ID = random.randint(1,1000000)
				category = "list contents"
				params = (ID,user,query,category,t)
				c.execute("INSERT INTO commands VALUES (?,?,?,?,?)",params)
				conn.commit()
				ID = random.randint(1,1000000)
				dirContents()

			elif "install" in query:
				if(config["assistant"]["name"] in query):
					query = query.lstrip(config["assistant"]["name"]+" ")
				t = datetime.datetime.now().strftime("%H")
				ID = random.randint(1,1000000)
				category = "install"
				params = (ID,user,query,category,t)
				c.execute("INSERT INTO commands VALUES (?,?,?,?,?)",params)
				conn.commit()
				install(query)

			elif "parent directory" in query:
				if(config["assistant"]["name"] in query):
					query = query.lstrip(config["assistant"]["name"]+" ")
				parentDir()

			elif ("what does" in query) and ("mean" in query):
				if(config["assistant"]["name"] in query):
					query = query.lstrip(config["assistant"]["name"]+" ")
				words = query.split(" ")
				t = datetime.datetime.now().strftime("%H")
				ID = random.randint(1,1000000)
				category = "dictionary"
				params = (ID,user,query,category,t)
				c.execute("INSERT INTO commands VALUES (?,?,?,?,?)",params)
				conn.commit()
				var.append({'question': query})
				write_to_file(var)
				if(len(words)==4):
					getMeaning(query)
				else:
					speak("Please say that again")

			elif ("rock" in query) or ("paper" in query) or ("scissors" in query):
				playRockPaperScissors()

			elif ("play" in query) or ("songs" in query):
				if(config["assistant"]["name"] in query):
					query = query.lstrip(config["assistant"]["name"]+" ")
				t = datetime.datetime.now().strftime("%H")
				ID = random.randint(1,1000000)
				category = "music"
				params = (ID,user,query,category,t)
				c.execute("INSERT INTO commands VALUES (?,?,?,?,?)",params)
				conn.commit()
				playMusic(query)
				
			elif "email" in query:
				if(config["assistant"]["name"] in query):
					query = query.lstrip(config["assistant"]["name"]+" ")
				t = datetime.datetime.now().strftime("%H")
				ID = random.randint(1,1000000)
				category = "email"
				params = (ID,user,query,category,t)
				c.execute("INSERT INTO commands VALUES (?,?,?,?,?)",params)
				conn.commit()
				sendEmail(query)

			elif "stop music" in query:
				if(config["assistant"]["name"] in query):
					query = query.lstrip(config["assistant"]["name"]+" ")
				t = datetime.datetime.now().strftime("%H")
				ID = random.randint(1,1000000)
				category = "stop_music"
				params = (ID,user,query,category,t)
				c.execute("INSERT INTO commands VALUES (?,?,?,?,?)",params)
				conn.commit()
				stopMusic()

			elif "pause music" in query:
				if(config["assistant"]["name"] in query):
					query = query.lstrip(config["assistant"]["name"]+" ")
				t = datetime.datetime.now().strftime("%H")
				ID = random.randint(1,1000000)
				category = "pause_music"
				params = (ID,user,query,category,t)
				c.execute("INSERT INTO commands VALUES (?,?,?,?,?)",params)
				conn.commit()
				pauseMusic()

			elif "resume music" in query:
				if(config["assistant"]["name"] in query):
					query = query.lstrip(config["assistant"]["name"]+" ")
				t = datetime.datetime.now().strftime("%H")
				ID = random.randint(1,1000000)
				category = "resume_music"
				params = (ID,user,query,category,t)
				c.execute("INSERT INTO commands VALUES (?,?,?,?,?)",params)
				conn.commit()
				resumeMusic()

			elif "temperature" in query:
				if(config["assistant"]["name"] in query):
					query = query.lstrip(config["assistant"]["name"]+" ")
				api_key = "7943cfc4814b521bd57a972383abdcc8"
				words = query.split(" ")
				t = datetime.datetime.now().strftime("%H")
				ID = random.randint(1,1000000)
				category = "temperature"
				params = (ID,user,query,category,t)
				c.execute("INSERT INTO commands VALUES (?,?,?,?,?)",params)
				conn.commit()
				try:
					location = words[5]
					getWeather(api_key,location)
				except Exception as e:
					speak("Please say that again")

			elif ("hostname" in query) or ("host name" in query):
				if(config["assistant"]["name"] in query):
					query = query.lstrip(config["assistant"]["name"]+" ")
				t = datetime.datetime.now().strftime("%H")
				ID = random.randint(1,1000000)
				category = "hostname"
				params = (ID,user,query,category,t)
				c.execute("INSERT INTO commands VALUES (?,?,?,?,?)",params)
				conn.commit()
				getHostName();

			elif "youtube" in query:
				if(config["assistant"]["name"] in query):
					query = query.lstrip(config["assistant"]["name"]+" ")
				t = datetime.datetime.now().strftime("%H")
				ID = random.randint(1,1000000)
				category = "youtube"
				params = (ID,user,query,category,t)
				c.execute("INSERT INTO commands VALUES (?,?,?,?,?)",params)
				conn.commit()
				openYoutubeVideo(query)

			elif "create" in query:
				if(config["assistant"]["name"] in query):
					query = query.lstrip(config["assistant"]["name"]+" ")
				t = datetime.datetime.now().strftime("%H")
				ID = random.randint(1,1000000)
				category = "create"
				params = (ID,user,query,category,t)
				c.execute("INSERT INTO commands VALUES (?,?,?,?,?)",params)
				conn.commit()
				create(query)

			elif "delete" in query:
				if(config["assistant"]["name"] in query):
					query = query.lstrip(config["assistant"]["name"]+" ")
				t = datetime.datetime.now().strftime("%H")
				ID = random.randint(1,1000000)
				category = "delete"
				params = (ID,user,query,category,t)
				c.execute("INSERT INTO commands VALUES (?,?,?,?,?)",params)
				conn.commit()
				delete(query)

			elif "internet speed" in query:
				if(config["assistant"]["name"] in query):
					query = query.lstrip(config["assistant"]["name"]+" ")
				t = datetime.datetime.now().strftime("%H")
				ID = random.randint(1,1000000)
				category = "internet speed"
				params = (ID,user,query,category,t)
				try:
					c.execute("INSERT INTO commands VALUES (?,?,?,?,?)",params)
					conn.commit()
				except Exception as e:
					print("Could not update DB")
				speedTest()

			elif "news" in query:
				if(config["assistant"]["name"] in query):
					query = query.lstrip(config["assistant"]["name"]+" ")
				t = datetime.datetime.now().strftime("%H")
				ID = random.randint(1,1000000)
				category = "news"
				params = (ID,user,query,category,t)
				try:
					c.execute("INSERT INTO commands VALUES (?,?,?,?,?)",params)
					conn.commit()
				except Exception as e:
					print("Could not update DB")
				getNews()

			elif ("spell") in query:
				if(config["assistant"]["name"] in query):
					query = query.lstrip(config["assistant"]["name"]+" ")
				t = datetime.datetime.now().strftime("%H")
				ID = random.randint(1,1000000)
				category = "spell"
				params = (ID,user,query,category,t)
				try:
					c.execute("INSERT INTO commands VALUES (?,?,?,?,?)",params)
					conn.commit()
				except Exception as e:
					print("Could not update DB")
				spell(query)

			elif ("go out" in query) or ("step out" in query) or ("weather check" in query):
				if(config["assistant"]["name"] in query):
					query = query.lstrip(config["assistant"]["name"]+" ")
				t = datetime.datetime.now().strftime("%H")
				ID = random.randint(1,1000000)
				category = "weather_check"
				params = (ID,user,query,category,t)
				try:
					c.execute("INSERT INTO commands VALUES (?,?,?,?,?)",params)
					conn.commit()
				except Exception as e:
					print("Could not update DB")
				api_key = "7943cfc4814b521bd57a972383abdcc8"
				weatherCheck(api_key)

			elif ("goodbye" or "good boy" or "good bye") in query:
				if(config["assistant"]["name"] in query):
					query = query.lstrip(config["assistant"]["name"]+" ")
				speak("goodbye")
				t = datetime.datetime.now().strftime("%H")
				ID = random.randint(1,1000000)
				category = "exit"
				params = (ID,user,query,category,t)
				try:
					c.execute("INSERT INTO commands VALUES (?,?,?,?,?)",params)
					conn.commit()
				except Exception as e:
					print("Could not update DB")
				sys.exit()

			else:
				if(config["assistant"]["name"] in query):
					query = query.lstrip(config["assistant"]["name"]+" ")
				t = datetime.datetime.now().strftime("%H")
				ID = random.randint(1,1000000)
				category = "AI"
				params = (ID,user,query,category,t)
				try:
					c.execute("INSERT INTO commands VALUES (?,?,?,?,?)",params)
					conn.commit()
				except Exception as e:
					print("Could not update DB")
				getBotResponse(query)







