import os
import json

pwd = os.path.dirname(os.path.abspath(__file__))
database_file = r'user_database.cypher'
user_info_file = r'user_information'


class databaseBuilder:
    def __init__(self, user_data_directory=None, database_file=None):
        self.cypher_file = os.path.join(pwd, database_file)
        self.user_info_file = os.path.join(pwd, user_data_directory)
        self.user_dict = {}

    def create_user(self, user_info:dict) -> tuple:
        user_id = f'U{user_info["user_id"]}'
        properties = f'{{userid:"{user_id}}", username:"{user_info["username"]}", fullname:"{user_info["full_name"]}", isprivate:"{user_info["is_private"]}", isverified:"{user_info["is_verified"]}", mediacount:"{user_info["media_count"]}", numfollowers:"{user_info["num_followers"]}", numfollowing:"{user_info["num_following"]}"}}'
        expression = f'CREATE ({user_id}:USER {properties})' + '\n'

        return (expression, user_id, user_info['followers'], user_info['following'])
        #return user_info['username'], {'user_node':expression, 'followers':user_info['followers'], 'following':user_info['following']}

    def create_relationship(self, node_1_username, node_2_username, relationship: str):
        if relationship == 'FOLLOWED_BY':
            arrow1, arrow2 = '<-', '-'
        if relationship == 'FOLLOWING':
            arrow1, arrow2 = '-', '->'

        expression = f'''\nMATCH (USER1), (USER2) WHERE USER1.username = "{node_1_username}" AND USER2.username = "{node_2_username}" CREATE (USER1){arrow1}[:{relationship}]{arrow2}(USER2)''' 
        
        return expression

    def read_json_file(self, file_name):
        with open(file_name, 'r') as f:
            data = f.read()
            data = json.loads(data)
        return data

    def write_to_file(self, expression_list: list, file_name):
        if isinstance(expression_list[0], tuple):
            expression_list = list(map(lambda x: x[0], expression_list))

        with open(file_name, 'a') as f:
            for l in expression_list:
                try:
                    f.write(l)
                except UnicodeEncodeError:
                    continue


    def construct_user_data_graph(self):
        file_list = os.listdir(self.user_info_file)

        node_list = [self.create_user(self.read_json_file(f'{self.user_info_file}/{user_file}'))for user_file in file_list]

        user_id_list = [node[1] for node in node_list]

        self.write_to_file(node_list, self.cypher_file)

        for expression, user_id, followers, following in node_list:
            if isinstance(followers, list):
                user_followers = [self.create_relationship(user_id, follower, "FOLLOWED_BY") for follower in followers if follower in username_list]
                if user_followers:
                    self.write_to_file(user_followers, self.cypher_file)

            if isinstance(following, list):
                user_followees = [self.create_relationship(username, followee, "FOLLOWING") for followee in following if followee in username_list]
                if user_followees:
                    self.write_to_file(user_followees, self.cypher_file)


if __name__ == "__main__":
    database_builder = databaseBuilder(user_data_directory=user_info_file, database_file=database_file)
    database_builder.construct_user_data_graph()

