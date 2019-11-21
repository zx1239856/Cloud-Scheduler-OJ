# Registry Management



## Overview

This is a section for private registry management. It allows users to:

1. Upload an image to an existing repository or a new repository
2. Check upload status from server to registry
3. Delete images from a repository
4. Display information of each images



## Information

### Left Column

This a a column of all the repositories in our private registry. It is ordered in alphabetical order.



### Main Table

This section is to display the images/tags of a repository. The content is changed based on the repository that you select.

Each row refers to an image, and the columns are some information of the image.



## Procedure

### Upload an image

#### First you need to prepare a docker-image.tar file, which you can generate using 

```bash
docker save -o docker-image.tar docker-image:tag
```

'docker' is the bash cli. Using docker save allows user to generate a '.tar' file from an existing docker image from the local machine.

#### Now let's upload our image. 

1. Click on the '+ New Image' button on the upper right corner
2. Attach the '.tar' file, and fill in the repository name.
3. Click upload and wait for the 'upload successful' message.
4. If you received 'upload successful', then it means your image is successfully uploaded to our server.
5. Now we can check the uploading progress of our image pushing into the private registry from our server from 'Upload Status'.
6. The process indicator in Upload Status is 'cached' -> 'uploading' -> 'success' / 'failed'.
7. If you saw 'success' indicator, then it means you have successfully uploaded the image and you should see your image in the repository that you assigned to.



### Delete an image

Delete an image is fairly simple, you just need to click on the delete button of the image that you want to delete and click confirm.