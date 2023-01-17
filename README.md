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

- Clone this repo to your machine
- `git clone https://github.com/wikimedia/toolhunt.git`
- `cd toolhunt`

### To run locally

- Install Poetry and Flask if they aren't installed locally
- `poetry run flask run`
- Open a browser window to localhost:5000

### To run with Docker

- `docker build -t toolhunt_front_img .`
- `docker run -d --rm -p 5000:5000 --name toolhunt_frontend toolhunt_front_img`
- Open a browser window to localhost:5000

## Technologies to be Used

- Python
- Flask
- Redis

## To do

- Write docker-compose.yml
