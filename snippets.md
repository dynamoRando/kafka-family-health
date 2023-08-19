# Grant perms to user

```
GRANT ALL PRIVILEGES ON *.* TO 'family_health'@'%';
FLUSH PRIVILEGES;
```

# Kafka-UI settings

| Item              | Value                                        |
| ----------------- | -------------------------------------------- |
| Cluster Name      | family-health                                |
| Bootstrap Servers | kafka-1:9092                                 |
| Schema Registry   | http://schema-registry:8081                  |
| Kafka Connect     | Connect-Cluster, http://kafka-connect-1:8083 |
| Ksqldb            | http://ksqldb-server-1:8088                  |


# Validate the Debezium connector

Instructs Debezium to connect to our database and to follow the specified tables. We also will attempt to flatten out records from Debezium's normal BEFORE/AFTER fields into something simpler using the the `ExtractNewRecordState` SMT (Single Messsage Transform). Finally, we'll also convert any DATE fields from Unix epoch into a date string.

Note that this is against the `validate` endpoint.

```
 curl -X PUT http://localhost:8083/connector-plugins/io.debezium.connector.mysql.MySqlConnector/config/validate -H "Content-Type: application/json" -d '{ 
    "connector.class": "io.debezium.connector.mysql.MySqlConnector",
    "database.user": "family_health",
    "database.server.id": "1",
    "tasks.max": "1",
    "schema.history.internal.kafka.bootstrap.servers": "kafka-1:9092",
    "database.port": "3306",
    "topic.prefix": "family_health_0",
    "schema.history.internal.kafka.topic": "schema-changes.health.0",
    "database.hostname": "db",
    "database.password": "family_health",
    "name": "source_family_health_0",
    "database.allowPublicKeyRetrieval":"true",
    "database.history.kafka.bootstrap.servers": "kafka-1:9092",
    "database.history.kafka.topic": "family_health-history",
    "database.server.name" : "family_health_0",
    "database.include.list": "family_health",
    "transforms":"unwrap, ts, ts2",
    "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
    "transforms.unwrap.drop.tombstones" : "true",
    "transforms.unwrap.delete.handling.mode":"drop",
    "transforms.ts.type":"org.apache.kafka.connect.transforms.TimestampConverter$Value",
    "transforms.ts.format": "yyyy-MM-dd",
    "transforms.ts.target.type": "string", 
    "transforms.ts.field":"visit_date",
    "transforms.ts2.type":"org.apache.kafka.connect.transforms.TimestampConverter$Value",
    "transforms.ts2.format": "yyyy-MM-dd",
    "transforms.ts2.target.type": "string", 
    "transforms.ts2.field":"payment_date",
    "time.precision.mode":"connect",
    "key.converter.schemas.enable":"true",
    "value.converter.schemas.enable":"true",
    "key.converter": "io.confluent.connect.avro.AvroConverter",
    "key.converter.schema.registry.url": "http://schema-registry:8081",
    "table_include_list":"DOCTOR,CLAIM,FAMILY,FAMILY_MEMBER,PAYMENT"
 }';
```

# Create the Debezium connector

Now, do it for real:

