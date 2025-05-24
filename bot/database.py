from pymongo import MongoClient
from datetime import datetime
import config

class Database:
    def __init__(self):
        self.client = MongoClient(config.MONGO_CONNECTION_STRING)
        self.db = self.client["chatgpt_bot"]
        self.users = self.db["users"]
        self.dialogs = self.db["dialogs"]

    def check_if_user_exists(self, user_id):
        return self.users.count_documents({"_id": user_id}) > 0

    def add_new_user(self, user_id, chat_id, username=None, first_name=None, last_name=None):
        self.users.insert_one({
            "_id": user_id,
            "chat_id": chat_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "created_at": datetime.utcnow(),
            "current_dialog_id": None,
            "n_used_tokens": {},
            "n_transcribed_seconds": 0.0,
            "n_generated_images": 0,
            "current_model": None,
            "current_chat_mode": "assistant",
            "last_interaction": None,
        })

    def get_user_attribute(self, user_id, attribute):
        user = self.users.find_one({"_id": user_id})
        return user.get(attribute) if user else None

    def set_user_attribute(self, user_id, attribute, value):
        self.users.update_one({"_id": user_id}, {"$set": {attribute: value}})

    def start_new_dialog(self, user_id):
        dialog_id = str(datetime.utcnow().timestamp())
        self.set_user_attribute(user_id, "current_dialog_id", dialog_id)
        self.dialogs.insert_one({"_id": dialog_id, "user_id": user_id, "messages": []})

    def get_dialog_messages(self, user_id, dialog_id=None):
        dialog_id = dialog_id or self.get_user_attribute(user_id, "current_dialog_id")
        dialog = self.dialogs.find_one({"_id": dialog_id})
        return dialog["messages"] if dialog else []

    def set_dialog_messages(self, user_id, messages, dialog_id=None):
        dialog_id = dialog_id or self.get_user_attribute(user_id, "current_dialog_id")
        self.dialogs.update_one({"_id": dialog_id}, {"$set": {"messages": messages}})

    def update_n_used_tokens(self, user_id, model, n_input_tokens, n_output_tokens):
        tokens = self.get_user_attribute(user_id, "n_used_tokens") or {}
        if model not in tokens:
            tokens[model] = {"n_input_tokens": 0, "n_output_tokens": 0}
        tokens[model]["n_input_tokens"] += n_input_tokens
        tokens[model]["n_output_tokens"] += n_output_tokens
        self.set_user_attribute(user_id, "n_used_tokens", tokens)
