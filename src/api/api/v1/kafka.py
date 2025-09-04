from flask import Flask, request, jsonify
from kafka.admin import KafkaAdminClient, NewTopic

app = Flask(__name__)

# Adresse publique de Kafka
KAFKA_BOOTSTRAP_SERVERS = '20-199-76-32.nip.io:9092'

# Création du client admin Kafka
admin_client = KafkaAdminClient(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    client_id='api-location-service'
)


@app.route('/create-topic/<user_id>', methods=['POST'])
def create_location_topic(user_id):
    topic_name = f'location-{user_id}'

    topic = NewTopic(
        name=topic_name,
        num_partitions=1,
        replication_factor=1
    )

    try:
        admin_client.create_topics([topic])
        return jsonify({'status': 'success', 'topic': topic_name}), 201
    except Exception as e:
        if 'TopicExistsError' in str(e):
            return jsonify({'status': 'exists', 'topic': topic_name}), 200
        return jsonify({'status': 'error', 'error': str(e)}), 500


