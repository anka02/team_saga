#!/usr/bin/env python3
import os
import sys
import requests
import pprint


def main():
    pp = pprint.PrettyPrinter(indent=4)

    username = os.getenv("RASA_X_USERNAME", "me")
    password = os.getenv("RASA_X_PASSWORD")
    base_url = os.getenv("RASA_BASE_URL", "http://localhost:5002")
    bot_name = os.getenv("RASA_BOT_NAME", "MyBot")
    bot_description = os.getenv("RASA_BOT_DESCRIPTION", "")

    print("Use RASA username:", username)
    print("Use RASA password:", password)
    print("Use RASA base URL:", base_url)

    if not username:
        print("Error: No username specified, specify environment variable RASA_X_USERNAME", file=sys.stderr)
        return 1

    if not password:
        print("Error: No password specified, specify environment variable RASA_X_PASSWORD", file=sys.stderr)
        return 1

    if not base_url:
        print("Error: No base_url specified, specify environment variable RASA_BASE_URL", file=sys.stderr)
        return 1

    r = requests.post(base_url + "/api/auth", json={"username": username, "password": password})
    r.raise_for_status()
    r_json = r.json()
    access_token = r_json["access_token"]

    headers = {"Authorization": "Bearer {}".format(access_token), "Accept": "application/json"}

    r = requests.get(base_url + "/api/chatToken?token={}".format(access_token), headers=headers)
    r.raise_for_status()
    r_json = r.json()
    chat_token = r_json['chat_token']

    expires = 0
    r = requests.put(base_url + "/api/chatToken",
                     headers=headers,
                     json={"bot_name": bot_name, "description": bot_description,
                           "expires": expires,
                           "chat_token": chat_token}
                     )
    r.raise_for_status()
    r_json = r.json()
    # pp.pprint(r_json)
    guest_url = base_url + "/guest/conversations/production/{}".format(chat_token)
    print("Guest URL: ", guest_url)

    return 0


if __name__ == '__main__':
    sys.exit(main())
