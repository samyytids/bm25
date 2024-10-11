from openai import OpenAI
import json 
import psycopg2
from psycopg2.extras import execute_values
import os

def create_new_category(category_of_interest, cur):
    print("Requesting embedding from API")
    embedding = client.embeddings.create(input = [category_of_interest], model="text-embedding-3-large").data[0].embedding
    print("Storing embedding in db")
    cur.execute("INSERT INTO category (category_label, embedding) VALUES (%s, %s)", (category_of_interest, embedding))
    cur.execute("SELECT * FROM category WHERE category_label = %s", (category_of_interest,))
    category_id, category_of_interest, embedding = cur.fetchone()
    return category_id, category_of_interest, embedding

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

with conn:
    with conn.cursor() as cur:
        category_of_interest = input("What category are you checking?").lower()
        cur.execute("SELECT * FROM category WHERE levenshtein(category_label, %s) < 3", (category_of_interest,))
        existing_category = cur.fetchone()
        if existing_category is not None:
            good_category = input(f"Existing category found (y/n): {existing_category[1]}")
            if good_category == "n":
                category_id, category_of_interest, embedding = create_new_category(category_of_interest, cur)
            else:
                category_id, category_of_interest, embedding = existing_category
        else:
            category_id, category_of_interest, embedding = create_new_category(category_of_interest, cur)
        
        print("Making distance query on local db")
        ewbedding = str(embedding)
        cur.execute("SELECT id, feature, 1.0 - (embedding <=> %s) AS similarity FROM key_feature WHERE embedding IS NOT NULL ORDER BY 1.0 - (embedding <=> %s) DESC", (embedding,embedding))
        features = cur.fetchall()
        finished = False
        index = 0
        while not finished:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"{category_of_interest}: {index}")
            print("")
            for feature in features[index:index+10]:
                print(feature)
            print("")
            try:
                jump = input("How far do you want to jump?")
                if "." in jump:
                    jump = float(jump)
                    for idx, f in enumerate(features):
                        if f[-1] <= jump:
                            break
                    jump = idx - index
                else:
                    jump = int(jump)

            except KeyboardInterrupt:
                finished = False
                break
            except:
                jump = 1
            
            index = index + jump
            if index < 0:
                index = 0

            if jump == 0:
                finished = True
        
        if finished:
            valid_features = features[0:index]
            inserts = [(f[0], category_id) for f in valid_features]
            execute_values(cur, "INSERT INTO key_feature_categories (key_feature_id, category_id) VALUES %s ON CONFLICT (key_feature_id, category_id) DO NOTHING", inserts)
        


        
            