```
curl -i -X PUT -H "Accept:application/json" \
    -H  "Content-Type:application/json" http://localhost:8083/connectors/source_family_health_0/config \
    -d '{ 
    "connector.class": "io.debezium.connector.mysql.MySqlConnector",
    "database.user": "family_health",
    "database.server.id": "1",
    "tasks.max": "1",
    "schema.history.internal.kafka.bootstrap.servers": "kafka-1:9092",
    "database.port": "3306",
    "topic.prefix": "family_health_0",
    "schema.history.internal.kafka.topic": "schema-changes.health.0",
    "database.hostname": "db",
    "database.password": "family_health",
    "name": "source_family_health_0",
    "database.allowPublicKeyRetrieval":"true",
    "database.history.kafka.bootstrap.servers": "kafka-1:9092",
    "database.history.kafka.topic": "family_health-history",
    "database.server.name" : "family_health_0",
    "database.include.list": "family_health",
    "transforms":"unwrap, ts, ts2",
    "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
    "transforms.unwrap.drop.tombstones" : "true",
    "transforms.unwrap.delete.handling.mode":"drop",
    "transforms.ts.type":"org.apache.kafka.connect.transforms.TimestampConverter$Value",
    "transforms.ts.format": "yyyy-MM-dd",
    "transforms.ts.target.type": "string", 
    "transforms.ts.field":"visit_date",
    "transforms.ts2.type":"org.apache.kafka.connect.transforms.TimestampConverter$Value",
    "transforms.ts2.format": "yyyy-MM-dd",
    "transforms.ts2.target.type": "string", 
    "transforms.ts2.field":"payment_date",
    "time.precision.mode":"connect",
    "key.converter.schemas.enable":"true",
    "value.converter.schemas.enable":"true",
    "key.converter": "io.confluent.connect.avro.AvroConverter",
    "key.converter.schema.registry.url": "http://schema-registry:8081",
    "table_include_list":"DOCTOR,CLAIM,FAMILY,FAMILY_MEMBER,PAYMENT"
 }';
```

# Create a "plain" Debezium connector.

This is an alternative example of creating a Debezium connector for the same data. It leaves the BEFORE/AFTER format for rows in the Kafka topic's records. Note that we won't use these topics that are created as part of any sinks. They're just here to show what happens from Debezium with the BEFORE/AFTER state.

```
curl -i -X PUT -H "Accept:application/json" \
    -H  "Content-Type:application/json" http://localhost:8083/connectors/source_family_health_1_dnu/config \
    -d '{ 
    "connector.class": "io.debezium.connector.mysql.MySqlConnector",
    "database.user": "family_health",
    "database.server.id": "2",
    "tasks.max": "1",
    "schema.history.internal.kafka.bootstrap.servers": "kafka-1:9092",
    "database.port": "3306",
    "topic.prefix": "family_health_1_dnu",
    "schema.history.internal.kafka.topic": "schema-changes.health.2",
    "database.hostname": "db",
    "database.password": "family_health",
    "name": "source_family_health_1_dnu",
    "database.allowPublicKeyRetrieval":"true",
    "database.history.kafka.bootstrap.servers": "kafka-1:9092",
    "database.history.kafka.topic": "family_health-history-1",
    "database.server.name" : "family_health_1",
    "database.include.list": "family_health",
    "table_include_list":"DOCTOR,CLAIM,FAMILY,FAMILY_MEMBER,PAYMENT"
 }';
```

# Insert test CLAIM and PAYMENT
```sql
INSERT INTO CLAIM (doctor_id, visit_date, family_member_id, amount) VALUES (1, '2023-01-01', 1, 500);
INSERT INTO CLAIM (doctor_id, visit_date, family_member_id, amount) VALUES (1, '2023-01-02', 3, 700);
INSERT INTO PAYMENT(family_member_id, claim_id, amount, payment_date) VALUES(2, 1, 100, '2023-01-31');
```

# Create a JDBC sink to mirror data from the FAMILY_MEMBER topic 

This creates a sink against the "family_health_clone" database and pulls messages from the `family_health_00.family_health.FAMILY_MEMBER` topic to sink into the corresponding same named table. We apply a few transforms: one to route message thru a REGEX to remove any components in the record in the topic to replace anything that won't work with SQL. We also apply an unwrap to that, and finally we pull out the key for the record out of the value of the record, using the "id" field. This is so that when we sink the record into our "clone" database, instead of using the key value in the record of the topic (which looks like `Struct{id=1}`), we'll instead extract it from the value of the record in the topic.

