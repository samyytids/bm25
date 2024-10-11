from collections import defaultdict
from openai import OpenAI
import psycopg2
from psycopg2.extras import execute_values
import json 
import os
from tqdm import tqdm
os.system('cls' if os.name == 'nt' else 'clear')

def analyze_features(features):
    results = defaultdict(int)
    for feature in tqdm(features, desc="Feature loop"):
        for i in feature.split(" "):
            results[i] += 1        
    results = dict(results)
    results = dict(sorted(results.items(), key=lambda item: item[1], reverse=True)) 
    with open("test.json", "w") as f:
        json.dump(results, f, indent=4)



def create_categories(cur, features):
    categories = set()
    for feature in features:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(categories)
        print("")
        print(feature)
        done = False
        while not done:
            category = input("add category: ")
            if category == "":
                done = True
            else:
                categories.add(category)
        bored = input("bored yet?")
        if bored == "y":
            break
    
    result = [(id_, category) for id_, category in enumerate(categories)]

    execute_values(cur, "INSERT INTO categories (id, category) VALUES %s", result)

    return result
        
def check_embeddings(cur):
    cur.execute(
    "WITH distance_query AS (SELECT features.id, small_embedding <=> (SELECT small_embedding FROM query WHERE id = %s) AS distance FROM features) SELECT features.id, distance_query.distance FROM features JOIN distance_query ON distance_query.id = features.id WHERE distance <= 0.4 ORDER BY distance",
    ("Modern fitted kitchen",)
    )


    # cur.execute(
    #     "SELECT id, features.large_embedding <=> (SELECT large_embedding FROM query WHERE id = %s LIMIT 1) FROM features ORDER BY large_embedding <=> (SELECT large_embedding FROM query WHERE id = %s LIMIT 1) DESC LIMIT 10",
    #     ("Kitchen", "Kitchen")
    # )
    values = cur.fetchall()
    print(values)


conn_rightmove = psycopg2.connect(
    host = "localhost",
    dbname = "rightmove_new",
    port = 5432, 
    user = "samyytids",
    password = "Pokemon11"
)

conn_embedding = psycopg2.connect(
    host = "localhost",
    dbname = "embedding_test",
    port = 5432,
    user = "samyytids",
    password = "Pokemon11"
)

# with conn_embedding:
#     with conn_embedding.cursor() as cur:
#         cur.execute("SELECT id FROM features")
#         features = cur.fetchall()
#         features = [f[0] for f in features]
#         create_categories(cur, features)

with conn_rightmove:
    with conn_rightmove.cursor() as cur:
        cur.execute("SELECT feature FROM key_feature ORDER BY RANDOM() LIMIT 1000")
        features = cur.fetchall()
        features = [(f[0],) for f in features]


with open("/home/samyytids-server/api_key.json", "r") as f:
    api_key = json.load(f)

client = OpenAI(api_key=api_key["open_ai"])

with conn_embedding:
    with conn_embedding.cursor() as cur:
        check_embeddings(cur)
        # cur.execute("SELECT feature FROM key_feature")
        # features = cur.fetchall()
        # features = [f[0] for f in features]
        # analyze_features(features)
        # features = ["Hot tub", "Patio", "Modern fitted kitchen", "Traditional kitchen", "Open plan kitchen"]
        # embeddings = client.embeddings.create(input = features, model="text-embedding-3-large").data
        # embeddings = [(e.embedding, features[idx]) for idx, e in enumerate(embeddings)]
        # execute_values(
        #     cur,
        #     """
        #     UPDATE features 
        #     SET small_embedding = data.embedding
        #     FROM (VALUES %s) AS data (embedding, id)
        #     WHERE features.id = data.id
        #     """,    
        #     embeddings
        # )
        # execute_values(
        #     cur,
        #     """
        #     INSERT INTO query (large_embedding, id) VALUES %s
        #     """,
        #     embeddings
        # )
        

# with open("/home/samyytids-server/api_key.json", "r") as f:
#     api_key = json.load(f)




# client = OpenAI(api_key=api_key["open_ai"])