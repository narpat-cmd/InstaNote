#!/bin/bash
cd D:/InstaNote
gh repo create InstaNote --public --source=. --remote=origin --push
gh api repos/narpat-cmd/InstaNote --jq '.html_url'