#!python3
import os

from algoliasearch.search_client import SearchClient
from dotenv import load_dotenv, find_dotenv
import json
import requests
from flatten_json import flatten

load_dotenv(find_dotenv())

export_path = "export"
export_file = "export-graphql.json"
headers = {"Authorization": f"token {os.getenv('GITHUB_TOKEN')}"}

def main():
    all_records = []
    for user in ['chuckmeyer', 'makvoid', 'clemfromspace']:
        print(f'Gettting repos for {user}')
        result = getIssuesForAllRepos(user)
        print(result)
        records = transform_records(result['data']['user']['repositories']['nodes'])
        all_records.extend(records)
    export_records(all_records)
    update_index(all_records)


def run_query(query, variables): # A simple function to use requests.post to make the API call. Note the json= section.
    request = requests.post('https://api.github.com/graphql', json={'query': query, 'variables': variables}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


def getIssuesForAllRepos(login):
    query = '''
        query ($login: String!, $repositoriesFirst: Int, $issuesFirst: Int) {
          user(login: $login) {
            repositories(first: $repositoriesFirst) {
              totalCount
              nodes {
                issues(first: $issuesFirst) {
                  totalCount
                  nodes {
                    author {
                      login
                    }
                    title
                    createdAt
                    objectID: id
                    repository {
                      name
                    }
                    url
                    state
                    comments {
                      totalCount
                    }
                    closedAt 
                    number
                  }
                }
              }
            }
          }
        }''' 

    variables = {
        "login": login,
       "repositoriesFirst": 100,
       "issuesFirst": 100               
    }

    return run_query(query, variables) #execute query


def transform_records(results):
    records = []
    for row in results:
        if row['issues']['totalCount'] > 0:
            for node in row['issues']['nodes']:
                print(node)
                records.append(flatten(node))
        else:
            print('Skipping repo with no issues')
    return records


def update_index(records):
  # Create the index
  client = SearchClient.create(os.getenv('APP_ID'), os.getenv('API_KEY'))
  index = client.init_index(os.getenv('ALGOLIA_INDEX_NAME'))
  index.clear_objects()
  index.save_objects(records)


def export_records(records):
  # Write the records to a file
  if not os.path.exists(export_path):
    os.makedirs(export_path)
  

  with open(os.path.join(export_path, export_file), 'w') as outfile:
    json.dump(records, outfile)
if __name__ == "__main__":
    main()
