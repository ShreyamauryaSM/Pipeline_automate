from flask import Flask, render_template, request
import requests
import yaml
import os
import base64
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

REPO_OWNER = os.getenv("REPO_OWNER")
REPO_NAME = os.getenv("REPO_NAME")


@app.route('/add',methods=['GET','POST'])
def add_form():
    if request.method=='POST':
        data={
            'username':request.form['username'],
            'companyname':request.form['companyname'],
            'repourl': request.form['repourl']
        }  

        file_content = yaml.dump(data, default_flow_style=False)

        file_content_base64 = base64.b64encode(file_content.encode()).decode()

        repo_name = data['repourl'].split('/')[-1]

        file_path = f'Pipeline/SoftwareMathematics/{data["companyname"]}/{repo_name}/{data["username"]}.yaml'

        url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_path}'

        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
        # File already exists, update its content
            existing_file = response.json()
            payload = {
                'message': 'Update file',
                'content': file_content_base64,
                'sha': existing_file['sha']  # SHA of the existing file for update
            }
            response = requests.put(url, headers=headers, json=payload)
        elif response.status_code == 404:
            # File does not exist, create a new file
            payload = {
                'message': 'Create file',
                'content': file_content_base64
            }
            response = requests.put(url, headers=headers, json=payload)
        
        if response.status_code == 201 or response.status_code == 200:
            return 'File saved successfully to GitHub.'
        else:
            return f'Failed to save file to GitHub. Status code: {response.status_code}'

    return "Data saved succesfully!!"

@app.route('/')
def hello_world():
    return render_template("index.html")

if __name__=="__main__":
    app.run(debug=True)