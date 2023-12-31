# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

FROM python:3.10-slim

WORKDIR /app

ADD Pipfile .
RUN pip install pipenv
RUN pipenv install

ADD src .
ADD .env .

ENTRYPOINT [ "pipenv", "run" ]
CMD [ "python", "main.py" ]
