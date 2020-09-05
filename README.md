# AWS Textract Implementation using Python

This repo implements Amazon Web Services (AWS) textract api to extraact raw text from documents. Read more about it [here](https://aws.amazon.com/textract/)

### ✍ About files

- [aws_api_call.py](https://github.com/hardy8059/aws_textract/blob/master/aws_api_call.py) - Implements the amazon web service API call as a class.
- [main.py](https://github.com/hardy8059/aws_textract/blob/master/main.py) - Calls the class from aws_api_call.py and calls the method to run the api.
- [utility.py](https://github.com/hardy8059/aws_textract/blob/master/utility.py) - Implements common methods like getting paths to different files and folders.

### 🔢 Steps to run the project:
- Create a **data** folder in the project root directoy.

- Add an image of the document you want to extract informations from, to data folder.

- Change the **aws credentials** in **aws_api_call.py** file
  > aws_access_key_id='XXXXXXXXXXXX' #your aws key
  > aws_secret_access_key='XXXX', #your aws secret key
  > region_name='XXXX', #region of your aws account

- Change name of the file in **main.py**.
  > aws = AwsTextExtraction("dummy.JPG", "dev") # Change your image name.

- Run **main.py**
  ```shell
    python main.py
  ```
