FROM python:3.12.7

RUN apt-get update && apt-get install -y cron

WORKDIR /usr/src/app
COPY . .

RUN mkdir ./images

RUN pip install -r requirements.txt

RUN echo "0 5 * * * python ./get_stasera.py >> /var/log/cron.log 2>&1" > /etc/cron.d/get_tv_program
RUN chmod 0644 /etc/cron.d/get_tv_program
RUN crontab /etc/cron.d/get_tv_program

CMD ["cron", "-f"]
CMD ["python", "-u", "./bot.py"]