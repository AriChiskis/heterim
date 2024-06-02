
import openai
import faiss
import numpy as np
import psycopg2
import numpy as np
import os

#HOW I CREATED MY DATABASE IN PSQL
"""
    HOW I CREATED MY DATABASE:

    arielchiskis@ARIELs-MacBook-Pro ~ % psql -U arielchiskis -d postgres

    psql (14.12 (Homebrew))
    Type "help" for help.

    postgres=# CREATE DATABASE first_database
    postgres-# \c first_database
    connection to server on socket "/tmp/.s.PGSQL.5432" failed: FATAL:  database "first_database" does not exist
    Previous connection kept
    postgres-# CREATE DATABASE first_database;
    ERROR:  syntax error at or near "CREATE"
    LINE 2: CREATE DATABASE first_database;
            ^
    postgres=# CREATE DATABASE first_database;
    CREATE DATABASE
    postgres=# \c first_database
    You are now connected to database "first_database" as user "arielchiskis".
    first_database=# CREATE TABLE embeddings (
        word VARCHAR(255) PRIMARY KEY,
        embedding FLOAT8[]
    );
    CREATE TABLE
    first_database=# 

"""

# Example usage
words = ['apple', 'banana', 'cherry', 'date', 'elderberry']
animals  = ['cat','dog','lion','bear','mouse']

# Set your API key here
openai.api_key = 'sk-proj-cI8ubN4KyDSZxD99a9WxT3BlbkFJ1ANiwMwzilpkVzJ0Ce5f'

def get_embedding_text(text):
    response = openai.Embedding.create(
        input=[text],
        model="text-embedding-ada-002"  # You can choose a different model based on your needs
    )
    return response['data'][0]['embedding']  # This extracts the embedding from the response

        # # Example usage
        # sentence = "i am a cat"
        # embedding = get_embeddings(sentence)
        # # print("Embedding:", embedding)

def get_embeddings(words):
    # Your existing function that fetches embeddings
    return openai.Embedding.create(
        input=words,
        model="text-embedding-ada-002"
    )

def insert_embeddings(words, embeddings):
    conn = None
    try:
        # Connect to your PostgreSQL database
        conn = psycopg2.connect("dbname=first_database user=arielchiskis")
        cur = conn.cursor()

        # Insert each word and its corresponding embedding
        for word, embedding in zip(words, embeddings):
            # Ensure embedding is a list of floats (if it's not already)
            embedding_list = embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
            cur.execute(
                "INSERT INTO embeddings (word, embedding) VALUES (%s, %s) ON CONFLICT (word) DO UPDATE SET embedding = EXCLUDED.embedding;",
                (word, embedding_list)
            )

        # Commit the changes to the database
        conn.commit()
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
    finally:
        if conn is not None:
            conn.close()

def print_embeddings():
    conn = psycopg2.connect("dbname=first_database user=arielchiskis")
    cur = conn.cursor()
    cur.execute("SELECT word, embedding FROM embeddings;")
    rows = cur.fetchall()
    for row in rows:
        print("Word:", row[0], "Embedding:", row[1])
    cur.close()
    conn.close()

def find_closest_word(query_embedding, embeddings, words):
    d = embeddings.shape[1]  # Dimensionality of the embeddings
    index = faiss.IndexFlatL2(d)  # Create a FAISS index
    index.add(embeddings)  # Add embeddings to the index

    # Query the index
    distances, indices = index.search(np.array([query_embedding]), 1)  # Find the closest embedding

    # Return the closest word and its distance
    return words[indices[0][0]], distances[0][0]

def fetch_embeddings():
    conn = psycopg2.connect("dbname=first_database user=arielchiskis")
    cur = conn.cursor()
    cur.execute("SELECT word, embedding FROM embeddings;")
    data = cur.fetchall()
    cur.close()
    conn.close()
    words, embeddings = zip(*data)
    embeddings = np.array([np.array(embed, dtype=float) for embed in embeddings])
    return words, embeddings



if __name__ == "__main__":

    query_word = 'king'
    # Get the embedding of the query word
    query_embedding = get_embedding_text(query_word)

    # Fetch embeddings from the database
    words, embeddings = fetch_embeddings()

    # Find the closest word in the dataset
    closest_word, distance = find_closest_word(np.array(query_embedding, dtype=float), embeddings, words)
    print(f"The closest word to '{query_word}' is '{closest_word}' with a distance of {distance:.2f}")




