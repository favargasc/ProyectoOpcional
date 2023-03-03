import requests
import lxml.html as lh
import pika
import datetime
import json
import mariadb
import sys
from dotenv import load_dotenv
import os
import time
import hashlib

load_dotenv()


class OrchestratorCronJob():
    url = 'https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/'
    data = []

    def __init__(self):
        self.rabbitqm_conn = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='localhost'
            )
        )

        self.channel = self.rabbitqm_conn.channel()

        self.channel.queue_declare(queue='TO_PROCESS', durable=True)

        try:
            self.mariadb_conn = mariadb.connect(
                user=os.getenv('DB_USER_NAME'),
                password=os.getenv('DB_PASSWORD'),
                host=os.getenv('DB_HOST'),
                port=int(os.getenv('DB_PORT')),
                database=os.getenv('DB_DATABASE')
            )

        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(1)
        self.cursor = self.mariadb_conn.cursor()

    def list_data(self):
        file = lh.fromstring(requests.get(self.url).content)

        for element in file.xpath('//tr')[3:-2]:
            self.data.append(element.text_content()[:15])
            print(element.text_content()[:15])

    def publish_message(self):
        self.list_data()

        for message in self.data:
            self.channel.basic_publish(
                exchange='',
                routing_key='TO_PROCESS',
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2
                )
            )

            self._update_files('null', self.url + message)
            print(" [x] Sent %r" % message)
        self.rabbitqm_conn.close()
        self.mariadb_conn.close()

    def receive_message(self):
        def callback(ch, method, properties, body):
            message = body.decode("utf-8")
            print(" [x] Received %r" % message)
            time.sleep(2)

            data = requests.get(self.url + message).text
            md5 = hashlib.md5(bytes(data, 'utf8')).hexdigest()

        self.channel.basic_consume(
            queue='TO_PROCESS', on_message_callback=callback)

        print(' [*] Waiting for messages. To exit press CTRL+C')
        self.channel.start_consuming()
        self.rabbitqm_conn.close()

    def _update_files(self, md5, url):
        statement = 'INSERT IGNORE INTO files (md5, file_name, url, processing_date, status_id) VALUES (?, ?, ?, ?, ?)'
        file_name = url.split('/')[-1]
        date = datetime.datetime.now()

        self.cursor.execute(
            statement, (md5, file_name, url, date, 2))
        self.mariadb_conn.commit()
        print('the files table has been updated')
