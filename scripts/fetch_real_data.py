#!/usr/bin/env python3
"""
Fetch real public data for CDS synthesis.
Uses only unauthenticated public APIs.
"""

import json
import urllib.request
from datetime import datetime, timedelta

def fetch_github_trending():
    """Fetch GitHub trending repos (via their public JSON)"""
    try:
        url = "https://api.github.com/search/repositories?q=stars:>1000+created:>2024-01-01&sort=stars&per_page=10"
        req = urllib.request.Request(url, headers={'User-Agent': 'CDS-Bot'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            repos = []
            for r in data.get('items', [])[:5]:
                repos.append({
                    'id': f"GH_{r['full_name'].replace('/', '_')}",
                    'title': f"GitHub: {r['full_name']}",
                    'category': 'Technology',
                    'subcategory': 'Open Source',
                    'content': f"Repository {r['full_name']} has {r['stargazers_count']} stars, {r['forks_count']} forks. Primary language: {r['language'] or 'N/A'}. Description: {r['description'] or 'No description'}.",
                    'source': 'GitHub Public API',
                    'timestamp': r['created_at'],
                    'tags': ['github', 'trending', 'open-source', (r['language'] or 'unknown').lower()],
                    'metrics': {
                        'stars': r['stargazers_count'],
                        'forks': r['forks_count'],
                        'open_issues': r['open_issues_count']
                    }
                })
            return repos
    except Exception as e:
        return [{'error': str(e), 'source': 'GitHub API'}]

def fetch_reddit_worldnews():
    """Fetch world news headlines from Reddit (public)"""
    try:
        url = "https://www.reddit.com/r/worldnews/hot.json?limit=5"
        req = urllib.request.Request(url, headers={'User-Agent': 'CDS-Bot/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            posts = []
            for child in data.get('data', {}).get('children', [])[:5]:
                post = child.get('data', {})
                posts.append({
                    'id': f"REDDIT_{post['name']}",
                    'title': post.get('title', 'Untitled'),
                    'category': 'Geopolitics',
                    'subcategory': 'World News',
                    'content': f"Reddit worldnews post: {post.get('title', 'N/A')}. Score: {post.get('score', 0)} upvotes, {post.get('num_comments', 0)} comments.",
                    'source': 'Reddit Public API',
                    'timestamp': datetime.now().isoformat(),
                    'tags': ['reddit', 'worldnews', 'geopolitics'],
                    'metrics': {'score': post.get('score', 0), 'comments': post.get('num_comments', 0)}
                })
            return posts
    except Exception as e:
        return [{'error': str(e), 'source': 'Reddit API'}]

def fetch_hackernews():
    """Fetch top stories from Hacker News (public Firebase API)"""
    try:
        top_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        req = urllib.request.Request(top_url, headers={'User-Agent': 'CDS-Bot/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            top_ids = json.loads(resp.read())[:5]
        
        stories = []
        for story_id in top_ids:
            story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            req = urllib.request.Request(story_url, headers={'User-Agent': 'CDS-Bot/1.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                story = json.loads(resp.read())
                if story.get('title'):
                    stories.append({
                        'id': f"HN_{story_id}",
                        'title': f"HN: {story['title'][:60]}...",
                        'category': 'Technology',
                        'subcategory': 'Tech News',
                        'content': f"HackerNews top story: {story.get('title', 'N/A')}. Type: {story.get('type', 'story')}. Score: {story.get('score', 0)}.",
                        'source': 'Hacker News API',
                        'timestamp': datetime.now().isoformat(),
                        'tags': ['hackernews', 'tech', 'startup'],
                        'metrics': {'score': story.get('score', 0), 'descendants': story.get('descendants', 0)}
                    })
        return stories
    except Exception as e:
        return [{'error': str(e), 'source': 'HN API'}]

def main():
    print("=" * 60)
    print("FETCHING REAL PUBLIC DATA FOR CDS")
    print("=" * 60)
    
    all_nodes = []
    
    # Get GitHub trending
    print("\n📦 Fetching GitHub trending...")
    gh_nodes = fetch_github_trending()
    print(f"   Got {len(gh_nodes)} repos")
    all_nodes.extend(gh_nodes[:3])  # Take top 3
    
    # Get Reddit worldnews
    print("\n📦 Fetching Reddit worldnews...")
    reddit_nodes = fetch_reddit_worldnews()
    print(f"   Got {len(reddit_nodes)} posts")
    all_nodes.extend(reddit_nodes[:2])  # Take top 2
    
    # Get Hacker News
    print("\n📦 Fetching Hacker News top stories...")
    hn_nodes = fetch_hackernews()
    print(f"   Got {len(hn_nodes)} stories")
    all_nodes.extend(hn_nodes[:2])  # Take top 2
    
    print(f"\n📊 Total nodes collected: {len(all_nodes)}")
    
    # Save for CDS
    output = {
        'nodes': all_nodes,
        'metadata': {
            'collected_at': datetime.now().isoformat(),
            'sources': ['GitHub Public API', 'Reddit Public API', 'Hacker News Firebase API']
        }
    }
    
    with open('/output/real_cds_input.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("\n✅ Saved to /output/real_cds_input.json")
    
    # Print summary
    print("\n" + "=" * 60)
    print("DATA SUMMARY")
    print("=" * 60)
    for i, node in enumerate(all_nodes, 1):
        print(f"\n{i}. {node.get('id', 'N/A')}")
        print(f"   Category: {node.get('category', 'N/A')} / {node.get('subcategory', 'N/A')}")
        print(f"   Title: {node.get('title', 'N/A')[:70]}")

if __name__ == "__main__":
    main()