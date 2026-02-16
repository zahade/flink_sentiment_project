from kafka import KafkaConsumer
from clickhouse_driver import Client
import json

print("=" * 80)
print("🚀 REAL-TIME TWEET PROCESSOR STARTED")
print("=" * 80)

# ClickHouse setup
clickhouse = Client(host='localhost', port=9000, database='default')

clickhouse.execute('''
    CREATE TABLE IF NOT EXISTS tweet_sentiment (
        tweet String,
        sentiment String,
        ts DateTime DEFAULT now(),
        timestamp UInt32
    ) ENGINE = MergeTree()
    ORDER BY (timestamp, ts)
''')
print("✅ ClickHouse table ready")

# Kafka consumer
consumer = KafkaConsumer(
    'tweets',
    bootstrap_servers='localhost:9092',
    group_id='flink-sentiment-group',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='latest'
)

print("✅ Kafka consumer ready")
print("🎯 Processing tweets in real-time...")
print("=" * 80)

count = 0
try:
    for message in consumer:
        data = message.value
        
        # Insert into ClickHouse
        clickhouse.execute(
            "INSERT INTO tweet_sentiment (tweet, sentiment, timestamp) VALUES",
            [(data['tweet'], data['sentiment'], data['timestamp'])]
        )
        
        count += 1
        sentiment_emoji = {'positive': '😊', 'neutral': '😐', 'negative': '😟'}
        emoji = sentiment_emoji.get(data['sentiment'], '❓')
        
        print(f"✅ #{count:04d} {emoji} {data['sentiment'].upper():8s} | {data['tweet'][:60]}")
        
except KeyboardInterrupt:
    print(f"\n{'=' * 80}")
    print(f"✅ Processor stopped. Total tweets processed: {count}")
    print("=" * 80)
finally:
    consumer.close()
    clickhouse.disconnect()