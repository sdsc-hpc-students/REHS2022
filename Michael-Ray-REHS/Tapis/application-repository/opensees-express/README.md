# opensees-express

This is a sequential version of the [OpenSees](https://opensees.berkeley.edu/) application, rather than a parallelized one. See the [OpenSees documentation](https://opensees.berkeley.edu/wiki/index.php/OpenSees_User) for more information. 
<br><br>


## Details

The opensees-express app is non-interactive. Once a job using this app has been submitted, the input files provided in the app definition (TCL, raw data, etc.) are staged and the main TCL file is executed. The resulting output can be found in the output directory specified in the app definition ("execSystemOutputDir"). 
<br><br>


## Using the opensees-express app

Use the _app_definition.json_ file as a reference for creating the opensees-express app. Simply download the file or copy its contents and [create the app](https://tapis.readthedocs.io/en/latest/technical/apps.html#creating-an-application).

To run the app on a specified system instead of a publicly shared one, users can add an "execSystemId" key-value pair under the "jobAttributes" field in the app definition:

```
{
    ...
    "containerImage": "stevemock/docker-opensees:latest",
    "jobAttributes": {
        "execSystemId": <SYSTEM_NAME_HERE>
        "execSystemExecDir": "${JobWorkingDir}/jobs/${JobUUID}",
        ...
}
``` 
<br>

If using a job definition template, be sure to replace the "<SYSTEM_NAME_HERE>" and "<XXX_FILE>" values with a specific system and file paths as appropriate!
<br><br> 


## Handling input files

Underneath "jobAttributes" in the app definition, there are two important fields: "parameterSet" and "fileInputs".

The opensees-express app requires that **at least one** input TCL file. In the reference app definition, a TCL file is provided by the user and passed to the job as "input.tcl" (note that the tapis://<SYSTEM_NAME>/ prefix indicates the file exists on a Tapis system). 

If the user has multiple files to pass in, this can be done in the job submission request, as seen below. There are a few points regarding file inputs passed in through the job submission request:
* The main input file *must* follow the same syntax as that provided in the app definition.
* If a job submission request contains a main file different from that provided in the app definition, it will override the app definition file.
* Any additional files added in the job submission request do not have to exist in the app definition already.

```
{
    ...,

    "fileInputs": [
        {
            "sourceUrl": "tapis://<SYSTEM_NAME>/main_tcl_file.tcl",
            "targetPath": "input.tcl",
            "inPlace": false,
            "meta": {
                "name": "TCL_input",
                "required": true
            }
        },
        {
            "sourceUrl": "tapis://<SYSTEM_NAME>/extra_file_1.tcl",
            "targetPath": "extra_file_1.tcl"
        },
        {
            "sourceUrl": "tapis://<SYSTEM_NAME>/extra_file_2.tcl",
            "targetPath": "extra_file_2.tcl"
        },

        ...
    ]
}
```
<br>

Read the [Tapis jobs documentation](https://tapis.readthedocs.io/en/latest/technical/jobs.html#fileinputs) for more information on file inputs.