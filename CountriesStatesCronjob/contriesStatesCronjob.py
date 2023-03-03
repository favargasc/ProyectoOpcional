import requests
import sys
import mariadb
import os
from dotenv import load_dotenv
import hashlib
import datetime

load_dotenv()


class CountriesStatesCronJob:
    def __init__(self):
        try:
            self.connection = mariadb.connect(
                user=os.getenv('DB_USER_NAME'),
                password=os.getenv('DB_PASSWORD'),
                host=os.getenv('DB_HOST'),
                port=int(os.getenv('DB_PORT')),
                database=os.getenv('DB_DATABASE')
            )

        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(1)

        self.cursor = self.connection.cursor()

    def add_countries(self):
        statement = 'INSERT INTO countries (code,name) VALUES (?, ?)'
        countries_url = os.getenv('COUNTRIES_URL')

        if self._insert_into_db(countries_url, statement):
            print('The information has been successfully inserted into the countries table')
        else:
            print('The information had already been in the countries table')

    def add_states(self):
        statement = 'INSERT IGNORE INTO states (code,name) VALUES (?, ?)'
        states_url = os.getenv('STATES_URL')
        if self._insert_into_db(states_url, statement):
            print('The information has been successfully inserted into the states table')
        else:
            print('The information had already been in the states table')

    def _insert_into_db(self, url, statement):
        data = requests.get(url).text
        md5 = hashlib.md5(bytes(data, 'utf8')).hexdigest()

        if not self._is_available(md5):
            return False
        else:
            for row in data.split('\n'):
                if row.strip():
                    code = row[:2]
                    name = row[3:]
                    self.cursor.execute(statement, (code, name))
            self._update_files(md5, url)
        self.connection.commit()
        return True

    def _update_files(self, md5, url):
        statement = 'INSERT IGNORE INTO files (md5, fileName, url, processingDay, status) VALUES (?, ?, ?, ?, ?)'
        file_name = url.split('/')[-1]
        date = datetime.datetime.now()

        self.cursor.execute(statement, (md5, file_name, url, date, 'PROCESADO'))
        self.connection.commit()
        print('the files table has been updated')

    def close_connection(self):
        self.connection.close()

    def _is_available(self, md5):
        try:
            statement = "SELECT COUNT(*) FROM files WHERE md5 = %s"
            self.cursor.execute(statement, (md5,))

            (number_of_rows,) = self.cursor.fetchone()
            return True if number_of_rows == 0 else False

        except mariadb.Error as e:
            print(f"Error retrieving entry from database: {e}")


def main():
    csc = CountriesStatesCronJob()
    csc.add_countries()
    csc.add_states()
    csc.close_connection()

if __name__ == "__main__":
    main()
