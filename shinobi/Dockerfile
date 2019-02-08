FROM node:11-stretch

RUN apt-get update && apt-get install -y \
	ffmpeg \
	curl

RUN cd /tmp && \
	curl https://gitlab.com/Shinobi-Systems/Shinobi/-/archive/master/Shinobi-master.tar.gz > shinobi.tar.gz && \
	tar -xzf shinobi.tar.gz && \
	rm shinobi.tar.gz && \
	mv Shinobi* /opt/shinobi && \
	cd /opt/shinobi && \
	npm install

CMD ["node", "/opt/shinobi/camera.js"]

 
