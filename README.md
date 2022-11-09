# etlman

## Local Setup

### 1. Get the project

First clone the repository from Github and switch to the new directory:

```
git clone git@github.com:caktus/etlman.git
cd etlman
```

### 2. Set up virtual environment

[direnv](https://direnv.net/) is recommended for managing your local Python virtual environment and shell environment variables. Once installed, add the following to a file called `.envrc` in the root of the `etlman/` directory:

```sh
# .envrc
layout python python3.9

export CELERY_BROKER_URL=redis://localhost:6379
export DATABASE_URL=postgres:///etlman_dev
export USE_DOCKER=true
export COMPOSE_FILE=local.yml
export PATH="node_modules/.bin/:$PATH"
```

When prompted, run:

```sh
direnv allow
```

(If you received no prompt after saving `.envrc`, direnv might not be installed properly.)

### 3. Install dependencies

If you **don't** intend to use Docker to develop, install requirements locally:

```sh
pip install -r requirements/local.txt
npm install
npm run dev
```

### 4. Pre-commit

Pre-commit is used to enforce a variety of community standards. CI runs it,
so it's useful to setup the pre-commit hook to catch any issues before pushing
to GitHub and reset your pre-commit cache to make sure that you're starting fresh.

To install, run:

```sh
pre-commit clean
pre-commit install
pre-commit run --all-files
```

### 5. Postgres

#### Using Docker

If you are unable to run Postgres locally (if you develop on an M1), Docker is a great alternative. See [cookiecutter-django Docker documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html) for more details on the Docker setup.

##### Build the stack

```sh
docker-compose build
```

**Note**: Building the stack can take a while

See detailed [cookiecutter-django Docker documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html).

##### Run the stack

```sh
docker-compose up
```

This causes docker to run in the foreground, so you will need to open another terminal to continue.

Alternatively:

```sh
docker-compose up -d
```

Adding -d indicates running docker in "detached mode" which allows you to continue using the same terminal window.

#### Not Using Docker

If not using Docker, you can create the database using a local Postgres installation and run migrations:

```sh
createdb etlman_dev
python manage.py migrate
python manage.py runserver
```

If not using ident authentication, you might need to update the `DATABASE_URL` in your `.envrc`.

### 6. Exec into the Docker container (if developing in Docker)

You'll need to open a bash shell container to run migrate and createsuperuser inside the container:

```sh
docker-compose run --rm django bash
```

### 7. Migrate and Create a super user

**Note**: When creating a super user, you must provide an email address. If you fail to provide an email address, you will not be able to verify your account (via the link in the email printed to the console) nor login to the system.

```sh
python manage.py migrate
python manage.py createsuperuser
```

After creating an account, navigate to http://localhost:3000/ to login. On first login, you will be prompted to verify your account. You should see the verification email in the console output from the `etlman_local_django` container (or runserver, if running locally).

## Testing

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

```sh
coverage run -m pytest
coverage report -m
```

Alternatively, to view the report in HTML:

```sh
coverage html
open htmlcov/index.html
```

## Webpack

If you make any changes to index.js or webpack.config.js, re-build the js & css bundles by running:

```sh
npm run build
```

To run webpack continuously to watch for updates you are making to the build in realtime, run:

```sh
npm run webpack-watch
```

## Custom Bootstrap Compilation

The generated CSS is set up with automatic Bootstrap recompilation with variables of your choice.
Bootstrap v5 is installed using npm and customised by tweaking your variables in `static/sass/custom_bootstrap_vars`.

You can find a list of available variables [in the bootstrap source](https://github.com/twbs/bootstrap/blob/main/scss/_variables.scss), or get explanations on them in the [Bootstrap docs](https://getbootstrap.com/docs/5.1/customize/sass/).

Bootstrap's javascript as well as its dependencies is concatenated into a single file: `static/js/app.js`.
