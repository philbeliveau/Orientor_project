# Hybrid LLM–Recommendation System

A **proof-of-concept** project integrating a Large Language Model (LLM) with a Recommendation Engine for personalized learning. The LLM guides learners through **Socratic-style** questioning, extracting key insights such as **learning goals** and **knowledge gaps**. These insights form a **structured query** used by the **Recommendation Engine** to fetch and rank relevant content.

---

## Table of Contents
1. [Key Features](#key-features)
2. [Core Components](#core-components)
3. [Architecture Overview](#architecture-overview)
4. [Installation & Setup](#installation--setup)
5. [Usage](#usage)
6. [Contributing](#contributing)
7. [License](#license)

---

## Key Features
- **LLM-Driven Personalization**: The LLM engages the student with open-ended questions to understand their learning goals and challenges.
- **Structured Query Extraction**: Key topics, difficulty levels, and preferences are extracted into a machine-readable query.
- **Hybrid Recommendation Engine**:
  - **Content-Based Filtering**: Matches user interests with relevant content (videos, articles, interactive exercises).
  - **Collaborative Filtering**: Leverages community data (ratings, completion rates) to suggest widely successful resources.
- **Interactive UI**: A chat-like interface prompts students to refine their queries, view recommended items, and track learning progress.
- **Game Semantics**: The LLM uses guided, step-by-step questioning to nudge deeper thinking, turning each dialogue into a problem-solving "game."  

---

## Core Components
1. **LLM (Orientator)**  
   - Engages with the student.
   - Asks clarifying/socratic questions.
   - Outputs a structured query (JSON) for the recommendation engine.

2. **Recommendation Engine**  
   - Reads the LLM’s structured query.
   - Performs content-based and collaborative filtering.
   - Ranks and returns a list of recommended resources.

3. **Content Database**  
   - Houses curated courses, videos, articles, and exercises.
   - Preprocessed with metadata (topic, difficulty, format) and embeddings.

4. **UI / Frontend**  
   - Displays a conversation interface with the LLM.
   - Presents recommended content in a ranked list.
   - Allows users to save, rate, and track progress.

---

## Architecture Overview
1. **Student asks a question** through the UI.
2. **LLM** interprets the question, extracting key parameters.
3. **LLM** sends a **structured query** (JSON) to the recommendation engine (e.g., `{"topic":"coding","difficulty":"beginner"}`).
4. **Recommendation System** processes the query, searching and ranking content.
5. **Recommendations** (sorted list) are returned to the UI.
6. **Student** interacts further, refining or exploring suggestions.

---

## Installation & Setup
Follow these steps to run locally. Adjust if you’re deploying on different platforms.

1. **Clone the Repo**:
   ```bash
   git clone https://github.com/YourUsername/hybrid-llm-recommendation.git
   cd hybrid-llm-recommendation
   ```
2. **Backend Setup** (Rust Example):
   - Install [Rust](https://www.rust-lang.org/tools/install) using `rustup`.
   - Go to the backend folder:
     ```bash
     cd backend
     cargo build
     ```
   - Start the server:
     ```bash
     cargo run
     ```
3. **Frontend Setup** (React + TailwindCSS Example):
   - Ensure you have Node.js (>= 14) & npm or yarn installed.
   - From the root directory:
     ```bash
     cd frontend
     npm install
     npm run dev
     ```
   - Open [http://localhost:3000](http://localhost:3000) to see the application.

---

## Usage
1. **Open the UI** in your browser.
2. **Type a question** or goal in the chat box. Example: *"I want to learn Python but it’s too hard."*
3. The LLM will **ask clarifying questions** (game semantics), prompting the student.
4. **LLM** builds a structured request.
5. **Recommendation Engine** provides a list of resources (videos, articles, exercises).
6. **Explore** the recommendations, mark favorites, or refine queries.

---

## Contributing
1. **Fork** the repository.
2. **Create a new branch** for your feature or bug fix.
3. Submit a **Pull Request** with a clear description of changes.

We welcome improvements and new features—particularly around **AI-driven ranking**, **dialogue systems**, or **UI enhancements**.

---

## License
This project is released under the [MIT License](./LICENSE). Feel free to use it in your own commercial or non-commercial projects.

---

### **Questions or Feedback?**
Feel free to open an issue or contact the maintainers for any queries, suggestions, or contributions.

---

**Thank you for checking out our Hybrid LLM–Recommendation System!**

