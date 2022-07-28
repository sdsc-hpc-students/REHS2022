# Details

This folder contains all files needed to build docker images that can be used to run the img-classify application
using docker or singularity.

There are two files for building docker images. One for running the application using docker and one for running the
application using singularity.

## Prerequisites

In order to run most of the commands discussed below, you will need to be on a host that has docker installed and
configured. To test this you can run the following commands:

```
docker --version
docker images
```

In order to test the image built for singularity, you will need to be on a host that has singularity installed and
configured. To test this you can run the following commands:

```
singularity --version
singularity cache list
```

## Creating docker images

To build the image for local testing using docker, download this folder and navigate to it on the command line,
then run commands similar to the following:

```
docker build -f Dockerfile -t my-img-classify:0.1 .
docker build -f Dockerfile_singularity -t my-img-classify-sing:0.1 .
```

## Dockerfiles

The images are built upon TensorFlow's official _tensorflow_ image, which is itself based on Ubuntu Linux version 18.04.

## classify_img.py

The image to be processed is passed in through the command line using the _--image_file_ argument.
In order to test the application using the docker image, run a command similar to the following:

```docker run <NAME_OF_IMAGE> --image_file=<PATH_TO_IMAGE_FILE>```

For example:

```
docker run --rm my-img-classify:0.1 --image_file=https://s3.amazonaws.com/cdn-origin-etr.akc.org/wp-content/uploads/2017/11/12231410/Labrador-Retriever-On-White-01.jpg
```
 
This will cause the app to perform image classification on the JPEG found in the S3 bucket at the given URL.
The JPEG contains an image of a Labrador Retriever. If the app runs successfully, the following output should be produced:

 ```
Successfully downloaded inception-2015-12-05.tgz 88931400 bytes.
Labrador retriever (score = 0.97471)
golden retriever (score = 0.00324)
kuvasz (score = 0.00099)
bull mastiff (score = 0.00095)
Saint Bernard, St Bernard (score = 0.00067)
 ```

Note that you should also be able to use docker to test the image created using the file Dockerfile_singularity.

In order to test the image built for singularity, you will need to be on a host that has singularity installed and
configured. To test you can run a command similar to the following:

```
singularity run docker://my-img-classify-sing:0.1 --image_file=https://s3.amazonaws.com/cdn-origin-etr.akc.org/wp-content/uploads/2017/11/12231410/Labrador-Retriever-On-White-01.jpg
```

Note that singularity will create a sif file from the docker image the first time this command is run.
This may take a significant amount of time.