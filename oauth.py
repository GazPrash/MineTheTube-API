import os, pickle, secrets
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class OauthVerfication:
    """
    OauthVerfication Class ~ For Genrating Oauth Flow, 
    Authentication & Saving Session Tokens.
    
    """

    def __init__(self) -> None:
        self.credentials = None
        self.hex_path = f"oauth_configs/{(str(secrets.token_hex(16)))}.pickle" #--------->USE THIS FILE PATH TO SEPRATE TOKEN FILES...

    def get_creds(self):
        if os.path.exists(self.hex_path):
            with open(self.hex_path, "rb") as token:
                self.credentials = pickle.load(token)

        # If there are no valid credentials available, then either refresh the token or log in.
        if not self.credentials or not self.credentials.valid:
            if (
                self.credentials
                and self.credentials.expired
                and self.credentials.refresh_token
            ):
                # print("Refreshing Access Token...")
                self.credentials.refresh(Request())
            else:
                # print("Fetching New Tokens...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    "oauth_configs/client_secrets.json",
                    scopes=["https://www.googleapis.com/auth/youtube"],
                )

                flow.run_local_server(
                    port=8000, prompt="consent", authorization_prompt_message=""
                )
                self.credentials = flow.credentials

                # Save the credentials for the next run
                with open(self.hex_path, "wb") as f:
                    pickle.dump(self.credentials, f)

        return self.credentials
