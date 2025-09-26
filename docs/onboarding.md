# Onboarding

1. download and install [sqlite3](https://sqlite.org/download.html)

2. clone the repo and cd BabyBites

3. checkout the dan branch
    `git checkout dan`

4. start a python virtual environment
    `python -m venv .venv`

5. activate the python virtual environment
    `source .venv/bin/activate`

6. install dependencies
    `pip install -r requirements.txt`

7. setup database
   `python manage.py migrate`

8. populate allergies
    `python manage.py loaddata allergies.json`

9. create a superuser account
    `python manage.py createsuperuser`

10. launch the backend server
    `python manage.py runserver 0.0.0.0:8080`   

11. go to localhost:8080 in a web browser
    - you can log into the app with the user you just created
    - you can also log into /admin
    - i find it helpful to use the private browsing or incognito option to avoid caching issues
    - i also find it useful to pull up the development tools window (F12 should bring it up)
    - also, if your phone is on the same network as your pc, you can pull up the website on your phone at your-pcs-local-ip:8080 in a browser
