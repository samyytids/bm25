import psycopg2
from psycopg2.extras import execute_values
from openai import OpenAI
import json

conn = psycopg2.connect(
    port = 5432, 
    dbname="rightmove_new",
    user="samyytids",
    password="Pokemon11",
    host="localhost"
)

with open("/home/samyytids-server/api_key.json", "r") as f:
    api_key = json.load(f)

client = OpenAI(api_key=api_key["open_ai"])

LIMIT = 2048
OFFSET = 0
page = 0
while True:
    with conn:
        with conn.cursor() as cur:
            OFFSET = LIMIT*page
            print("Selecting: ", page)
            cur.execute("SELECT id, feature FROM key_feature WHERE embedding IS NULL LIMIT %s OFFSET %s", (LIMIT, OFFSET))
            features = cur.fetchall()
            text = [f[1] for f in features]
            print("Getting embeddings: ", page)
            embeddings = client.embeddings.create(input = text, model="text-embedding-3-large").data
            embeddings = [(e.embedding, features[idx][0]) for idx, e in enumerate(embeddings)]
            print("Inserting embeddings: ", page)
            execute_values(
                cur,
                """
                UPDATE key_feature 
                SET embedding = data.embedding
                FROM (VALUES %s) AS data (embedding, id)
                WHERE key_feature.id = data.id
                """,    
                embeddings
            )
            page += 1
            


