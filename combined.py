from bm25 import BM25
import threading
import queue
import psycopg2
import tiktoken
import numpy as np
import json
from time import time
from openai import OpenAI


def rank_embedding(query, api_key, queue):
    client = OpenAI(api_key=api_key["open_ai"])
    conn = psycopg2.connect(
        port = 5432, 
        dbname="rightmove_new",
        user="samyytids",
        password="Pokemon11",
        host="localhost"
    )
    print("Open ai: Fetching embedding")
    embedding = client.embeddings.create(input = [query], model="text-embedding-3-large").data[0].embedding
    embedding = str(embedding)
    with conn:
        with conn.cursor() as cur:
            print("Open ai: Getting rankings")
            cur.execute("SELECT id FROM key_feature WHERE embedding IS NOT NULL ORDER BY 1.0 - (embedding <=> %s) DESC", (embedding,))
            features = cur.fetchall()
    results = [(idx+1, f[0]) for idx, f in enumerate(features)] # place, id
    print("Open ai: Finsihed")
    queue.put(results)

def rank_bm25(data, query, encoding, queue):
    print("BM25: Getting ids")
    ids = np.array([d[0] for d in data])
    features = np.array([encoding.encode(f[1]) for f in data], dtype=object)
    bm25 = BM25(features)
    print("BM25: Getting rankings")
    scores = bm25.get_scores(query)
    print("BM25: Finsihed")
    sorted_indices = np.argsort(scores)[::-1]
    sorted_ids = ids[sorted_indices]
    results = [(idx+1, int(id_)) for idx, id_ in enumerate(sorted_ids)] # place, id
    queue.put(results)


with open("/home/samyytids-server/api_key.json", "r") as f:
    api_key = json.load(f)

encoding = tiktoken.encoding_for_model("text-embedding-3-large")
test_query = encoding.encode("bright airy light natural modern cosy")
conn = psycopg2.connect(
    port = 5432, 
    dbname="rightmove_new",
    user="samyytids",
    password="Pokemon11",
    host="localhost"
)
with conn:
    with conn.cursor() as cur:
        cur.execute("SELECT id, feature FROM key_feature WHERE embedding IS NOT NULL")
        features = cur.fetchall()


s = time()
print("Spawning queue")
# Create queues to hold the results
output_queue1 = queue.Queue()
output_queue2 = queue.Queue()

print("Beginning threading")
# Create threads for both tasks
thread1 = threading.Thread(target=rank_bm25, args=(features, test_query, encoding, output_queue1))
thread2 = threading.Thread(target=rank_embedding, args=(test_query, api_key, output_queue2))

print("Starting")
# Start the threads
thread1.start()
thread2.start()

print("Joining")
# Wait for both threads to complete
thread1.join()
thread2.join()

print("Getting results")
# Retrieve results from the queues
result1 = output_queue1.get() # place, id
result2 = output_queue2.get() # place, id

len1 = len(result1) 
len2 = len(result2)

if len1 < len2:
    result2 = result2[:len1]
elif len2 < len1:
    result1 = result1[:len2]

# why are you nonsense.
places = {}
for idx, (r1_place, r1_id) in enumerate(result1):
    r2_place, r2_id = result2[idx]
    if r1_id not in places:
        places[r1_id] = [r1_place]
    else:
        places[r1_id].append(r1_place)

    if r2_id not in places:
        places[r2_id] = [r2_place]
    else:
        places[r2_id].append(r2_place)

for key, values in places.items():
    new_rank = 0
    for value in values:
        new_rank += 1/(60 + value)
    places[key] = new_rank

places = {k: v for k, v in sorted(places.items(), key=lambda item: item[1], reverse=True)[0:10]}

# print(places)
# print(result1)
# print(result2)

result1 = {r[1]:r[0] for r in result1}
result2 = {r[1]:r[0] for r in result2}

elements = places.keys()
with conn:
    with conn.cursor() as cur:
        cur.execute("SELECT id, feature FROM key_feature WHERE id IN %s AND embedding IS NOT NULL", (tuple(elements),))
        features = cur.fetchall()

result = {"bright airy light natural modern cosy":[]}
for idx, element in enumerate(features):
    bm_25_place = None
    bm_25_place = result1[element[0]]
    embedding_place = result1[element[0]]

    result["bright airy light natural modern cosy"].append(
        {
            "id" : element[0],
            "text" : element[1],
            "place combined" : idx + 1,
            "place BM25" : bm_25_place,
            "place embedding" : embedding_place

        }
    )

with open("test_placement.json", "w") as f:
    json.dump(result, f, indent=2)

e = time()
print(e - s)
