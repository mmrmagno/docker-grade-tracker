FROM python:3.11.3

WORKDIR /usr/src/app

COPY . .

RUN python3 grade-tracker/app/requirements.py

CMD [ "python", "grade-tracker/app/main.py" ]