#!/bin/bash

# Define variables
GITHUB_USER="vladimirovertheworld"
GITHUB_REPO="picresizer"
LOCAL_REPO_PATH="$HOME/picresizer"
SSH_PRIVATE_KEY="$HOME/.ssh/id_ed25519"
GIT_SSH_COMMAND="ssh -i $SSH_PRIVATE_KEY -o StrictHostKeyChecking=no"

echo "Checking Git environment..."
echo "--------------------------------"

# Check if Git is installed
if ! command -v git &>/dev/null; then
    echo "Error: Git is not installed. Please install Git before proceeding."
    exit 1
fi

# Display Git version
echo "Git version: $(git --version)"

# Check global Git username and email
GIT_USER=$(git config --global user.name)
GIT_EMAIL=$(git config --global user.email)
if [[ -z "$GIT_USER" || -z "$GIT_EMAIL" ]]; then
    echo "Warning: Git global username or email is not set."
    echo "Set it using:"
    echo "  git config --global user.name \"Your Name\""
    echo "  git config --global user.email \"you@example.com\""
else
    echo "Git Global User: $GIT_USER"
    echo "Git Global Email: $GIT_EMAIL"
fi

# Ensure the SSH key exists
if [ ! -f "$SSH_PRIVATE_KEY" ]; then
    echo "Error: SSH private key not found at $SSH_PRIVATE_KEY"
    exit 1
fi

# Ensure the local repository directory exists
if [ ! -d "$LOCAL_REPO_PATH" ]; then
    echo "Error: Directory $LOCAL_REPO_PATH does not exist."
    exit 1
fi

# Navigate to the correct repo directory
cd "$LOCAL_REPO_PATH" || { echo "Error: Unable to access directory $LOCAL_REPO_PATH."; exit 1; }

# Check if it's a Git repository
if [ ! -d ".git" ]; then
    echo "Initializing a new Git repository..."
    git init
    git remote add origin git@github.com:$GITHUB_USER/$GITHUB_REPO.git
fi

# Verify the correct remote repository
REMOTE_URL=$(git remote get-url origin 2>/dev/null)
EXPECTED_URL="git@github.com:$GITHUB_USER/$GITHUB_REPO.git"
if [[ "$REMOTE_URL" != "$EXPECTED_URL" ]]; then
    echo "Fixing incorrect remote repository..."
    git remote remove origin
    git remote add origin "$EXPECTED_URL"
fi

# Ensure the main branch exists
if ! git rev-parse --verify main >/dev/null 2>&1; then
    echo "Creating 'main' branch..."
    git checkout -b main
else
    git checkout main
fi

# Configure Git
git config user.name "$GITHUB_USER"
git config user.email "vladimir@overtheworld.uk"

# Ensure SSH key is added to the agent
if ! ssh-add -l | grep -q "$SSH_PRIVATE_KEY"; then
    echo "Adding SSH key to agent..."
    eval "$(ssh-agent -s)"
    ssh-add "$SSH_PRIVATE_KEY"
fi

# Test SSH connection to GitHub
echo "Testing GitHub SSH authentication..."
ssh -T git@github.com
if [ $? -ne 1 ]; then
    echo "Error: GitHub SSH authentication failed. Ensure your SSH key is added to GitHub."
    echo "You can add it manually at: https://github.com/settings/keys"
    exit 1
fi

# Add all files, commit, and push to GitHub
git add .
if git diff-index --quiet HEAD --; then
    echo "No changes to commit."
else
    git commit -m "Automated commit and push from script"
fi

# Push changes with SSH authentication
echo "Pushing to GitHub..."
GIT_SSH_COMMAND="$GIT_SSH_COMMAND" git push -u origin main

if [ $? -eq 0 ]; then
    echo "Push completed successfully."
else
    echo "Error: Failed to push changes to GitHub."
    exit 1
fi