```
curl -i -X PUT -H "Accept:application/json" \
    -H  "Content-Type:application/json" http://localhost:8083/connectors/sink_family_health_clone_family_member_0/config \
    -d '{
	"connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
	"tasks.max": "1",
	"topics": "family_health_0.family_health.FAMILY_MEMBER",
    "name": "sink_family_health_clone_family_member_0",
    "delete.enabled": "true",
	"transforms": "route,unwrap,valueKey",
    "transforms.route.type": "org.apache.kafka.connect.transforms.RegexRouter",
    "transforms.route.regex": "([^.]+)\\.([^.]+)\\.([^.]+)",
    "transforms.route.replacement": "$3",
	"transforms.unwrap.drop.tombstones": "false",
	"transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
    "transforms.valueKey.type":"org.apache.kafka.connect.transforms.ValueToKey",
    "transforms.valueKey.fields":"id",        
	"auto.create": "true",
    "key.converter":"io.confluent.connect.avro.AvroConverter",
    "key.converter.schema.registry.url":"http://schema-registry:8081",
	"connection.url": "jdbc:mysql://db:3306/family_health_clone?user=family_health&password=family_health",
	"insert.mode": "upsert",
	"pk.mode": "record_key",
	"pk.fields": "id"
}';
```

# Create a JDBC sink again, this time for FAMILY

This does the same thing as before, except that we're going to pull messages from the FAMILY topic. We'll need this because we have a FK constraint in the "FAMILY_MEMBER" table against the "FAMILY" table, meaning that we can't have records in FAMILY_MEMBER unless there is a FAMILY to link to.

```
curl -i -X PUT -H "Accept:application/json" \
    -H  "Content-Type:application/json" http://localhost:8083/connectors/sink_family_health_family_0/config \
    -d '{
	"connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
	"tasks.max": "1",
	"topics": "family_health_0.family_health.FAMILY",
    "name": "sink_family_health_family_0",
    "delete.enabled": "true",
	"transforms": "route,unwrap",
    "transforms.route.type": "org.apache.kafka.connect.transforms.RegexRouter",
    "transforms.route.regex": "([^.]+)\\.([^.]+)\\.([^.]+)",
    "transforms.route.replacement": "$3",
	"transforms.unwrap.drop.tombstones": "false",
	"transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState", 
    "key.converter":"io.confluent.connect.avro.AvroConverter",
    "key.converter.schema.registry.url":"http://schema-registry:8081",
	"auto.create": "true",
	"connection.url": "jdbc:mysql://db:3306/family_health_clone?user=family_health&password=family_health",
	"insert.mode": "upsert",
	"pk.mode": "record_key",
	"pk.fields": "id"
}';
```

# Do this again for DOCTOR, CLAIM, and PAYMENT:

```
curl -i -X PUT -H "Accept:application/json" \
    -H  "Content-Type:application/json" http://localhost:8083/connectors/sink_family_health_doctor_0/config \
    -d '{
	"connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
	"tasks.max": "1",
	"topics": "family_health_0.family_health.DOCTOR",
    "name": "sink_family_health_doctor_0",
    "delete.enabled": "true",
	"transforms": "route,unwrap,valueKey",
    "transforms.route.type": "org.apache.kafka.connect.transforms.RegexRouter",
    "transforms.route.regex": "([^.]+)\\.([^.]+)\\.([^.]+)",
    "transforms.route.replacement": "$3",
	"transforms.unwrap.drop.tombstones": "false",
	"transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
    "transforms.valueKey.type":"org.apache.kafka.connect.transforms.ValueToKey",
    "transforms.valueKey.fields":"id", 
    "key.converter":"io.confluent.connect.avro.AvroConverter",
    "key.converter.schema.registry.url":"http://schema-registry:8081",       
	"auto.create": "true",
	"connection.url": "jdbc:mysql://db:3306/family_health_clone?user=family_health&password=family_health",
	"insert.mode": "upsert",
	"pk.mode": "record_key",
	"pk.fields": "id"
}';
```

