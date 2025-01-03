FROM python:3.12.7

RUN apt-get update && apt-get install -y cron

WORKDIR /usr/src/app
COPY bot.py get_stasera.py requirements.txt canali.json start.sh .

RUN pip install -r requirements.txt

RUN echo "0 8 * * * /usr/local/bin/python /usr/src/app/get_stasera.py >> /usr/src/app/data/cron.log 2>&1" > /etc/cron.d/get_tv_program
RUN chmod 0644 /etc/cron.d/get_tv_program
RUN crontab /etc/cron.d/get_tv_program

RUN chmod +x ./start.sh
CMD ./start.sh