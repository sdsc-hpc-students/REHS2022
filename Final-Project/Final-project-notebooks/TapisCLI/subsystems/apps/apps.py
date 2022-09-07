from tapipy import tapis
import sys
import argparse

sys.path.insert(1, r'C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\Neo4j\TapisCLI\subsystems\tapis-object.py')
from tapisobject import tapisObject


class Apps(tapisObject):
    def __init__(self, tapis_object, username, password):
        super().__init__(tapis_object, username, password, r'C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\Neo4j\TapisCLI\subsystems\apps\apps.json')

    def create_app(self, kwargs: dict, args: list): # create a tapis app taking a json descriptor file path
        try:
            with open(kwargs['F'], 'r') as f:
                app_def = json.loads(f.read())
            url = self.t.apps.createAppVersion(**app_def)
            return f"App created successfully\nID: {app_def['id']}\nVersion: {app_def['version']}\nURL: {url}"
        except Exception as e:
            return e

    def get_app(self, kwargs: dict, args: list): # returns app information with an id and version as arguments
        try:
            app = self.t.apps.getApp(appId=args[0], appVersion=kwargs['v'])
            return app
        except Exception as e:
            return e

    def run_job(self, kwargs: dict, args: list): # run a job using an app. Takes a job descriptor json file path
        try:
            with open(kwargs['F'], 'r') as f:
                app_args = json.loads(f.read())

            job = {
                "name": kwargs['n'],
                "appId": args[0], 
                "appVersion": kwargs['v'],
                "parameterSet": {"appArgs": [app_args]        
                                }
            }
            job = self.t.jobs.submitJob(**job)
            return job.uuid
        except Exception as e:
            return e

    def get_job_status(self, kwargs: dict, args: list): # return a job status with its Uuid
        try:
            job_status = self.t.jobs.getJobStatus(jobUuid=args[0])
            return job_status
        except Exception as e:
            return e

    def download_job_output(self, kwargs: dict, args: list): # download the output of a job with its Uuid
        try:
            jobs_output = self.t.jobs.getJobOutputDownload(jobUuid=args[0], outputPath='tapisjob.out')
            with open(kwargs['of'], 'w') as f:
                f.write(jobs_output)
            return f"Successfully downloaded job output to {kwargs['of']}"
        except Exception as e:
            return e

    def jobs_cli(self, kwargs: dict, args: list): # function to manage all jobs
        try:
            if kwargs['r'] == 'create_app':
                return self.create_app(kwargs, args)
            elif kwargs['r'] == 'get_app_info':
                return self.get_app(kwargs, args)
            elif kwargs['r'] == 'run_app':
                return self.run_job(kwargs, args)
            elif kwargs['r'] == 'get_app_status':
                return self.get_job_status(kwargs, args)
            elif kwargs['r'] == 'download_app_results':
                return self.download_job_output(kwargs, args)
            else:
                return 'Command not recognized'
        except IndexError:
            return "must specify subcommand. See 'help'"
        except Exception as e:
            return e