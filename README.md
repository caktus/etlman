# etlman
## Local Setup

**1. Get the project**

First clone the repository from Github and switch to the new directory:

```
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

This is needed only if you are not using Docker - in such case fetch all dependencies (preferable inside your virtualenv), run:

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
    (etlman-venv)$ pre-commit run --all-files
```

**5. Postgress**

### Using Docker
If you are unable to run Postgres locally (if you develop on an M1), Docker is a great alternative. See [cookiecutter-django Docker documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html) for more details on the Docker setup.

#### Build the stack

```
(etlman-venv)$ docker-compose -f local.yml build
```

**Note**: Building the stack can take a while

See detailed [cookiecutter-django Docker documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html).

#### Run the stack

To run the stack
```
(etlman-venv)$ docker-compose -f local.yml up
```

If you wish to only run the `django` container (will speed up reload), include `$ export COMPOSE_FILE=local.yml` in your `.envrc` file. After adding the command to the `.envrc` file, run:

```
(etlman-venv)$ docker compose up
(etlman-venv)$ docker compose up -d (detached mode)
```


### Not Using Docker

1.  Create a database with  ```createdb etlman_dev```
2. python manage.py migrate
3. python manage.py runserver

**6. Exec into the Docker container(only if developing in Docker)**
You'll need to open a bash shell container to run migrate and createsuperuser inside the container.

```
docker-compose exec django bash
```

**7. Migrate and Create a super user**

```
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

### Custom Bootstrap Compilation

The generated CSS is set up with automatic Bootstrap recompilation with variables of your choice.
Bootstrap v5 is installed using npm and customised by tweaking your variables in `static/sass/custom_bootstrap_vars`.

You can find a list of available variables [in the bootstrap source](https://github.com/twbs/bootstrap/blob/main/scss/_variables.scss), or get explanations on them in the [Bootstrap docs](https://getbootstrap.com/docs/5.1/customize/sass/).

Bootstrap's javascript as well as its dependencies is concatenated into a single file: `static/js/vendors.js`.
