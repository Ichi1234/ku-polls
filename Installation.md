## Installation Guide:

1. Clone this repositorie
```
git clone <repository link>
```

2. Create python environment
```
python -m venv .venv
```

3. Activate the virtual environment
      
   On Linux or MacOS
   ```
   source venv/bin/activate
   ```
   On Windows
   ```
   venv\Scripts\activate
   ```
   
4. Install All packages
```
pip install -r requirements.txt
```

5. Set Values For Externalized Variables

      For macOS/Linux
      ```
      cp sample.env .env
      ```
      
      For Windows
      ```
      copy sample.env .env
      ```

6. Initailize Database
```
python ./manage.py migrate
```

7. run tests
```
python manage.py test
```

8. Load Polls Data Into Database
```
python manage.py loaddata data/<filename>
```

