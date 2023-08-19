


```
curl -i -X PUT -H "Accept:application/json" \
    -H  "Content-Type:application/json" http://localhost:8083/connectors/source_family_health_5/config \
    -d '{ 
    "connector.class": "io.debezium.connector.mysql.MySqlConnector",
    "database.user": "family_health",
    "database.server.id": "5",
    "tasks.max": "1",
    "schema.history.internal.kafka.bootstrap.servers": "kafka-1:9092",
    "database.port": "3306",
    "topic.prefix": "family_health_5",
    "schema.history.internal.kafka.topic": "schema-changes.health.5",
    "database.hostname": "db",
    "database.password": "family_health",
    "name": "source_family_health_5",
    "errors.tolerance":"all",
    "database.allowPublicKeyRetrieval":"true",
    "database.history.kafka.bootstrap.servers": "kafka-1:9092",
    "database.history.kafka.topic": "family_health-history-5",
    "database.server.name" : "family_health_5",
    "database.include.list": "family_health",
    "transforms":"unwrap, ts, ts2, k",
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
    "transforms.k.type": "org.apache.kafka.connect.transforms.ExtractField$Key",
    "transforms.k.field":"id",
    "time.precision.mode":"connect",
    "key.converter.schemas.enable":"true",
    "value.converter.schemas.enable":"true",
    "key.converter": "io.confluent.connect.avro.AvroConverter",
    "key.converter.schema.registry.url": "http://schema-registry:8081",
    "table_include_list":"DOCTOR,CLAIM,FAMILY,FAMILY_MEMBER,PAYMENT"
 }';
```