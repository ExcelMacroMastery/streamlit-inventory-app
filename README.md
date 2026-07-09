This Inventory Web App is an example of a real-world style application using Python and Streamlit.

**Prerequisites:**
1. Code Editor(I use VS Studio)
2. Python installed(I install using the Ananconda installation)

**How to use:**
1. Download the code.
2. Create an environment for this app on your local machine(optional but recommended).
3. Install dependencies: `pip install -r requirements.txt`
4. Build the database: `python migrate.py`
5. Select "StreamLit Debug": You can do this from "Run and Debug" in the side panel of VS Studio.

**Troubleshooting:**
1. Code runs but doesn't appear in browser.
Solution 1: First time you it runs you may be asked for email in terminal. Click on email and hit enter.
Solution 2: Make sure you have selected the correct debugger("StreamLit Debug" - see above).

2. Error ModuleNotFound
e.g.     from login.auth import require_login
ModuleNotFoundError: No module named 'login'
Solution: Make sure you have selected the correct debugger("StreamLit Debug" - see above).



