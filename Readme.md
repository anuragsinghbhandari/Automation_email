# Gmail Automation Assistant

## Overview
The Gmail Automation Assistant is a web application that leverages Flask and React to automate email responses using AI. It connects to your Gmail account, allowing you to upload PDF files as a knowledge base and generate replies to unread emails based on the content of those files.

## Features
- **OAuth2 Authentication**: Securely connect your Gmail account.
- **Email Automation**: Automatically respond to unread emails using AI-generated replies.
- **Knowledge Base**: Upload PDF files to create a context for generating responses.
- **User-Friendly Interface**: Built with React for a smooth user experience.

## Requirements
- Python 3.8+
- Node.js (for the frontend)
- A Google Cloud project with Gmail API enabled and OAuth2 credentials set up.

## Installation

### Backend
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory and add your environment variables:
   ```plaintext
   FLASK_SECRET_KEY=<your_secret_key>
   ```

5. Place your `client_secret.json` file in the root directory.

6. Run the backend:
   ```bash
   python app.py
   ```

### Frontend
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install the frontend dependencies:
   ```bash
   npm install
   ```

3. Run the frontend:
   ```bash
   npm run dev
   ```

## Usage
- Access the application at `http://localhost:5000` for the backend and `http://localhost:5173` for the frontend.
- Follow the prompts to log in and start using the automation features.

### Authentication
- Click on the "Connect with Gmail" button to initiate the OAuth2 flow.
- After successful authentication, you can upload PDF files to create a knowledge base.

### Starting Automation
- Once authenticated, you can upload PDF files and start the automation process, which will monitor your Gmail for unread messages and respond based on the knowledge base.

## License
This project is licensed under the MIT License.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## Acknowledgments
- [Flask](https://flask.palletsprojects.com/) - The web framework used for the backend.
- [React](https://reactjs.org/) - The JavaScript library for building the user interface.
- [Google API](https://developers.google.com/gmail/api) - For interacting with Gmail.
- [Langchain](https://langchain.com/) - For AI-driven responses.

## Contact
For any inquiries, please reach out to [your-email@example.com].