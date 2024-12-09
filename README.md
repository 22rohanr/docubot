# Docubot

Docubot is an automated documentation tool that uses GitHub Actions to generate comprehensive documentation for your code. When changes are pushed to the main branch, GitHub Actions triggers an API endpoint that automatically documents your code. A sandbox repo testing it can be found here: https://github.com/22rohanr/docubotTest

## Features

- **Automated Documentation**: Automatically generates documentation for your code when changes are detected.
- **GitHub Actions Integration**: Uses GitHub Actions to streamline the documentation process.
- **Endpoint Integration**: Hits a specified endpoint to fetch and document code changes.

## Getting Started

### Installation

1. **Set up GitHub Actions**:

   - Ensure you have a GitHub repository set up.
   - Create a `.github/workflows/documentation.yml` file in your repository.

2. **Set up files**:
   - Ensure that you have created a `documentation.md` file in the top level of your repository.

3. **Github Actions Permissions**:
   - Ensure your project gives Github actions the permission to read, write, and push to main.
   
### GitHub Actions Workflow

Here is an example workflow configuration:

```yaml
name: Combined Workflow

on:
  push:
    branches:
      - '**'

  pull_request:
    branches:
      - main

jobs:
  documentation:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      - name: Get Changed Files
        id: get_changed_files
        uses: actions/github-script@v6
        with:
          script: |
            const { owner, repo } = context.repo;
            const commitSha = context.sha;
            const commit = await github.rest.repos.getCommit({
              owner,
              repo,
              ref: commitSha
            });
            const changedFiles = commit.data.files.map(file => file.filename);
            console.log("Changed files: ", changedFiles);  // Print changed files for debugging
            const fs = require('fs');
            fs.writeFileSync('changedFiles.txt', JSON.stringify(changedFiles));
      - name: Read Changed Files
        run: |
          if [ -f changedFiles.txt ]; then
            files_changed=$(cat changedFiles.txt)
          else
            files_changed='[]'
          fi
          echo "Files changed: $files_changed"
      - name: Call the API
        run: |
          if [ -f changedFiles.txt ]; then
            files_changed=$(cat changedFiles.txt)
          else
            files_changed='[]'
          fi
          files_changed=$(echo $files_changed | jq .)

          json_payload=$(jq -n \
            --arg repo_owner "${{ github.repository_owner }}" \
            --arg repo "${{ github.event.repository.name }}" \
            --argjson files_changed "$files_changed" \
            --arg github_token "${{ secrets.GITHUB_TOKEN }}" \
            '{repo_owner: $repo_owner, repo: $repo, files_changed: $files_changed, github_token: $github_token}')
                    
          echo "JSON Payload: $json_payload"
          response=$(curl -s ${{ secrets.AWS_API_URL }} -H "Content-Type: application/json" -d "$json_payload")
          if [ $? -ne 0 ]; then
            echo "Error in API request"
            exit 1
          fi
          echo "API Response: $response"
          if echo "$response" | jq -e . > /dev/null 2>&1; then
            response_content=$(echo $response | jq -r '.updated_doc')
            echo "$response_content" > response.txt
          else
            echo "Invalid JSON response: $response"
            exit 1
          fi
      - name: Update Documentation
        run: |
          cat response.txt > documentation.md
      - name: Commit and Push Changes if Documentation Was Updated
        run: |
          git config --global user.name 'github-actions'
          git config --global user.email 'github-actions@github.com'
          
          if ! git diff --quiet documentation.md; then
            echo "Documentation updated, committing changes..."
            git add documentation.md
            git commit -m "Update documentation with API data"
            
            branch_name=$(echo "${{ github.ref }}" | sed 's|refs/heads/||')
            git fetch origin "$branch_name"
            git rebase origin/"$branch_name"
            git push origin "$branch_name"
          else
            echo "No changes in documentation.md, skipping commit."
          fi
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Usage

1. Push changes to the main branch of your repository.
2. GitHub Actions will trigger and run the workflow to update your documentation automatically.
