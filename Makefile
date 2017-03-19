clone:
	git clone https://github.com/akimul/Notebook.git src

build:
	docker-compose build

up:
	docker-compose up -d

start:
	docker-compose start

stop:
	docker-compose stop

restart:
	stop start

git-pull:
	cd src; git pull

shell:
docker exec -ti notebook bash