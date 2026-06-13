# Pyloom Tech Website

This repository contains a simple static website for **Pyloom Tech**.

## What is included

- `index.html` — the homepage
- `styles.css` — styling for the website
- `script.js` — a small interaction script

## How to use

1. Open `index.html` in a browser to preview the site locally.
2. Customize the content, branding, and styling as needed.

## Publish to GitHub

1. Initialize git if needed:
   ```bash
   git init
   git add .
   git commit -m "Initial Pyloom Tech website"
   ```
2. Create a GitHub repository named `pyloomweb` or another name you prefer.
3. Add the remote and push:
   ```bash
   git remote add origin https://github.com/<your-username>/<repo-name>.git
   git branch -M main
   git push -u origin main
   ```

## Deploy to prabhuhost

- If prabhuhost supports FTP/SFTP, upload the site files from this repository to your hosting server.
- If prabhuhost supports GitHub-based deployment, connect the GitHub repository and select the `main` branch.

## cPanel Git deployment

This repository now includes a `.cpanel.yml` file, which cPanel uses to deploy your site files to the `public_html` directory automatically.

1. In cPanel, open **Git Version Control**.
2. Create or clone a repository using this URL:
   ```text
   https://github.com/<your-username>/<repo-name>.git
   ```
3. Choose the branch you are using (`master` or `main`).
4. Confirm the repository path is valid and writable.

When cPanel detects `.cpanel.yml` in the repository root, it will run the deployment commands automatically after a push.

> If you want, I can also help you add a contact form, a services page, or convert this into a React/Vite site.
