import requests

from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
from openai import OpenAI
client = OpenAI(api_key=api_key)

query = input("Enter your query: ")
url = f"https://hn.algolia.com/api/v1/search?query={query}&tags=story"
info = requests.get(url).json()

for item in info["hits"]:

    title = item["title"]
    id = item["objectID"]

    if title is None:
        title = "No title"

    print("Title: ", title)
    print("ID: ", id)
    print("------")

for story in info["hits"]:
    story_id = story["objectID"]
    story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
    story_data = requests.get(story_url).json()
    print(story_data)

database = []
depth = 0
def get_comment(comment_id, depth):
    comment_url = f"https://hacker-news.firebaseio.com/v0/item/{comment_id}.json"
    comment_data = requests.get(comment_url).json()

    if comment_data is None:
        return
    
    if "text" in comment_data:
        database.append({
            "text": comment_data["text"], 
            "depth": depth}
            )

    if "kids" in comment_data:
        for i in comment_data["kids"]:
            get_comment(i, depth+1)

for comment_id in story_data["kids"]:
    get_comment(comment_id, 0)
print(database[:5])

def chunking(database):
    chunks = []
    current_chunk = ""
    for item in database:
        if item["depth"] == 0:
            if current_chunk != "":
                chunks.append(current_chunk)
            
            current_chunk = ""
            indent = "  " * item["depth"]
            current_chunk += indent + "Main Comment: " + item["text"] + "\n"
        else:
            indent = "  " * item["depth"]
            current_chunk += "Reply" + indent + item["text"] + "\n"

    if current_chunk != "":
        chunks.append(current_chunk)
    return chunks

chunks = chunking(database)[:3]
print(chunks)
print(len(chunks))

def summarize(chunk):       
    try:  
        chunk = chunk[:3000]

        response = client.chat.completions.create(
            model = "gpt-4o-mini",
            messages = [
                {
                    "role" : "system",
                    "content" : "You are an assistant that summarizes discussions like a tech newsletter digest in concise bullet points"
                },

                {
                    "role" : "user",
                    "content" :  f"""
                Summarize the following discussion into:
                    -Main Idea
                    -Key Points (2-3 bullets)
                    -Conclusion

                    Discussion:
                    {chunk}
                    """
                }
            ]
        )   

        return response.choices[0].message.content
     
    except:  
        og_chunk = chunk
        sentences = og_chunk.split(".")
        clean_chunk = og_chunk.lower()

        import re
        chunk = re.sub(r'[^\w\s]', '', clean_chunk)
        genwords = {"the", "is", "and", "a", "to", "of", "in", "that", "it", "for"}
        words = clean_chunk.split()

        filtered_words = []
        for word in words:
            if word not in genwords:
                filtered_words.append(word)

        frequency = {}
        for word in filtered_words:
            if word in frequency:
                frequency[word] += 1
            else:
                frequency[word] = 1

        sentence_score = {}   
        for sentence in sentences: 
            if len(sentence.split()) < 5:
                continue
            score = 0 
            sentence_words = sentence.split()
            for word in sentence_words:
                if word in frequency:
                    score += frequency[word]
            sentence_score[sentence] = score

        sorted_sentences = sorted(sentence_score, key = sentence_score.get, reverse = True)
        top_sentences = sorted_sentences[:3]

        summary = "" 
        for sentence in top_sentences:
            summary += sentence.strip() + "."

        return summary



for i,chunk in enumerate(chunks[:1]):
        print(f"\n --- Summary {i+1} --- \n")
        summary = summarize(chunk)
        print(summary)