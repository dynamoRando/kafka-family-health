import mysql.connector
import names

host = "localhost"
user = "root"
password = "family_health"
db_name = "family_health"
db_name_clone = db_name + "_clone"

db = mysql.connector.connect(host=host, user=user, password=password, port=23306)

total_families = 4
total_members_per_family = 4
total_doctors = 10


sql_create_family_table = """
    CREATE TABLE IF NOT EXISTS FAMILY 
                (id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                name varchar(50) NOT NULL);
                """

sql_create_family_member_table = """
    CREATE TABLE IF NOT EXISTS FAMILY_MEMBER
                (id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                family_id INT UNSIGNED NOT NULL,
                name VARCHAR(50) NOT NULL,
                FOREIGN KEY (family_id) REFERENCES FAMILY(id)
                );
                """

sql_create_doctor_table = """
    CREATE TABLE IF NOT EXISTS DOCTOR
                (id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL
                );
                """

sql_create_claim_table = """
    CREATE TABLE IF NOT EXISTS CLAIM
                (id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                 doctor_id INT UNSIGNED NOT NULL,
                 visit_date DATE NOT NULL,
                 family_member_id INT UNSIGNED NOT NULL,
                 amount INT UNSIGNED NOT NULL,
                FOREIGN KEY (family_member_id) REFERENCES FAMILY_MEMBER(id),
                FOREIGN KEY (doctor_id) REFERENCES DOCTOR(id)
                );
                """

sql_create_payment_table = """
    CREATE TABLE IF NOT EXISTS PAYMENT
                (id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                 family_member_id INT UNSIGNED NOT NULL,
                 claim_id INT UNSIGNED NOT NULL,
                 amount INT UNSIGNED NOT NULL,
                 payment_date DATE NOT NULL,
                FOREIGN KEY (family_member_id) REFERENCES FAMILY_MEMBER(id),
                FOREIGN KEY (claim_id) REFERENCES CLAIM(id)
                );
                """

sql_grant_perms = """
GRANT ALL PRIVILEGES ON *.* TO 'family_health'@'%';
FLUSH PRIVILEGES;
"""


def init_database(db):
    cur = db.cursor()
    cur.execute("DROP DATABASE IF EXISTS family_health_clone;")
    db.commit()
    cur.execute("CREATE DATABASE IF NOT EXISTS family_health_clone;")
    db = mysql.connector.connect(
        host=host, user=user, password=password, database=db_name, port=23306
    )

    cur = db.cursor()
    cur.execute(sql_create_family_table)
    cur.execute(sql_create_family_member_table)
    cur.execute(sql_create_doctor_table)
    cur.execute(sql_create_claim_table)
    cur.execute(sql_create_payment_table)

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

    # create structures in clone database
    db = mysql.connector.connect(
        host=host, user=user, password=password, database=db_name_clone, port=23306
    )
    cur = db.cursor()
    cur.execute(sql_create_family_table)
    cur.execute(sql_create_family_member_table)
    cur.execute(sql_create_doctor_table)
    cur.execute(sql_create_claim_table)
    cur.execute(sql_create_payment_table)
    db.commit()


init_database(db)
