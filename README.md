# etlman
## Local Setup

**1. Get the project**

First clone the repository from Github and switch to the new directory:

```linux
    $ git clone git@github.com:caktus/etlman.git
    $ cd etlman
```

**2. Set up virtual environment**

Next, set up your virtual environment with Python3. For example, `etlman-venv`
You will note the distinct lack of opinion on how you should manage your
virtual environment. This is by design.

In case you use [direnv](https://direnv.net/).

envrc sample file
```
layout python python3.9

export DATABASE_URL=postgres:///etlman_dev
export USE_DOCKER=no
```


**3. Install dependencies**

This only really needed in case you aren't using docker, in this case you can fetch all dependencies - preferable inside your virtualenv - using the following command:

```
pip install -r requirements/local.txt
```

**4. Pre-commit**

Pre-commit is used to enforce a variety of community standards. CI runs it,
so it's useful to setup the pre-commit hook to catch any issues before pushing
to GitHub and reset your pre-commit cache to make sure that you're starting fresh.

To install, run:

```linux
    (etlman-venv)$ pre-commit clean
    (etlman-venv)$ pre-commit install
```

**5. Postgress**

### Using Docker
If you are unable to run Postgres locally (if you develop on an M1), Docker is a great alternative. See [cookiecutter-django Docker documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html) for more details on Docker for cookiecutter-django.

#### Build the stack

```
(etlman-venv)$ docker-compose -f local.yml build
```

**Note**: Building the stack can take a while

#### Run the stack
To run the stack
```
(etlman-venv)$ docker-compose -f local.yml up
```

If you wish to only run the `django` container (will speed up reload), include `$ export COMPOSE_FILE=local.yml` in your `.envrc` file. After adding the command to the `.envrc` file, run:

```
(etlman-venv)$ docker compose up
(etlman-venv)$ docker compose up -d
```


### Not Using Docker

- Have a postgres instance running either on docker to your local machine, or install it locally
- Create a database with  ```createdb etlman_dev```
- python manage.py migrate
- python manage.py runserver

**6. Migrate and create a superuser**
You'll need to open a bash shell container to run migrate and createsuperuser inside the container.

```
docker-compose exec django bash
root# python manage.py migrate
root# python manage.py createsuperuser
```

**7. Testing**

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:
```
(etlman-venv)$ coverage run -m pytest
(etlman-venv)$ coverage html
(etlman-venv)$ open htmlcov/index.html
```

### Running tests with pytest

```
(etlman-venv)$ pytest
```
