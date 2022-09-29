# Algolia GitHub GraphQL example

Run queries against GitHub's GraphQL API and use the results to populate your Algolia index.

This python code iterates over a list of users and then pulls issue data from all of their repos. The result is a searchable, cross-repository issue index.

Here's the GraphQL query:

```graphql
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
```

You can use `poetry` to install dependencies and execute this code using `poetry run python github_graphql/__init__.py`
