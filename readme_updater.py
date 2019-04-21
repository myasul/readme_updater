#!/usr/bin/env python3
import configparser
import requests
import base64


class ReadMeUpdater:
    def __init__(self, config):
        self._username = config.get('GITHUB', 'USERNAME')
        self._repository = config.get('GITHUB', 'REPOSITORY')
        self._api_url = config.get('GITHUB', 'API_URL')
        self._accept = config.get('GITHUB', 'ACCEPT')

    def get_readme(self):
        headers = {'Accept': self._accept}
        github_readme_url = ("{api_url}/repos/{username}/" +
                             "{repository}/readme").format(
            api_url=self._api_url,
            username=self._username,
            repository=self._repository)

        resp = requests.get(github_readme_url, headers=headers)
        resp_dict = resp.json()

        if resp_dict.get('content'):
            readme = base64.b64decode(resp_dict.get('content'))
            filename = "{}_{}_README.md".format(
                self._username,
                self._repository
            )
            with open(filename, "w+", encoding="utf-8") as file:
                file.write(readme.decode())

    def update_readme(self):
        pass

    def generate_preview(self):
        pass


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    readme = ReadMeUpdater(config)
    readme.get_readme()


if __name__ == "__main__":
    main()
