# Here's where I get all of the data from ToolHub
import os
import requests

REQUEST_LABEL = 'Toolhunt API'
USER_INFO = 'User: NicoleLBee'
headers = {'User-Agent': f'{REQUEST_LABEL} - {USER_INFO}'}
TOOL_API_ENDPOINT = "https://toolhub.wikimedia.org/api/tools/"
TOOL_TEST_API_ENDPOINT = "https://toolhub-demo.wmcloud.org/api/tools/"

def get_tools():
  """ Getting data on all Toolhub tools """
  url = f'{TOOL_TEST_API_ENDPOINT}'
  response = requests.get(url, headers=headers)
  if response.status_code == 200:
    api_response = response.json()
    tools = api_response["results"]
    while api_response["next"]:
      api_response = requests.get(api_response["next"], headers=headers).json()
      tools.extend(api_response["results"])
    return tools

def get_single_tool(tool):
  """ Gets data on a single tool """
  url = f'{TOOL_TEST_API_ENDPOINT}{tool}'
  response = requests.get(url, headers=headers)
  if response.status_code == 200:
    api_response = response.json()
    return api_response