## KU Polls: Online Survey Questions 
![Test Status](https://github.com/Ichi1234/ku-polls/actions/workflows/django.yml/badge.svg)

An application to conduct online polls and surveys based
on the [Django Tutorial project](https://docs.djangoproject.com/en/5.0/intro/tutorial01/), with
additional features.

This app was created as part of the [Individual Software Process](
https://cpske.github.io/ISP) course at [Kasetsart University](https://www.ku.ac.th).

## Requirement:

* Python 3.11 >=
  
## Installation Guide:

1. Clone this repositorie
```
git clone <repository link>
```

2. Create python environment
```
python -m venv .venv
```

3. Install All packages
```
pip install -r requirements.txt
```

4. Initailize Database
```
python ./manage.py migrate
```

5. Load Polls Data Into Database
```
python manage.py loaddata data/<filename>
```

## Run:

Use this command to run the sever the default server is [localhost:8000](http://localhost:8000)
```
python ./manage.py runserver
```
## Project Documents:

All project documents are in the [Project Wiki](../../wiki/Home).

- [Vision and Scope](../../wiki/Vision%20and%20Scope)
- [Requirements](../../wiki/Requirements)
- [Project Plan](../../wiki/Project%20Plan)
- [Domain Model](../../wiki/Domain%20Model)




