from django.shortcuts import render, redirect
from .variable import var 

def help(request):
	return render(request,'help.html')

def configure(request):
	if request.GET:
		uname = request.GET['username']
		ulocation = request.GET['userlocation']
		aname = request.GET['assistantname']
		uemail = request.GET['useremail']				
		write_config(uname,ulocation,aname,uemail)


		return redirect("http://127.0.0.1:8000/assistant/")
	return render(request,'configure.html')

def assistant(request):
	f = open("./assistant/interface/variable.py" , 'r')
	print(f)
	reply = [{'question':"Not finding what you want?"},{'answer':"We are solving the issue"}]

	assistant_name = "Voice Assistant"
	user_name = "User"


	if(len(var) < 6):
		reply = var
	else:
		reply = var[-6:]


	return render(request,'home.html', {
		'assistant_name' : assistant_name,
		'user_name' : user_name,
		'reply' : reply, 
		})

def write_config(uname,ulocation,aname,uemail):
	if (uname == "" or ulocation == "" or aname == "" or  uemail == ""):
		print("empty input") 

	else:
		f = open("config.yaml" , 'w') 
		f.write("user: \n")
		l1 = ["	"+"name: "+uname+"\n" , "	"+"location: "+ulocation+"\n"]
		f.writelines(l1)
		f.write("db: <Path to your voiceassistant.db>\n")
		f.write("assistant: \n")
		f.write("	"+"name: "+aname+"\n")
		f.write("music: <Path to your Music directory>\n")
		f.write("application: \n")
		f.write("	"+"intellij: /opt/idea-IC-193.6015.39/bin/idea.sh\n")
		f.write("email: \n")
		l2 = ["	"+"server: smtp.gmail.com\n","	"+"sender_username: <username>\n","	"+"sender_password: <password>\n","	"+"reciever_name: "+uname+"\n","	"+"reciever_mail: "+uemail+"\n"]
		f.writelines(l2)
		f.write("reminders: \n")
		f.write("	"+"dinner: \"21:18:00\"")
		f.close()
		print("Configuration Successful")


	