import time
import json
import random
from kafka import KafkaProducer
from datetime import datetime

# Kafka configuration
KAFKA_BROKER = 'localhost:9092'
TOPIC = 'tweets'

# Initialize Kafka producer with retry logic
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    acks='all',  # Wait for all replicas to acknowledge
    retries=3,
    max_in_flight_requests_per_connection=1
)

# Expanded sample tweets with clear sentiment signals
sample_tweets = {
    'positive': [
        "I absolutely love Apache Flink! Best stream processing framework ever! 🚀",
        "Python is amazing for data engineering. So productive!",
        "ClickHouse query performance is mind-blowing! Sub-second aggregations!",
        "Kafka streams make real-time processing so elegant and powerful!",
        "Just deployed my first Flink pipeline - feeling accomplished! 💪",
        "The synergy between Flink + Kafka + ClickHouse is incredible!",
        "Data engineering has never been this exciting! Love working with these tools!",
        "Successfully processed 1M events/sec with Flink! Amazing performance! 🎉"
    ],
    'neutral': [
        "Working on Apache Flink integration today.",
        "Comparing different stream processing frameworks.",
        "ClickHouse has interesting design choices.",
        "Kafka is widely used in enterprise environments.",
        "Setting up the data pipeline infrastructure.",
        "Reading documentation about Flink's watermarks.",
        "The project uses standard data engineering patterns.",
        "Evaluating different database options for analytics."
    ],
    'negative': [
        "Struggling with Flink dependency conflicts again... frustrating!",
        "Why is debugging distributed systems so painful? 😤",
        "Lost hours to a silly Kafka configuration error. Not happy.",
        "ClickHouse documentation could be much better organized.",
        "Another day fighting with serialization issues. Ugh.",
        "This Flink job keeps failing silently. Very annoying!",
        "Kafka offset management is more complex than it should be.",
        "Spent entire day troubleshooting network issues. Terrible productivity."
    ]
}

def generate_tweet():
    """Generate a random tweet with appropriate sentiment"""
    sentiment = random.choices(
        ['positive', 'neutral', 'negative'],
        weights=[0.5, 0.3, 0.2]  # More positive tweets for better demo
    )[0]
    
    tweet = random.choice(sample_tweets[sentiment])
    
    return {
        'tweet': tweet,
        'sentiment': sentiment,
        'timestamp': int(time.time())
    }

def main():
    print("=" * 80)
    print("🚀 TWEET GENERATOR STARTED")
    print("=" * 80)
    print(f"Kafka Broker: {KAFKA_BROKER}")
    print(f"Target Topic: {TOPIC}")
    print(f"Generation Rate: 1 tweet/second")
    print("=" * 80)
    print()
    
    tweet_count = 0
    
    try:
        while True:
            message = generate_tweet()
            
            # Send to Kafka
            future = producer.send(TOPIC, message)
            result = future.get(timeout=10)  # Wait for confirmation
            
            tweet_count += 1
            
            # Format output
            timestamp = datetime.fromtimestamp(message['timestamp']).strftime('%H:%M:%S')
            sentiment_emoji = {
                'positive': '😊',
                'neutral': '😐',
                'negative': '😟'
            }[message['sentiment']]
            
            print(f"[{timestamp}] Tweet #{tweet_count:04d} {sentiment_emoji} {message['sentiment'].upper():8s} | {message['tweet']}")
            
            time.sleep(1)  # 1 tweet per second
            
    except KeyboardInterrupt:
        print("\n" + "=" * 80)
        print(f"✅ Generator stopped. Total tweets sent: {tweet_count}")
        print("=" * 80)
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        producer.flush()
        producer.close()

if __name__ == "__main__":
    main()
