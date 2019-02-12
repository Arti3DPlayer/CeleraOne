import json
import urllib
from datetime import datetime
from flask import Flask, redirect, request, render_template

app = Flask(__name__)

app.config.from_mapping(
    GITHUB_API_URL='https://api.github.com/',
)

@app.route('/navigator')
def navigator():
    
    search_term = request.args.get('search_term')
    if not search_term:
        return '{search_term} parametr is required'

    
    api_params = urllib.parse.urlencode({
        'per_page': '5',
        'q': search_term
    })
    api_url = f"{app.config['GITHUB_API_URL']}search/repositories?{api_params}"
    try:
        data = urllib.request.urlopen(api_url).read()
        data = json.loads(data.decode('utf-8'))
    except (urllib.error.URLError, ValueError) as e:
        return f'Github error. Reason: {e.reason}'
    
    items = data.get('items', [])
    items.sort(key=lambda x: x['created_at'], reverse=True)

    for item in items:
        item['created_at'] = datetime.strptime(item['created_at'], '%Y-%m-%dT%H:%M:%SZ')

        api_params = urllib.parse.urlencode({
            'per_page': '1'
        })
        api_url = f"{app.config['GITHUB_API_URL']}repos/{item['owner']['login']}/{item['name']}/commits?{api_params}"
        
        try:
            commit_data = urllib.request.urlopen(api_url).read()
            commit_data = json.loads(commit_data.decode('utf-8'))
            item['commit_data'] = commit_data
        except (urllib.error.URLError, ValueError) as e:
            item['commit_data'] = []

    return render_template('template.html', items=items, search_term=search_term)


if __name__=='__main__':
    app.run(port=9876)