```
curl -i -X PUT -H "Accept:application/json" \
    -H  "Content-Type:application/json" http://localhost:8083/connectors/sink_family_health_claim_0/config \
    -d '{
	"connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
	"tasks.max": "1",
	"topics": "family_health_0.family_health.CLAIM",
    "name": "sink_family_health_claim_0",
    "delete.enabled": "true",
	"transforms": "route,unwrap,valueKey",
    "transforms.route.type": "org.apache.kafka.connect.transforms.RegexRouter",
    "transforms.route.regex": "([^.]+)\\.([^.]+)\\.([^.]+)",
    "transforms.route.replacement": "$3",
	"transforms.unwrap.drop.tombstones": "false",
	"transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
    "transforms.valueKey.type":"org.apache.kafka.connect.transforms.ValueToKey",
    "transforms.valueKey.fields":"id",   
    "auto.create": "true",
    "key.converter":"io.confluent.connect.avro.AvroConverter",
    "key.converter.schema.registry.url":"http://schema-registry:8081",
	"connection.url": "jdbc:mysql://db:3306/family_health_clone?user=family_health&password=family_health",
	"insert.mode": "upsert",
	"pk.mode": "record_key",
	"pk.fields": "id"
}';
```

```
curl -i -X PUT -H "Accept:application/json" \
    -H  "Content-Type:application/json" http://localhost:8083/connectors/sink_family_health_payment_0/config \
    -d '{
	"connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
	"tasks.max": "1",
	"topics": "family_health_0.family_health.PAYMENT",
    "name": "sink_family_health_payment_0",
    "delete.enabled": "true",
	"transforms": "route,unwrap,valueKey",
    "transforms.route.type": "org.apache.kafka.connect.transforms.RegexRouter",
    "transforms.route.regex": "([^.]+)\\.([^.]+)\\.([^.]+)",
    "transforms.route.replacement": "$3",
	"transforms.unwrap.drop.tombstones": "false",
	"transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
    "transforms.valueKey.type":"org.apache.kafka.connect.transforms.ValueToKey",
    "transforms.valueKey.fields":"id",   
    "auto.create": "true",
    "key.converter":"io.confluent.connect.avro.AvroConverter",
    "key.converter.schema.registry.url":"http://schema-registry:8081",
	"connection.url": "jdbc:mysql://db:3306/family_health_clone?user=family_health&password=family_health",
	"insert.mode": "upsert",
	"pk.mode": "record_key",
	"pk.fields": "id"
}';
```

# Create same abstractions in ksql

To login:

```
docker exec -it ksqldb-cli-1 bash
```

```
ksql http://ksqldb-server-1:8088
```

Show topics at the start:

```
SET 'auto.offset.reset' = 'earliest';
```

## Create ksql table abstractions

```
CREATE TABLE T_DOCTOR WITH (kafka_topic='family_health_0.family_health.DOCTOR', value_format='avro', key_format='avro');

CREATE TABLE T_FAMILY WITH (kafka_topic='family_health_0.family_health.FAMILY', value_format='avro', key_format='avro');

CREATE TABLE T_FAMILY_MEMBER WITH (kafka_topic='family_health_0.family_health.FAMILY_MEMBER', value_format='avro', key_format='avro');

CREATE TABLE T_CLAIM WITH (kafka_topic='family_health_0.family_health.CLAIM', value_format='avro', key_format='avro');

CREATE TABLE T_PAYMENT WITH (kafka_topic='family_health_0.family_health.PAYMENT', value_format='avro', key_format='avro');
```

Note that these tables have the ROWKEY with a struct of the ID. This is not desirable. Feel free to drop these objects, as we won't use them.

## Create streams and table to re-key

### Doctor

```
CREATE STREAM S_DOCTOR (ID BIGINT, NAME VARCHAR) WITH (kafka_topic='family_health_0.family_health.DOCTOR', value_format='avro', key_format='avro');

CREATE STREAM SK_DOCTOR AS SELECT ROWKEY->ID ID, NAME FROM S_DOCTOR PARTITION BY ROWKEY->ID;

CREATE TABLE TK_DOCTOR(ID BIGINT PRIMARY KEY, NAME VARCHAR) WITH (KAFKA_TOPIC='SK_DOCTOR', VALUE_FORMAT='AVRO', KEY_FORMAT='AVRO');

```

