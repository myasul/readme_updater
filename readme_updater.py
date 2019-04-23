#!/usr/bin/env python3
import requests
import base64
import json
import traceback
from configparser import ConfigParser, NoSectionError
from subprocess import call
from grip import export

USER_AGENT = 'myasul'
USERNAME = 'myasul'
PASSWORD = ''


class ReadMeUpdater:
    def __init__(self, config):
        self._config = config
        self._username = config.get('GITHUB', 'username')
        self._repository = config.get('GITHUB', 'repository')
        self._api_url = config.get('GITHUB', 'api_url')
        self._accept = config.get('GITHUB', 'accept')
        self._html_filename = ''
        self._preview_filename = ''
        self._readme_filename = ''
        self._generate_filenames()

    def pull_latest_readme(self):
        headers = {'Accept': self._accept}
        github_readme_url = ('{api_url}/repos/{username}/' +
                             '{repository}/readme').format(
            api_url=self._api_url,
            username=self._username,
            repository=self._repository)

        resp = requests.get(github_readme_url, headers=headers)
        resp_dict = resp.json()

        # Always update SHA and path of the README file
        self._update_config_file(
            'GITHUB', 'readme_sha', resp_dict.get('sha'))

        self._update_config_file(
            'GITHUB', 'readme_path', resp_dict.get('path'))

        if resp_dict.get('content'):
            readme = base64.b64decode(resp_dict.get('content'))
            filename = '{}_{}_README.md'.format(
                self._username,
                self._repository
            )
            with open(filename, 'w+', encoding='utf-8') as md:
                md.write(readme.decode())

    def push_updated_readme(self):
        # TODO :: Add a way to authenticate user

        if not self._config.get('GITHUB', 'readme_sha'):
            # TODO :: Add SHA validation
            pass

        try:
            with open(self._readme_filename, "r") as readme_file:

                content = readme_file.read()

                if isinstance(content, str):
                    content = content.encode()

                content = base64.b64encode(content).decode()

                headers = {
                    'Accept': self._accept,
                    'Authorization': "Basic " + base64.b64encode((USERNAME + ":" + PASSWORD).encode("utf-8")).decode("utf-8").replace('\n', ''),
                    'User-Agent': USER_AGENT
                }

                params = {
                    'message': 'Update README.md',
                    'content': content,
                    'sha': self._config.get('GITHUB', 'readme_sha'),
                    'branch': 'master',
                    'committer': {
                        'name': 'Matthew Yasul',
                        'email': 'yasulmatthew@gmail.com'
                    },
                    'author': {
                        'name': 'Matthew Yasul',
                        'email': 'yasulmatthew@gmail.com'
                    },
                }

                path = self._config.get('GITHUB', 'readme_path')

                github_update_url = ('{api_url}/repos/{username}/' +
                                     '{repository}/contents/{path}').format(
                                         api_url=self._api_url,
                                         username=self._username,
                                         repository=self._repository,
                                         path=path
                )

                print('GITHUB URL: {}'.format(github_update_url))

                resp = requests.put(github_update_url,
                                    data=json.dumps(params), headers=headers)

                if resp.status_code != 200:
                    # TODO :: Add validation
                    pass

                resp_json = resp.json()
                self._update_config_file(
                    'GITHUB', 'readme_sha', resp_json.get('sha'))

        except IOError:
            print("ERROR!")
            traceback.print_exc()
            # TODO :: Add error handling
            pass

    def generate_preview(self):
        self._generate_html()
        self._generate_pdf()

    def _generate_html(self):
        # TODO :: Add File Error Handling
        export(path=self._readme_filename, out_filename=self._html_filename)

    def _generate_pdf(self):
        # TODO :: Add in README.md to install wkthmtopdf
        call([
            'wkhtmltopdf',
            '-q',
            '--title', self._readme_filename,
            self._html_filename,
            self._preview_filename
        ])

    def _generate_filenames(self):
        self._readme_filename = '{}_{}_README.md'.format(
            self._username,
            self._repository
        )

        self._preview_filename = '{}_{}_README_preview.pdf'.format(
            self._username,
            self._repository
        )

        self._html_filename = '{}_{}_README_preview.html'.format(
            self._username,
            self._repository
        )

    def _update_config_file(self, section, option, value):
        try:
            self._config.set(section, option, value)
            with open('config.ini', 'w') as configfile:
                self._config.write(configfile)
        except NoSectionError:
            # TODO :: Add more logic
            pass


def main():
    config = ConfigParser()
    config.read('config.ini')
    readme = ReadMeUpdater(config)
    readme.pull_latest_readme()
    readme.push_updated_readme()
    readme.generate_preview()


if __name__ == '__main__':
    main()
