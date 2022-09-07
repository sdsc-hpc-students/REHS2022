import pyfiglet


class CLI:
    def __init__(self, username, password):
        self.username, self.password = username, password

        start = time.time()
        base_url = "https://icicle.develop.tapis.io"
        try:
            self.t = Tapis(base_url = base_url,
                    username = self.username,
                    password = self.password)
            self.t.get_tokens()
        except Exception as e:
            print(f"\nBROKEN! timeout: {time.time() - start}\n")
            raise

        # V3 Headers
        header_dat = {"X-Tapis-token": self.t.access_token.access_token,
                    "Content-Type": "application/json"}

        # Service URL
        self.url = f"{base_url}/v3"

        print(time.time() - start)
        print(f"base_url: {base_url}")
        print(f"serv_url: {self.url}\n")

        # create authenticator for tapis systems
        self.authenticator = self.t.access_token
        self.access_token = re.findall(r'(?<=access_token: )(.*)', str(self.authenticator))[0]
        print(self.authenticator)

        title = pyfiglet.figlet_format("Tapiconsole")
        print(title)
    
    def command_parser(self, command_input): # parse commands (to some degree of competence) should have just used optparse
        command_input = command_input.split(' -')
        args = command_input[0].split(' ')[1:]
        command_input = list(map(lambda x: tuple(x.split(' ')), command_input))
        command = command_input[0][0]
        kwargs = {element[0]:element[1] for element in command_input[1:] if len(element) > 1}

        return command, args, kwargs


if __name__ == '__main__':
    while True:
        username = str(input('enter your TACC username: '))
        password = getpass('enter your TACC password: ')
        try:
            client = CLI(username, password)
            break
        except Exception as e:
            print('Invalid login, try again')
            continue
    client.main()