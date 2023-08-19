


```
curl -i -X PUT -H "Accept:application/json" \
    -H  "Content-Type:application/json" http://localhost:8083/connectors/source_family_health_3/config \
    -d '{ 
    "connector.class": "io.debezium.connector.mysql.MySqlConnector",
    "database.user": "family_health",
    "database.server.id": "3",
    "tasks.max": "1",
    "schema.history.internal.kafka.bootstrap.servers": "kafka-1:9092",
    "database.port": "3306",
    "topic.prefix": "family_health_3",
    "schema.history.internal.kafka.topic": "schema-changes.health.3",
    "database.hostname": "db",
    "database.password": "family_health",
    "name": "source_family_health_3",
    "database.allowPublicKeyRetrieval":"true",
    "database.history.kafka.bootstrap.servers": "kafka-1:9092",
    "database.history.kafka.topic": "family_health-history",
    "database.server.name" : "family_health_3",
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