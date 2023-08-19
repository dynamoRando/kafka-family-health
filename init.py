import mysql.connector
import names

host = "localhost"
user = "family_health"
password = "family_health"
db_name = "family_health"

db = mysql.connector.connect(host=host, user=user, password=password, port=23306)

total_families = 4
total_members_per_family = 4
total_doctors = 10


def init_database(db):
    # cur = db.cursor()
    # cur.execute("DROP DATABASE IF EXISTS family_health;")
    # db.commit()
    # cur.execute("CREATE DATABASE IF NOT EXISTS family_health;")
    db = mysql.connector.connect(
        host=host, user=user, password=password, database=db_name, port=23306
    )

    cur = db.cursor()
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS FAMILY 
                (id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                name varchar(50) NOT NULL);
                """
    )

    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS FAMILY_MEMBER
                (id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                family_id INT UNSIGNED NOT NULL,
                name VARCHAR(50) NOT NULL,
                FOREIGN KEY (family_id) REFERENCES FAMILY(id)
                );
                """
    )

    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS DOCTOR
                (id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL
                );
                """
    )

    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS CLAIM
                (id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                 doctor_id INT UNSIGNED NOT NULL,
                 visit_date DATE NOT NULL,
                 family_member_id INT UNSIGNED NOT NULL,
                FOREIGN KEY (family_member_id) REFERENCES FAMILY_MEMBER(id),
                FOREIGN KEY (doctor_id) REFERENCES DOCTOR(id)
                );
                """
    )

    for n in range(total_families):
        name = names.get_last_name().title()
        family_name = []
        family_name.append(name)
        print(family_name)
        sql = "INSERT INTO FAMILY (name) VALUES (%s)"
        cur.execute(sql, (family_name))
        db.commit()

    for n in range(total_families):
        for m in range(total_members_per_family):
            name = names.get_first_name()
            sql = "INSERT INTO FAMILY_MEMBER (family_id, name) VALUES (%s, %s)"
            cur.execute(sql, (n + 1, name))
            db.commit()

    for n in range(total_doctors):
        name = names.get_full_name().title()
        doctor_name = []
        doctor_name.append(name)
        print(doctor_name)
        sql = "INSERT INTO DOCTOR (name) VALUES (%s)"
        cur.execute(sql, (doctor_name))
        db.commit()

    db.commit()


init_database(db)