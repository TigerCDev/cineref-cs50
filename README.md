# CineRef (CS50x Final Project)

A web app for cinematographers and film students to upload, browse, 
and organize shot references by visual and technical metadata.

Built as my CS50x final project.

## What it does

- Register and log in with hashed passwords (PBKDF2)
- Upload shot images with metadata: shot type, shot size, 
  aspect ratio, interior/exterior, time of day, cinematographer, director
- Browse all shots from all users in random order
- View detailed metadata for any individual shot
- Visit user profiles to see their uploaded shots
- Organize shots into personal collections

## Stack

- Python + Flask
- SQLite via CS50's SQL library
- Flask-Session for server-side sessions
- Werkzeug for password hashing and secure file uploads
- Jinja2 templates

## How to run

pip install -r requirements.txt
flask run

## Notes

This is the original Flask/SQLite version built for CS50x.
The same project is being rebuilt as a production-grade REST API 
using Django, DRF, PostgreSQL, Docker, and JWT auth — 
see [cineref-api](https://github.com/TigerCDev/cineref-api).
