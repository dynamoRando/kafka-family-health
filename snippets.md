# Grant perms to user

```
GRANT ALL PRIVILEGES ON *.* TO 'family_health'@'%';
FLUSH PRIVILEGES;
```

# Validate the Debezium connector

Instructs Debezium to connect to our database and to follow the specified tables. We also will attempt to flatten out records from Debezium's normal BEFORE/AFTER fields into something simpler using the the `ExtractNewRecordState` SMT (Single Messsage Transform).

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
```
curl -i -X PUT -H "Accept:application/json" \
    -H  "Content-Type:application/json" http://localhost:8083/connectors/source_family_health_00/config \
    -d '{ 
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
    "database.server.name" : "family_health_00",
    "database.include.list": "family_health",
    "transforms":"unwrap",
    "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
    "transforms.unwrap.drop.tombstones" : "true",
    "transforms.unwrap.delete.handling.mode":"drop",
    "table_include_list":"DOCTOR,CLAIM,FAMILY,FAMILY_MEMBER"
 }';
```

# Create plain Debezium connect with an SMT to move values that will interfere with sinking

```
curl -i -X PUT -H "Accept:application/json" \
    -H  "Content-Type:application/json" http://localhost:8083/connectors/source_family_health_02/config \
    -d '{ 
    "connector.class": "io.debezium.connector.mysql.MySqlConnector",
    "database.user": "family_health",
    "database.server.id": "3",
    "tasks.max": "1",
    "schema.history.internal.kafka.bootstrap.servers": "kafka-1:9092",
    "database.port": "3306",
    "topic.prefix": "dbz",
    "schema.history.internal.kafka.topic": "schema-changes.health_02",
    "database.hostname": "db",
    "database.password": "family_health",
    "name": "source_family_health_02",
    "database.allowPublicKeyRetrieval":"true",
    "database.history.kafka.bootstrap.servers": "kafka-1:9092",
    "database.history.kafka.topic": "family_health-history-02",
    "database.server.name" : "family_health_02",
    "database.include.list": "family_health",
    "table_include_list":"DOCTOR,CLAIM,FAMILY,FAMILY_MEMBER",
    "transforms": "route",
    "transforms.route.type": "org.apache.kafka.connect.transforms.RegexRouter",
    "transforms.route.regex": "([^.]+)\\.([^.]+)\\.([^.]+)",
    "transforms.route.replacement": "$3"
 }';
```

# Create clone database to sink data into

```sql
CREATE DATABASE family_health_clone;
```

# Create a JDBC sink to mirror data from the FAMILY_MEMBER topic (the one where we pulled out values that would interfer with sinking)

```
curl -i -X PUT -H "Accept:application/json" \
    -H  "Content-Type:application/json" http://localhost:8083/connectors/sink_family_health_clone_04/config \
    -d '{
	"connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
	"tasks.max": "1",
	"topics": "family_health_00.family_health.FAMILY_MEMBER",
    "name": "sink_family_health_clone_04",
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