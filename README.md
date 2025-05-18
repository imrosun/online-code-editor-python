## Prerequistes 

Python should be installed 

## Steps to setup django app locally

Open any newly created folder using vs code or any other IDE. folder name ex: online-code-editor
Go to terminal and follow below steps.

1. First create virtual environment
```bash
python -m venv myenvonline
```

2. To activate venv
```bash 
.\myenvonline\Scripts\activate
```

3. Install django
```bash
pip install django
```

4. To create project 
```bash
git clone https://github.com/imrosun/online-code-editor-python.git
OR
django-admin startproject onlinecode
```

Skip if cloned
5. To create app inside project 
```bash
cd onlinecode
python manage.py startapp codeeditor
```
After this add app {'codeeditor'} inside INSTALLED_APPS on settings.py file

6. To run server
```bash
python manage.py runserver
```

7. To host on vercel 
Step 1: Go to /onlinecode/settings.py
        Update ALLOWED_HOSTS = ['.vercel.app']
Step 2: Generate requirments.txt using command
```bash
pip freeze > requirements.txt
```
Step 3: Create vercel.json file in app folder or manage.py path

