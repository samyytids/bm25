import tiktoken
import psycopg2

conn = psycopg2.connect(
    host="localhost", port=5432, user="samyytids", password="Pokemon11", dbname="rightmove_new"
)
length = 0
max_length = 0
large_encoding = tiktoken.encoding_for_model("text-embedding-3-large")

with conn:
    with conn.cursor() as cur:
        page = 0
        LIMIT = 10_000
        while True:
            OFFSET = LIMIT * page

            cur.execute("SELECT feature FROM key_feature LIMIT %s OFFSET %s", (LIMIT, OFFSET))
            descriptions = cur.fetchall()
            if len(descriptions) == 0:
                break
            descriptions = [d[0] for d in descriptions]

            large_tokens = []
            for description in descriptions:
                large_tokens.append(large_encoding.encode(description))

            large_lengths = [len(ld) for ld in large_tokens]
            length += sum(large_lengths)
            if max(large_lengths) > max_length:
                max_length = max(large_lengths)
            print("page number: ", page)
            print("current max: ", max_length)
            print("descriptions checked: ", (page + 1)*LIMIT)
            page += 1