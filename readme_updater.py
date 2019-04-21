#!/usr/bin/env python3
import configparser
import requests
import base64
from grip import export
from xhtml2pdf import pisa


class ReadMeUpdater:
    def __init__(self, config):
        self._username = config.get('GITHUB', 'USERNAME')
        self._repository = config.get('GITHUB', 'REPOSITORY')
        self._api_url = config.get('GITHUB', 'API_URL')
        self._accept = config.get('GITHUB', 'ACCEPT')

    def pull_latest_readme(self):
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
            with open(filename, "w+", encoding="utf-8") as md:
                md.write(readme.decode())

    def push_updated_readme(self):
        pass

    def generate_preview(self):
        # TODO :: Add File Error Handling
        readme_filename = "{}_{}_README.md".format(
            self._username,
            self._repository
        )

        preview_filename = "{}_{}_README_preview.pdf".format(
            self._username,
            self._repository
        )

        html_filename = "{}_{}_README_preview.html".format(
            self._username,
            self._repository
        )
        export(path=readme_filename, out_filename=html_filename)

        # with open(html_filename, "r") as html,\
        #         open(preview_filename, "w+b") as preview:
        #     pisa_status = pisa.CreatePDF(html.read(), preview)

        # return pisa_status.err


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    readme = ReadMeUpdater(config)
    readme.pull_latest_readme()
    preview_status = readme.generate_preview()
    print(preview_status)


if __name__ == "__main__":
    main()
