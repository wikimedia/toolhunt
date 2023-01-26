# toolhunt

# Description

Toolhunt is a web application for editing Toolhub records in a fun and easy way.
It allows users to view and add missing fields for tools in Toolhub.

This repository contains the project backend.
The frontend can be found in the [toolhunt-ui repository](https://github.com/wikimedia/toolhunt-ui).

This is an [Outreachy](https://www.outreachy.org/) Internship project.

## Issue Tracker

This project uses [Phabricator](https://phabricator.wikimedia.org/project/board/6283/) to track issues and we would advice against using Github issue traking for bugs

## Setup/Installation Requirements

- Clone this repo to your machine with the command `git clone https://github.com/wikimedia/toolhunt.git`
- `cd toolhunt`

### To run locally

- Install Poetry and Flask if needed
- `poetry run flask run`
- Open a browser window to localhost:5000

### To run with Docker

- `docker-compose up --build --detach`
- Open a browser window to localhost:5000

### To start and check the Database

- `docker-compose exec flask-web python manage.py create_db`
- `docker exec -it mariadb mariadb --user user -p mydatabase` (password: mypassword)
- From the MariaDB command line: `SHOW TABLES;`

## Technologies to be Used

- Python
- Flask
- Redis
- Docker
- MariaDB
