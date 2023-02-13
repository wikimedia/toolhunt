# toolhunt

# Description

Toolhunt is a web application for editing Toolhub records in a fun and easy way.
It allows users to view and add missing fields for tools in Toolhub.

This repository contains the project backend.
The frontend can be found in the [toolhunt-ui repository](https://github.com/wikimedia/toolhunt-ui).

This is an [Outreachy](https://www.outreachy.org/) Internship project.

## Issue Tracker

This project uses [Phabricator](https://phabricator.wikimedia.org/project/board/6283/) to track issues and we would advice against using Github issue traking for bugs

## Documentation

API documentation is automatically generated by Swagger and can be accessed (while the app is running) at `localhost:5000/api/documentation`

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

### To initialize the Database

- From the command line, `docker-compose exec flask-web flask db upgrade`

### To access the Database

- From the command line, `docker exec -it mariadb mariadb --user user -p mydatabase` (password: mypassword)

### Adding bulk data to the Database

Whether you're working with the mock data or "real" data, the contents of the `field` table will remain the same.

- From the command line, `docker-compose exec flask-web python manage.py insert_fields`

#### To insert mock data into the Database

The mock data includes two tools and a selection of tasks, both complete and incomplete

- From the command line, `docker-compose exec flask-web python manage.py insert_mock_data`

#### To insert "real" data into the Database

- From the command line, `docker-compose exec flask-web python manage.py populate_db`

The fetch request currently draws data from the Toolhub Test Server. To get the **real** real data, open `api/jobs/get_tools.py` and switch from `TOOL_TEST_API_ENDPOINT` to `TOOL_API_ENDPOINT`

## Technologies to be Used

- Python
- Flask
- Redis
- Docker
- MariaDB
