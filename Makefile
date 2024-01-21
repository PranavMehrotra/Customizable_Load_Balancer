IMAGES := `sudo docker images -aq`
CONTAINERS := `sudo docker ps -aq`

deploy: clean
	sudo docker-compose up

install: build servers

build:
	sudo docker-compose build

servers:
	sudo docker build -t server_img ./server

clean:
	-sudo docker stop $(CONTAINERS)
	-sudo docker container prune -f

deepclean: clean
	-sudo docker rmi $(IMAGES)