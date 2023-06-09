import os

import paramiko
import tiktoken

from langchain.tools import BaseTool


class ExecuteCommand(BaseTool):
    name = "Execute Command"
    description = "Use this tool to execute a command via SSH and get the output. Command must be non-interactive and cant run forever. Send the command you want to execute as the query."

    def ssh_execute(self, ip, username, keyfile, command, timeout=10):
      client = paramiko.SSHClient()
      client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

      try:
          key = paramiko.RSAKey.from_private_key_file(keyfile)
      except IOError as e:
          return f"Error: Unable to load private key file: {str(e)}"

      try:
          client.connect(ip, username=username,
                        pkey=key, timeout=timeout)

          stdin, stdout, stderr = client.exec_command(command, timeout=timeout)

          output = stdout.read().decode('utf-8')
          error = stderr.read().decode('utf-8')

          result = output + error

          enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
          if len(enc.encode(result)) > 3000:
              result = "The command output is too long. Please rewrite the command with shorter ouput. Just send the new command."

          #if result == "":
          stdin, stdout, stderr = client.exec_command("echo $?")
          exit_code = int(stdout.read().decode('utf-8'))
          if exit_code != 0:
            result += f"\nCommand exited with error code {exit_code}"
          else:
            result += "\nCommand finished successfully"

      except TimeoutError as ex:
          #print(type(ex).__name__)
          result = "Timeout. Probably command needed interactive input, please rewrite the command to be non-interactive. Just send the new command."
      except Exception as ex:
          result = "Unknown error. " + str(ex)
      finally:
          client.close()

      return result

    def _run(self, query: str) -> str:
        return self.ssh_execute(os.environ["TARGET_SERVER"], os.environ["TARGET_USER"], os.environ["SSH_KEY"], query, int(os.environ["SSH_TIMEOUT"]))

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("ExecuteCommand does not support async")




class ConnectCommand(BaseTool):
    name = "Connect Command"
    description = "Use this tool when a user specifies a new server to connect to. Send the server IP as the query."


    def _run(self, query: str) -> str:
        os.environ["TARGET_SERVER"] = query
        os.environ["TARGET_USER"] = "root"
        return "Successfully connected to the server. This is the server that will be managed from now on."

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("ExecuteCommand does not support async")