# Gmail Automation Assistant

## Overview
The Gmail Automation Assistant is a web application that leverages Flask and React to automate email responses using AI. It connects to your Gmail account, allowing you to upload PDF files as a knowledge base and generate replies to unread emails based on the content of those files.

## Features
- **OAuth2 Authentication**: Securely connect your Gmail account.
- **Email Automation**: Automatically respond to unread emails using AI-generated replies.
- **Knowledge Base**: Upload PDF files to create a context for generating responses.
- **User-Friendly Interface**: Built with React for a smooth user experience.

## Requirements
- Python 3.8+ (python 3.10 recommended)
- Node.js (for the frontend)
- A Google Cloud project with Gmail API enabled and OAuth2 credentials set up.
   - Go to console.cloud.google.com.
   - Login then click on select project in top left.
   - Click on new project and create a new project.
   - Now select the created project.
   - In navigation menu, hover over apis & services and click on library.
   - Search and enable gmail api.
   - In navigation menu, hover over apis & services and click on Oauth consent screen.
   - Select user type external and then create.
   - Then add app name , contact support email and developer contact email click on save and continue.
   - In scopes no change , just save and continue.
   - In test users , add users email who will test your app.
   - Save and click on go to dashboard.
   - Now in credentials section click on create credentials and select oauth client id.
   - App type as web application, in authorised redirect uri add https://automation-email.onrender.com/oauth2callback and save.
   - Pop up will apear anc click on download json and save it as client_secret.json in root directory.
- GROQ_API_KEY.
   - Go to console.groq.com/keys.
   - Create Api key and save this in .env file in root folder.
   - Format (GROQ_API_KEY = PASTE KEY HERE).

## Installation

### Backend
1. Clone the repository:
   ```bash
   git clone https://github.com/anuragsinghbhandari/Automation_email.git
   cd Automation_email
   ```

2. Create a virtual environment:(only once during inital setup)
   ```bash
   python -m venv venv
   ```
3. Activate Virtual environment:(everytime you open the project folder)
   ```bash
   # On mac/ linux
   source venv/bin/activate
   # On Windows use
   `venv\Scripts\activate`
   ```
4. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

5. Create a `.env` file in the root directory and add your environment variables:
   ```plaintext
   GROQ_API_KEY=<your_secret_key>
   ```

6. Place your `client_secret.json` file in the root directory. 
   **Note - Rename the credentials file to client_secret.json and the credentials file is need to be downloaded from google cloud console.**

7. Run the backend:
   ```bash
   python app.py
   ```
   Backend will run at automation-email.onrender.com
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
   Frontend will run at automation-email.vercel.app
## Usage
- Access the application `https://automation-email.vercel.app` in browser for the frontend.
- Follow the prompts to log in and start using the automation features.

### Authentication
- Click on the "Connect with Gmail" button to initiate the OAuth2 flow.
- After successful authentication, you can upload PDF files to create a knowledge base.

### Starting Automation
- Once authenticated, you can upload PDF files and start the automation process, which will monitor your Gmail for unread messages and respond based on the knowledge base.
- **Note- Knowledge base creation will take time, patience is encouraged**

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
For any inquiries, please reach out to [Author](mailto:anuoo3ups@gmail.com).
