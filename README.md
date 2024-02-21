# MIS4180 Final Project

This is my final project for professor Deng's mis course.

The project is a website where users can share the details of their homes, and the business will turn those details into a hologram. This hologram can be viewed on any device that supports it. The main goal of this project is to focus on how we manage and process the data between the user (client) and the system (server) on the backend.

## Model of data flow:

![](./imgs/dataflow_drawio.png)

## The Tech Stack
- ![Python3](https://www.python.org/)
Responsible for the actual logic and interfacing with SQLite3 and Flask.

- ![Flask](https://flask.palletsprojects.com/en/3.0.x/)
Lightweight web framework for Python

- ![Gunicorn](https://gunicorn.org/)
WSGI HTTP Server for UNIX (because Flask's built-in WSGI is not meant for production).

- ![SQLite](https://www.sqlite.org/index.html)
SQL Satabase Engine.

- ![Vultr](https://www.vultr.com/)
Global Cloud Infrastructure (VPS).

- ![nginx](https://nginx.org/en/)
HTTP and reverse proxy server.

- ![Debian Linux](https://www.debian.org/)
The Operating System the VPS runs (because Windows & MS are disgusting).
