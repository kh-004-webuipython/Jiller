clone:
	git clone -b dev https://github.com/Phobos-Programmer/Jiller.git GIT_CLONE

build:
	docker-compose build

up:
	docker-compose up -d

stop:
	docker-compose stop


git-pull:
	cd src; git pull
