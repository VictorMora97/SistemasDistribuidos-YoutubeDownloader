off:
	sudo systemctl stop icegridregistry
	sudo systemctl stop icegridnode

1:
	icebox --Ice.Config=icebox.config 

2:
	mkdir -p /tmp/db/node1
	mkdir -p /tmp/db/registry
	icegridnode --Ice.Config=node1.config

3:
	./synctimer.py --Ice.Config=synctimer.config

4:
	./downloader.py --Ice.Config=downloader.config

5:
	./cliente.py --Ice.Config=cliente.config 


distribucion:
	mkdir -p /tmp/Downloader
	cp downloader.py /tmp/Downloader
	cp synctimer.py /tmp/Downloader
	cp cliente.py /tmp/Downloader
	cp downloader.ice /tmp/Downloader
	cp work_queue.py /tmp/Downloader
	cp downloader_scheduler.py /tmp/Downloader
	chmod +rwx /tmp/Downloader/cliente.py
	chmod +rwx /tmp/Downloader/downloader.py
	chmod +rwx /tmp/Downloader/synctimer.py
	icepatch2calc /tmp/Downloader






