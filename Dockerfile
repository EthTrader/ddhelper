FROM python:3-alpine

WORKDIR /usr/src/app

RUN pip3 install pipenv

COPY Pipfile* ./
RUN pipenv install

COPY src/app.py .

CMD [ "pipenv", "run", "python3", "./app.py" ]