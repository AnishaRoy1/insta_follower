
# app.py

from flask import Flask, render_template, request
from instagram_private_api import Client
from uuid import uuid4
import csv
import streamlit as st
app = Flask(__name__)

# Replace with your Instagram credentials
INSTAGRAM_USERNAME = "sightunseen96"  # Your default Instagram username
INSTAGRAM_PASSWORD = "koushiki"  # Your default Instagram password

# Initialize a default 'api' variable
api = Client(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_lists', methods=['POST'])
def get_lists():
    global api  # Access the global 'api' variable

    # Retrieve Instagram credentials from the form
    username = request.form['username']
    password = request.form['password']

    # Update 'api' variable if new credentials are provided
    if username and password:
        api = Client(username, password)

    # Get your own user ID
    user_id = api.authenticated_user_id

    # Get your followers using a manually generated rank token
    rank_token = str(uuid4())
    followers = api.user_followers(user_id, rank_token=rank_token)

    # Create a CSV file with UTF-8 encoding
    csv_file_path = 'followers.csv'

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Username', 'Full Name', 'User ID']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        # Write the first set of followers
        for follower in followers['users']:
            writer.writerow({
                'Username': follower['username'],
                'Full Name': follower['full_name'],
                'User ID': follower['pk']
            })

        # Fetch and write additional followers while paginating
        while 'next_max_id' in followers:
            next_max_id = followers['next_max_id']
            followers = api.user_followers(user_id, rank_token=rank_token, max_id=next_max_id)

            for follower in followers['users']:
                writer.writerow({
                    'Username': follower['username'],
                    'Full Name': follower['full_name'],
                    'User ID': follower['pk']
                })

    print(f'CSV file with followers data saved to: {csv_file_path}')

    # Get your following using a manually generated rank token
    rank_token = str(uuid4())
    following = api.user_following(user_id, rank_token=rank_token)

    # Create a CSV file with UTF-8 encoding for following
    csv_file_path_following = 'following.csv'

    with open(csv_file_path_following, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Username', 'Full Name', 'User ID']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        # Write the first set of following
        for followed_user in following['users']:
            writer.writerow({
                'Username': followed_user['username'],
                'Full Name': followed_user['full_name'],
                'User ID': followed_user['pk']
            })

        # Fetch and write additional following while paginating
        while 'next_max_id' in following:
            next_max_id = following['next_max_id']
            following = api.user_following(user_id, rank_token=rank_token, max_id=next_max_id)

            for followed_user in following['users']:
                writer.writerow({
                    'Username': followed_user['username'],
                    'Full Name': followed_user['full_name'],
                    'User ID': followed_user['pk']
                })

    print(f'CSV file with following data saved to: {csv_file_path_following}')

    # Read the usernames from the followers CSV file
    with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        follower_usernames = {row['Username'] for row in reader}

    # Read the usernames from the following CSV file
    with open(csv_file_path_following, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        following_usernames = {row['Username'] for row in reader}

    # Find unfollowers
    unfollowers_usernames = following_usernames - follower_usernames

    # Create a CSV file with sorted unfollower usernames
    csv_file_path_unfollowers = 'unfollowers.csv'
    with open(csv_file_path_unfollowers, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Username']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for username in sorted(unfollowers_usernames):
            writer.writerow({'Username': username})

    print(f'CSV file with sorted unfollowers usernames saved to: {csv_file_path_unfollowers}')

    return render_template('result.html', followers=follower_usernames, following=following_usernames, unfollowers=unfollowers_usernames)

if __name__ == '__main__':
    app.run(debug=True)
