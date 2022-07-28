# img-classify

This is an application that performs image classification using Tensorflow on HPC hardware.
It was demonstrated as part of a tutorial presented by TACC at the SCGI Gateways 2021 conference.
More information about the tutorial can be found
[here](https://github.com/TACC-Cloud/pearc22-portable-computing-cloud-hpc/releases/tag/gateways21-portable-computing-cloud-hpc)

## Details

The img-classify application is non-interactive. Once a job using this app has been submitted, the input files provided
in the job submission body are automatically staged and classification is performed.
The output can be found in the output directory specified in the application definition (*execSystemOutputDir*).

## Using the img-classify application

Use the _app_definition.json_ file as a reference for creating the img-classify application. Simply download the file
or copy its contents and [create the app](https://tapis.readthedocs.io/en/latest/technical/apps.html#creating-an-application).

Note that an application id must be unique, so in general it is a good idea to use a naming scheme likely to result
in a unique id. For example, it is common to include a username as part of the id.

To run the application on a specific system instead of a publicly shared one, users can add the *execSystemId*
attribute under the *jobAttributes* section in the app definition:

```
{
    ...,

    "containerImage": "docker://tapis/img-classify:0.1",
    "jobAttributes": {
        "execSystemId": <SYSTEM_NAME_HERE>,
        "execSystemExecDir": "${JobWorkingDir}/jobs/${JobUUID}",
        
        ...
}
```

If using the job definition template, be sure to replace the *execSystemId* with a specific system
(or remove it entirely), update *appId* with the Id of the application you created and change the "--account" in
*appArgs* to your specific account allocation.


## Handling input files

Underneath the *jobAttributes* field in the job definition, there is a subfield called *parameterSet*.
Within *parameterSet* is yet another subfield called *appArgs* where the user can pass in images to be classified
using two args: an "--image_file" flag and the image file path.

```
{
    ...,

    "parameterSet": {
        "appArgs": [
            {
                "arg": "--image_file"
            },
            {
                "arg": "'<IMAGE_FILE_PATH>"
            }
        ]
    
    ...
```
