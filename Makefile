clone:
	git clone -b digitalocean https://github.com/Phobos-Programmer/Jiller.git src

build:
	docker-compose build

up:
	docker-compose up -d

stop:
	docker-compose stop


git-pull:
	cd src; git pull
