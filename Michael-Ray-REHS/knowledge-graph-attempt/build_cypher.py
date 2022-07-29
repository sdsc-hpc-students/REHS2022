import os
import json
from neo4j import GraphDatabase

pwd = os.path.dirname(os.path.abspath(__file__))
database_file = r'user_database.cypher'
user_info_file = r'user_information'


class databaseBuilder:
    def __init__(self, user_data_directory=None, database_file=None):
        self.cypher_file = os.path.join(pwd, database_file)
        self.user_info_file = os.path.join(pwd, user_data_directory)

    def create_user(self, user_info:dict) -> tuple:
        properties = f'{{userid:"{user_info["user_id"]}", username:"{user_info["username"]}", fullname:"{user_info["full_name"]}", isprivate:"{user_info["is_private"]}", isverified:"{user_info["is_verified"]}", mediacount:"{user_info["media_count"]}", numfollowers:"{user_info["num_followers"]}", numfollowing:"{user_info["num_following"]}"}}'
        expression = f'CREATE (:USER {properties})' + '\n'

        return (expression, user_info['username'], user_info['followers'], user_info['following'])
        #return user_info['username'], {'user_node':expression, 'followers':user_info['followers'], 'following':user_info['following']}

    def create_relationship(self, user1, user2, relationship: str):
        if relationship == 'FOLLOWED_BY':
            user1, user2 = user2, user1

        expression = f'''\nMATCH (USER1), (USER2) WHERE USER1.username = "{user1}" AND USER2.username = "{user2}" CREATE (USER1)-[:FOLLOWING]->(USER2)''' 
        
        return expression

    def empty_file(self, file_name):
        with open(file_name, 'w') as f:
            f.write('')

    def read_json_file(self, file_name):
        with open(file_name, 'r') as f:
            data = f.read()
            data = json.loads(data)
        return data

    def write_to_file(self, expression_list: list, file_name):
        if isinstance(expression_list[0], tuple):
            expression_list = list(map(lambda x: x[0], expression_list))

        with open(file_name, 'a+') as f:
            for l in expression_list:
                contents = f.read()
                if l not in contents:
                    try:
                        f.write(l)
                    except UnicodeEncodeError:
                        continue

    def construct_user_data_graph(self):
        file_list = os.listdir(self.user_info_file)

        node_list = [self.create_user(self.read_json_file(f'{self.user_info_file}/{user_file}'))for user_file in file_list]

        username_list = [node[1] for node in node_list]

        self.write_to_file(node_list, self.cypher_file)

        for expression, username, followers, following in node_list:
            if isinstance(followers, list):
                user_followers = [self.create_relationship(username, follower, "FOLLOWED_BY") for follower in followers if follower in username_list]
                if user_followers:
                    self.write_to_file(user_followers, self.cypher_file)

            if isinstance(following, list):
                user_followees = [self.create_relationship(username, followee, "FOLLOWING") for followee in following if followee in username_list]
                if user_followees:
                    self.write_to_file(user_followees, self.cypher_file)


if __name__ == "__main__":
    database_builder = databaseBuilder(user_data_directory=user_info_file, database_file=database_file)
    database_builder.empty_file(database_builder.cypher_file)
    database_builder.construct_user_data_graph()

