from textblob import TextBlob

def analyze_sentiments(suggestions):
    """
    Takes a list of tuples (id, roll, suggestion, date)
    and returns categorized sentiments and statistics.
    """
    total = len(suggestions)
    if total == 0:
        return {"positive": 0, "negative": 0, "neutral": 0, "positive_pct": 0, "negative_pct": 0, "neutral_pct": 0, "total": 0, "analyzed_data": []}

    results = []
    pos_count = 0
    neg_count = 0
    neu_count = 0

    for item in suggestions:
        text = item[2]  # The suggestion text is at index 2
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        if polarity > 0.1:
            sentiment = "Positive"
            pos_count += 1
        elif polarity < -0.1:
            sentiment = "Negative"
            neg_count += 1
        else:
            sentiment = "Neutral"
            neu_count += 1
            
        results.append({
            "roll": item[1],
            "text": text,
            "date": item[3],
            "sentiment": sentiment,
            "polarity": round(polarity, 2)
        })

    # Sort results to show most extreme sentiments first (both completely positive or completely negative)
    results = sorted(results, key=lambda x: abs(x["polarity"]), reverse=True)

    stats = {
        "positive_pct": round((pos_count / total) * 100),
        "negative_pct": round((neg_count / total) * 100),
        "neutral_pct": round((neu_count / total) * 100),
        "total": total,
        "analyzed_data": results
    }

    return stats
