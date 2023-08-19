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
    "topic.prefix": "dbz",
    "schema.history.internal.kafka.topic": "schema-changes.health",
    "database.hostname": "db",
    "database.password": "family_health",
    "name": "source_family_health_00",
    "database.allowPublicKeyRetrieval":"true",
    "database.history.kafka.bootstrap.servers": "kafka-1:9092",
    "database.history.kafka.topic": "family_health-history",
    "database.server.name" : "family_health",
    "database.include.list": "family_health",
    "transforms":"unwrap",
    "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
    "transforms.unwrap.drop.tombstones" : "true",
    "transforms.unwrap.delete.handling.mode":"drop",
    "table_include_list":"DOCTOR,CLAIM,FAMILY,FAMILY_MEMBER"
 }';
```

# Create the Debezium connector

Now, do it for real:

```
curl -i -X PUT -H "Accept:application/json" \
    -H  "Content-Type:application/json" http://localhost:8083/connectors/source_family_health_11/config \
    -d '{ 
    "connector.class": "io.debezium.connector.mysql.MySqlConnector",
    "database.user": "family_health",
    "database.server.id": "11",
    "tasks.max": "1",
    "schema.history.internal.kafka.bootstrap.servers": "kafka-1:9092",
    "database.port": "3306",
    "topic.prefix": "family_health_11",
    "schema.history.internal.kafka.topic": "schema-changes.health",
    "database.hostname": "db",
    "database.password": "family_health",
    "name": "source_family_health_11",
    "database.allowPublicKeyRetrieval":"true",
    "database.history.kafka.bootstrap.servers": "kafka-1:9092",
    "database.history.kafka.topic": "family_health-history",
    "database.server.name" : "family_health_11",
    "database.include.list": "family_health",
    "transforms":"unwrap, ts",
    "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
    "transforms.unwrap.drop.tombstones" : "true",
    "transforms.unwrap.delete.handling.mode":"drop",
    "transforms.ts.type":"org.apache.kafka.connect.transforms.TimestampConverter$Value",
    "transforms.ts.format": "yyyy-MM-dd",
    "transforms.ts.target.type": "string", 
    "transforms.ts.field":"visit_date",
    "time.precision.mode":"connect",
    "table_include_list":"DOCTOR,CLAIM,FAMILY,FAMILY_MEMBER"
 }';
```

# Create a "plain" Debezium connector.

This is an alternative example of creating a Debezium connector for the same data. It leaves the BEFORE/AFTER format for rows in the Kafka topic's records. Note that we won't use these topics that are created as part of any sinks. They're just here to show what happens from Debezium with the BEFORE/AFTER state.

```
curl -i -X PUT -H "Accept:application/json" \
    -H  "Content-Type:application/json" http://localhost:8083/connectors/source_family_health_01/config \
    -d '{ 
    "connector.class": "io.debezium.connector.mysql.MySqlConnector",
    "database.user": "family_health",
    "database.server.id": "2",
    "tasks.max": "1",
    "schema.history.internal.kafka.bootstrap.servers": "kafka-1:9092",
    "database.port": "3306",
    "topic.prefix": "dbz",
    "schema.history.internal.kafka.topic": "schema-changes.health_01",
    "database.hostname": "db",
    "database.password": "family_health",
    "name": "source_family_health_01",
    "database.allowPublicKeyRetrieval":"true",
    "database.history.kafka.bootstrap.servers": "kafka-1:9092",
    "database.history.kafka.topic": "family_health-history-01",
    "database.server.name" : "family_health_01",
    "database.include.list": "family_health",
    "table_include_list":"DOCTOR,CLAIM,FAMILY,FAMILY_MEMBER"
 }';
```

# Create clone database to sink data into

```sql
CREATE DATABASE family_health_clone;
```

# Create a JDBC sink to mirror data from the FAMILY_MEMBER topic 

This creates a sink against the "family_health_clone" database and pulls messages from the `family_health_00.family_health.FAMILY_MEMBER` topic to sink into the corresponding same named table. We apply a few transforms: one to route message thru a REGEX to remove any components in the record in the topic to replace anything that won't work with SQL. We also apply an unwrap to that, and finally we pull out the key for the record out of the value of the record, using the "id" field. This is so that when we sink the record into our "clone" database, instead of using the key value in the record of the topic (which looks like `Struct{id=1}`), we'll instead extract it from the value of the record in the topic.

```
curl -i -X PUT -H "Accept:application/json" \
    -H  "Content-Type:application/json" http://localhost:8083/connectors/sink_family_health_clone_family_member_00/config \
    -d '{
	"connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
	"tasks.max": "1",
	"topics": "family_health_00.family_health.FAMILY_MEMBER",
    "name": "sink_family_health_clone_family_member_00",
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
    -H  "Content-Type:application/json" http://localhost:8083/connectors/sink_family_health_family_00/config \
    -d '{
	"connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
	"tasks.max": "1",
	"topics": "family_health_00.family_health.FAMILY",
    "name": "sink_family_health_family_00",
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
	"connection.url": "jdbc:mysql://db:3306/family_health_clone?user=family_health&password=family_health",
	"insert.mode": "upsert",
	"pk.mode": "record_key",
	"pk.fields": "id"
}';
```

Do this again for DOCTOR and for CLAIM:

```
curl -i -X PUT -H "Accept:application/json" \
    -H  "Content-Type:application/json" http://localhost:8083/connectors/sink_family_health_doctor_00/config \
    -d '{
	"connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
	"tasks.max": "1",
	"topics": "family_health_00.family_health.DOCTOR",
    "name": "sink_family_health_doctor_00",
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
	"connection.url": "jdbc:mysql://db:3306/family_health_clone?user=family_health&password=family_health",
	"insert.mode": "upsert",
	"pk.mode": "record_key",
	"pk.fields": "id"
}';
```

For the CLAIM table, we need to add an SMT to handle the date field converting from Unix epoch:

```
curl -i -X PUT -H "Accept:application/json" \
    -H  "Content-Type:application/json" http://localhost:8083/connectors/sink_family_health_claim_06/config \
    -d '{
	"connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
	"tasks.max": "1",
	"topics": "family_health_11.family_health.CLAIM",
    "name": "sink_family_health_claim_06",
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
	"connection.url": "jdbc:mysql://db:3306/family_health_clone?user=family_health&password=family_health",
	"insert.mode": "upsert",
	"pk.mode": "record_key",
	"pk.fields": "id"
}';
```