The rest:

### Family

```
CREATE STREAM S_FAMILY (ID BIGINT, NAME VARCHAR) WITH (kafka_topic='family_health_0.family_health.FAMILY', value_format='avro', key_format='avro');

CREATE STREAM SK_FAMILY AS SELECT ROWKEY->ID ID, NAME FROM S_FAMILY PARTITION BY ROWKEY->ID;

CREATE TABLE TK_FAMILY(ID BIGINT PRIMARY KEY, NAME VARCHAR) WITH (KAFKA_TOPIC='SK_FAMILY', VALUE_FORMAT='AVRO', KEY_FORMAT='AVRO');
```

### Family Member

```
CREATE STREAM S_FAMILY_MEMBER (ID BIGINT, FAMILY_ID BIGINT, NAME VARCHAR) WITH (kafka_topic='family_health_0.family_health.FAMILY_MEMBER', value_format='avro', key_format='avro');

CREATE STREAM SK_FAMILY_MEMBER AS SELECT ROWKEY->ID ID, FAMILY_ID, NAME FROM S_FAMILY_MEMBER PARTITION BY ROWKEY->ID;

CREATE TABLE TK_FAMILY_MEMBER(ID BIGINT PRIMARY KEY, FAMILY_ID BIGINT, NAME VARCHAR) WITH (KAFKA_TOPIC='SK_FAMILY_MEMBER', VALUE_FORMAT='AVRO', KEY_FORMAT='AVRO');
```

### Claim

```
CREATE STREAM S_CLAIM (ID BIGINT, DOCTOR_ID BIGINT, VISIT_DATE VARCHAR, FAMILY_MEMBER_ID BIGINT, AMOUNT BIGINT) WITH (kafka_topic='family_health_0.family_health.CLAIM', value_format='avro', key_format='avro');

CREATE STREAM SK_CLAIM AS SELECT ROWKEY->ID ID, DOCTOR_ID, VISIT_DATE, FAMILY_MEMBER_ID, AMOUNT FROM S_CLAIM PARTITION BY ROWKEY->ID;

CREATE TABLE TK_CLAIM(ID BIGINT PRIMARY KEY, DOCTOR_ID BIGINT, VISIT_DATE VARCHAR, FAMILY_MEMBER_ID BIGINT, AMOUNT BIGINT) WITH (KAFKA_TOPIC='SK_CLAIM', VALUE_FORMAT='AVRO', KEY_FORMAT='AVRO');
```

### Payment

```
CREATE STREAM S_PAYMENT (ID BIGINT, FAMILY_MEMBER_ID BIGINT, CLAIM_ID BIGINT, AMOUNT BIGINT, PAYMENT_DATE VARCHAR) WITH (kafka_topic='family_health_0.family_health.PAYMENT', value_format='avro', key_format='avro');

CREATE STREAM SK_PAYMENT AS SELECT ROWKEY->ID ID, FAMILY_MEMBER_ID, CLAIM_ID, AMOUNT, PAYMENT_DATE FROM S_PAYMENT PARTITION BY ROWKEY->ID;

CREATE TABLE TK_PAYMENT(ID BIGINT PRIMARY KEY, FAMILY_MEMBER_ID BIGINT, CLAIM_ID BIGINT, AMOUNT BIGINT, PAYMENT_DATE VARCHAR) WITH (KAFKA_TOPIC='SK_PAYMENT', VALUE_FORMAT='AVRO', KEY_FORMAT='AVRO');
```

### Create intermediate table to bring names into CLAIMs

Foreign key JOIN are not part of multiple table joins. If we try:

