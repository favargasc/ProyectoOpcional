import requests
import sys
import mariadb
import os
from dotenv import load_dotenv
import hashlib
import datetime


load_dotenv()


class StationsCronjob:
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

    def add_stations(self):
        statement = 'INSERT IGNORE INTO stations(country_id, state_id, id, latitude, longitude, elevation, state, name, gns_flag, hcn_crn_flag, wmo_id) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        stations_url = 'https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt'
        if self._insert_into_db(stations_url, statement):
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
                    country_id = row[:2]
                    id = row[:11]
                    latitude = row[13:20]
                    longitude = row[21:30]
                    elevation = row[31:37]
                    state = row[38:40]
                    name = row[41:71]
                    gns_flag = row[72:75]
                    hcn_crn_flag = row[76:79]
                    wmo_id = row[80:]

                    if (state == '  '):
                        state = 'UNK'

                    self.cursor.execute(statement, (country_id, state, id, latitude,
                                        longitude, elevation, state, name, gns_flag, hcn_crn_flag, wmo_id))
            self._update_files(md5, url)
        self.connection.commit()
        return True

    def _update_files(self, md5, url):
        statement = 'INSERT IGNORE INTO files (md5, fileName, url, processingDay, status) VALUES (?, ?, ?, ?, ?)'
        file_name = url.split('/')[-1]
        date = datetime.datetime.now()

        self.cursor.execute(
            statement, (md5, file_name, url, date, 2))
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
    csc = StationsCronjob()
    csc.add_stations()
    csc.close_connection()


if __name__ == "__main__":
    main()
