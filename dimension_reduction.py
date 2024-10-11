from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
import json
import numpy as np

with open("/home/samyytids-server/api_key.json", "r") as f:
    api_key = json.load(f)

string = ["I am a test string about oranges, I think oranges are really cool. What about you?", "I am even more test strings", "Wow I m just such a test string"]

client = OpenAI(api_key=api_key["open_ai"])

embedding_full = client.embeddings.create(input=string, model="text-embedding-3-large").data
embedding_small = client.embeddings.create(input=string, dimensions=3, model="text-embedding-3-large").data

embedding_full = np.array([np.array(f.embedding) for f in embedding_full])
embedding_small = np.array([np.array(f.embedding) for f in embedding_small])

pca = PCA(n_components=3)
reduced_full = pca.fit_transform(embedding_full)

print(cosine_similarity(embedding_small[0].reshape(1, -1), reduced_full[0].reshape(1, -1)))
