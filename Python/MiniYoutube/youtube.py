from googleapiclient.discovery import build

API_KEY = "PASTE_YOUR_API_KEY_HERE"

def search(query: str, max_results: int = 10):
    youtube = build(
        "youtube",
        "v3",
        developerKey=API_KEY,
        cache_discovery=False,
    )

    req = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=max_results,
    )
    res = req.execute()

    results = []
    for item in res.get("items", []):
        results.append({
            "title": item["snippet"]["title"],
            "video_id": item["id"]["videoId"],
        })

    return results
