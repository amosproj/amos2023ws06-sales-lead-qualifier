FROM python:3.10-slim

WORKDIR /app

ADD Pipfile .
ADD src src/

RUN pip install pipenv
RUN pipenv install

ENTRYPOINT [ "pipenv", "run" ]
CMD [ "python", "src/main.py" ]
