import numpy as np 
import pandas as pd
import psycopg2
from ast import literal_eval
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
import matplotlib
matplotlib.use('TkAgg') 
import matplotlib.pyplot as plt

n = 100

conn = psycopg2.connect(
    port = 5432, 
    dbname="rightmove_new",
    user="samyytids",
    password="Pokemon11",
    host="localhost"
)

with conn:
    with conn.cursor() as cur:
        cur.execute("SELECT embedding FROM key_feature WHERE embedding IS NOT NULL LIMIT 10000")
        key_features = cur.fetchall()
    
embeddings = np.vstack([np.array(literal_eval(kf[0])) for kf in key_features])

kmeans = KMeans(n_clusters=n, init="k-means++", random_state=42)
kmeans.fit(embeddings)
labels = kmeans.labels_
df = pd.DataFrame(embeddings, columns=[f'feature_{i}' for i in range(embeddings.shape[1])])  # <---
df['Cluster'] = labels  # <---

tsne = TSNE(n_components=2, perplexity=15, random_state=42, init="random", learning_rate=200)
points = tsne.fit_transform(embeddings)
x = [x for x, _ in points]
y = [y for _, y in points]

colors = plt.cm.get_cmap('tab10', n)

for category in range(n):
    color = colors(category)
    xs = np.array(x)[df.Cluster == category]
    ys = np.array(y)[df.Cluster == category]
    plt.scatter(xs, ys, color=color, alpha=0.3)

    avg_x = xs.mean()
    avg_y = ys.mean()

    plt.scatter(avg_x, avg_y, marker="x", color=color, s=100)
plt.title("Clusters identified visualized in language 2d using t-SNE")
plt.show()
