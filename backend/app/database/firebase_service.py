import os

import firebase_admin
from firebase_admin import credentials, firestore


def get_firestore_client():
    """Return a Firestore client when Firebase credentials are configured."""
    if not firebase_admin._apps:
        project_id = os.getenv("FIREBASE_PROJECT_ID")
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

        if credentials_path:
            if not os.path.isfile(credentials_path):
                raise RuntimeError(
                    "The configured Firebase credentials file was not found."
                )
            cred = credentials.Certificate(credentials_path)
            firebase_admin.initialize_app(
                cred,
                {"projectId": project_id} if project_id else None,
            )
        elif project_id:
            firebase_admin.initialize_app(
                options={"projectId": project_id}
            )
        else:
            return None

    return firestore.client()
