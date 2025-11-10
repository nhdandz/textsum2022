from kafka import KafkaAdminClient
import init

AdminClient = KafkaAdminClient(bootstrap_servers=init.bootstrap_servers)



lag = AdminClient.listConsumerGroupOffsets("18_multi_hertersum").partitionsToOffsetAndMetadata()
print(lag)
