# Installation

## Run server Directly

### Requirement

- Python >= 3.9

### Steps

Clone project from GitHub

```bash
git clone https://github.com/PelerYuan/KnowledgeShare.git
```

Go into the folder

```bash
cd KnowledgeShare
```

Install dependence

```bash
pip install -r requirements.txt
```

Make migrations respectively

```bash
python manage.py makemigrations accounts
python manage.py makemigrations boards
```

Migrate

```bash
python manage.py migrate
```

Run server

```bash
python manage.py runserver
```

If everything is correct, visit http://127.0.0.1:8000/ now, and you can see the page:

![image-20240915084541977](/deploy.assets/image-20240915084541977.png)

### Create administrator account

Use following code to create an administrator account

```bash
python manage.py createsuperuser
```

## Run server by Docker

### Requirement

- Python >= 3.9
- docker
- docker-compose

### Start

Clone project from GitHub

```bash
git clone https://github.com/PelerYuan/KnowledgeShare.git
```

Go into the folder

```bash
cd KnowledgeShare
```

start docker

```bash
sudo docker-compose up --build
```

### Stop

```bash
sudo docker-compose down
```
