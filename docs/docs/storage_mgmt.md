# Storage Management

A storage unit is a PVC (persistent volume claim). When a PVC is created, files can be uploaded into this storage space, and you can choose which PVC to be mounted to a new task in the **Task Settings -> Detail** page.

In the storage list page, you can:

+ Create and delete a storage unit
  + Please use '-' as a seperator for storage name, and format such as 1Ti/1Gi/100Mi/...  for storage capacity
  + A storage unit which is being used cannot be deleted
+ Upload files into a certain storage unit
  + Multiple files can be selected at one time
  + File names should not contain whitespace
  + Path is where you place your files under the mounted path, which can start as ./
+ Check uploading status and informations in **Upload Log**
  + 5 Status: Caching, Cached, Uploading, Succeeded, Failed
  + Click status for more detailed error information
  + Re-upload files. Note: Only for **Cached** files when the server is restarted. **Do not** use it when the normal uploading has not finished or crashed.
+ View and Edit files inside the storage unit by clicking **Editor**
  +  It will take some time to load
  + Only text and code files can be previewed and edited. Images can be viewed only.