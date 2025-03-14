# TypingMind Plugin Server 🚀

This repository contains the backend server code for some of my TypingMind plugins. Currently, it contains the following plugins:
1. [Brave Search](https://cloud.typingmind.com/plugins/p-01JJD655P2QCGCG3MGBQ50RCSV)
2. [Vectorize Query](https://cloud.typingmind.com/plugins/p-01JJD662KCM4X901JRQRF8DG6F)
3. [DOCX Generator](https://cloud.typingmind.com/plugins/p-01JM2R9TM8GVJJGAKGWAN1YR8E)

## How to deploy to Render.com

1.  **Create a New Web Service on Render:**
    *   Go to the [Render Dashboard](https://dashboard.render.com/) and log in.
    *   Create a new Web Service.
    *   Set your source code as Public Git repository and enter `https://github.com/Btran1291/TypingMind-Plugin-Server/` as the repo URL.

2.  **Configure Your Web Service:**
    *   **Name:** Enter a name for your web service (e.g., `typingmind-plugin-server`).
    *   **Language:** Select **"Python"**.
    *   **Region:** Choose the region closest to you.
    *   **Build Command:** Enter `pip install -r requirements.txt`.
    *   **Start Command:** Enter `gunicorn wsgi:application`.
    *   **Instance Type:** Choose the instance type that suits your needs (e.g., Free, Starter, etc.).

3.  **Create Web Service:**
    *   Click on the **"Create Web Service"** button.

4.  **Wait for Deployment:**
    *   Render will now build and deploy your application. This process may take a few minutes.
    *   You can monitor the progress in the Render dashboard.

5.  **Access Your Deployed Application:**
    *   Once the deployment is complete, Render will provide a URL for your deployed application.
    *   You can use this URL in your TypingMind plugin settings.

*Note: This was written with personal use in mind and does not handle concurrency well. If you are a business user who might have multiple customers using the plugins at the same time, remember to set up a higher number of gunicorn workers and threads for better concurrency performance.*
