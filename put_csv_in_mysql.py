import csv
import pymysql

conn = pymysql.connect(host="192.168.1.131", user="root", password="parola", database="test")

cursor = conn.cursor()
csv_data = csv.reader(open('emag_placi_video.csv'))
header = next(csv_data)

print('Importing the CSV Files')
for row in csv_data:
    print(row)
    cursor.execute(
        'INSERT INTO produse (pret,descriere,link) VALUES (%s, %s, %s)', row)

conn.commit()
cursor.close()
print('Done')