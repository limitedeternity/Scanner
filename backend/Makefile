run:
	gunicorn -b 0.0.0.0:8080 --worker-class=eventlet --worker-connections=1000 --workers=1 scan_server:app

install:
	pip3 install -r requirements.txt
