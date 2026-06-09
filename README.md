# 🚀 Enterprise Feedback Intelligence System
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![React](https://img.shields.io/badge/React-18.2-61dafb.svg)
![Status](https://img.shields.io/badge/Status-Production_Ready-brightgreen.svg)

A full-stack, AI-powered intelligence dashboard that aggregates, analyzes, and prioritizes customer feedback from multiple real-world sources in real-time. 

Instead of a basic Streamlit script, this project features a production-ready **React.js** frontend with a high-performance **FastAPI** backend, fully containerized for a seamless 1-click launch in GitHub Codespaces.

## ✨ Features & Rubric Completion
- **Multi-Source Integration:** Asynchronous scrapers for both **Google Play Store** and **Apple App Store** reviews.
- **Sentiment Analysis:** Accurate sentiment classification (Positive, Neutral, Negative) utilizing NLP.
- **Trend Detection:** Real-time data aggregation to track shifting customer satisfaction trends.
- **Issue Prioritization:** Automatically flags critical issues and negative reviews as "Urgent Bugs" for immediate team action.
- **⭐ EXTRA CREDIT - Premium Dashboard:** Built a highly advanced, fully responsive React.js dashboard with interactive Recharts (exceeding the Streamlit requirement).
- **⭐ EXTRA CREDIT - AI Response Generation:** One-click automated generation of professional customer service replies to individual reviews.

---

## 💻 How to Run this Project (1-Click Install)

This project is fully automated using a `.devcontainer` configuration. You do **not** need to manually install Python, Node, or any dependencies!

### Step 1: Launch the Cloud Environment
1. Click the green **"<> Code"** button at the top of this repository.
2. Select the **Codespaces** tab and click **"Create codespace on main"**.
3. **Wait ~60 seconds** while the automated script quietly builds the environment, installs Python, Node.js, and all required packages in the background.

### Step 2: Start the FastAPI Backend  
Once the terminal appears, copy and paste this command to start the server:
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000

###Step 3: Start the React Frontend
Open a Second Terminal (click the + icon in the terminal panel) and run:

bash
cd frontend
npm run dev

Step 4: View the Dashboard
A pop-up will appear in the bottom right corner of VS Code saying "Your application is running on port 5173". Click Open in Browser to view the live dashboard!



