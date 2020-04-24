#gnome-terminal -e python3 ./assistant/manage.py runserver
gnome-terminal --tab --title="UI-server" --command="bash -c 'python3 ./assistant/manage.py runserver; $SHELL'"
gnome-terminal --tab --title="Code-server" --command="bash -c 'python3 Code.py; $SHELL'"
sleep 4
gnome-terminal --tab --title="WebBrowser" --command="bash -c 'google-chrome http://127.0.0.1:8000/assistant; $SHELL'"