```
ksql> SELECT C.VISIT_DATE, D.NAME, FM.NAME FROM TK_CLAIM C INNER JOIN TK_DOCTOR D ON C.DOCTOR_ID = D.ID INNER JOIN TK_FAMILY_MEMBER FM ON C.FAMILY_MEMBER_ID = FM.ID EMIT CHANGES;

Invalid join condition: foreign-key table-table joins are not supported as part of n-way joins. Got C.FAMILY_MEMBER_ID = FM.ID.
Statement: SELECT C.VISIT_DATE, D.NAME, FM.NAME FROM TK_CLAIM C INNER JOIN TK_DOCTOR D ON C.DOCTOR_ID = D.ID INNER JOIN TK_FAMILY_MEMBER FM ON C.FAMILY_MEMBER_ID = FM.ID EMIT CHANGES;: SELECT C.VISIT_DATE, D.NAME, FM.NAME FROM TK_CLAIM C INNER JOIN TK_DOCTOR D ON C.DOCTOR_ID = D.ID INNER JOIN TK_FAMILY_MEMBER FM ON C.FAMILY_MEMBER_ID = FM.ID EMIT CHANG
ES;
```

The only way I've found around this is to produce intermediate objects, building up to the final desired JOIN. In other words, we'll first create an intermediate table to get the doctor's name:

```
 CREATE TABLE TI_CLAIM AS SELECT C.ID, C.VISIT_DATE, D.NAME, C.FAMILY_MEMBER_ID FROM TK_CLAIM C INNER JOIN TK_DOCTOR D ON C.DOCTOR_ID = D.ID;
```

Then we'll get the family member name, JOINing on this table:

```
ksql> SELECT C.VISIT_DATE, C.NAME DOCTOR_NAME, FM.NAME FAMILY_MEMBER_NAME FROM TI_CLAIM C INNER JOIN TK_FAMILY_MEMBER FM ON C.FAMILY_MEMBER_ID = FM.ID EMIT CHANGES;
+--------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------+
|VISIT_DATE                                                                                                          |DOCTOR_NAME                                                                                                         |FAMILY_MEMBER_NAME                                                                                                  |
+--------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------+
|2023-01-01                                                                                                          |Pamela Pence                                                                                                        |Thomas                                                                                                              |
|2023-01-02                                                                                                          |Pamela Pence                                                                                                        |Sandra                                                                                                              |

```

Again, this sucks if we want to try and get the family member's last name:

```
ksql> SELECT C.VISIT_DATE, C.NAME DOCTOR_NAME, FM.NAME FAMILY_MEMBER_FIRST_NAME, F.NAME FAMILY_MEMBER_LAST_NAME FROM TI_CLAIM C INNER JOIN TK_FAMILY_MEMBER FM ON C.FAMILY_MEMBER_ID = FM.ID INNER JOIN TK_FAMILY F ON FM.FAMILY_ID = F.ID EMIT CHANGES;

Invalid join condition: foreign-key table-table joins are not supported as part of n-way joins. Got FM.FAMILY_ID = F.ID.
Statement: SELECT C.VISIT_DATE, C.NAME DOCTOR_NAME, FM.NAME FAMILY_MEMBER_FIRST_NAME, F.NAME FAMILY_MEMBER_LAST_NAME FROM TI_CLAIM C INNER JOIN TK_FAMILY_MEMBER FM ON C.FAMILY_MEMBER_ID = FM.ID INNER JOIN TK_FAMILY F ON FM.FAMILY_ID = F.ID EMIT CHANGES;: SELECT C.VISIT_DATE, C.NAME DOCTOR_NAME, FM.NAME FAMILY_MEMBER_FIRST_NAME, F.NAME FAMILY_MEMBER_LAS
T_NAME FROM TI_CLAIM C INNER JOIN TK_FAMILY_MEMBER FM ON C.FAMILY_MEMBER_ID = FM.ID INNER JOIN TK_FAMILY F ON FM.FAMILY_ID = F.ID EMIT CHANGES;
ksql> 
```