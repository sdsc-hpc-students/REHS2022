import instaloader
import os
import json
import multiprocessing
import time
import getpass

pwd = os.path.dirname(os.path.abspath(__file__))

class InstagramCrawler:
    def __init__(self, username, password):
        self.L = instaloader.Instaloader()
        self.L.login(username, password)
        self.user_information_files = os.path.join(pwd, r'user_information')
        self.completed_usernames_file = os.path.join(pwd, r'completed-users.json')
        print("LOGIN SUCCESS")

    def get_account_information(self, account_username:str) -> tuple:
        profile = instaloader.Profile.from_username(self.L.context, account_username)
        profile_information = {'user_id':profile.userid,
                                'full_name':profile.full_name,
                                'username':account_username,
                                'is_private':profile.is_private,
                                'is_verified':profile.is_verified,
                                'media_count':profile.mediacount,
                                'num_followers':profile.followers,
                                'num_following':profile.followees,
                                'followers':'NaN',
                                'following':'NaN'}
  
        # create generator objects for follower and followee list
        if not profile_information['is_private']:
            followers_unprocessed = profile.get_followers()
            followees_unprocessed = profile.get_followees()

            profile_information['followers'] = [user.username for user in followers_unprocessed]
            profile_information['following'] = [user.username for user in followees_unprocessed]
        
        return profile_information

    def write_json(self, file_name, contents, filepath):
        user_information_file = os.path.join(filepath, f'{file_name}.json')
        json_content = json.dumps(contents)
        with open(user_information_file, 'w') as f:
            f.write(json_content)

    def read_json(self, file_name):
        user_information_file = os.path.join(self.user_information_files, f'{file_name}.json') 
        with open(user_information_file, 'r') as f:
            data = f.read()
            data = json.loads(data)

        return data

    def gather_and_write(self, username):
        user_data = self.get_account_information(username)
        self.write_json(username, user_data, self.user_information_files)

    def write_files(self, usernames, batch_size: int):
        if isinstance(usernames, str):
            followers, following = self.read_json(usernames)['followers'], self.read_json(usernames)['following']
            usernames_processes = ([multiprocessing.Process(target=self.gather_and_write, args=[username]) for username in followers],
                                   [multiprocessing.Process(target=self.gather_and_write, args=[username]) for username in following])
        else:  
            usernames_processes = ([multiprocessing.Process(target=self.gather_and_write, args=[username]) for username in usernames])

        for usernames_process in usernames_processes:
            while usernames_process:
                print("STARTING NEXT BATCH")
                if len(usernames_process) >= batch_size:
                    batch = usernames_process[:batch_size]
                else:
                    batch = usernames_process
                    usernames_process = False
                
                for process in batch:
                    print(f'Starting {process}')
                    process.start()
                    if usernames_process is not False:
                        usernames_process.remove(process)
                
                for process in batch:
                    map(lambda x: x.join(), batch)
                
                batch = None
                time.sleep(10)

    def spider(self, starting_username, batch_size=10):
        self.write_files(starting_username, batch_size)
        completed = [f'{starting_username}.json']
        self.write_json(self.completed_usernames_file, completed, pwd)

        while True:
            for user in listdir(self.user_information_files):
                if user in completed:
                    continue
                else:
                    self.write_files(user.split('.json')[0], batch_size)
                    completed.append()
                    self.write_json(self.completed_usernames_file, completed, pwd)

if __name__ == '__main__':
    username = str(input("enter username: "))
    password = getpass.getpass(prompt='Password: ', stream=None)
    instagram_crawler = InstagramCrawler(username, password)
    instagram_crawler.spider('luke.m.monson', batch_size=10)