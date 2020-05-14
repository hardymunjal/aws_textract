###################
# Developer: Hardik Munjal
###################
# Package Imports
from aws_api_call import AwsTextExtraction

# Code

if __name__ == '__main__':
    aws = AwsTextExtraction("dummy.JPG", "dev") # Change your image name.

    # Line wise result

    ret = aws.get_text_in_reading_order()
    for line in ret:
        print(line)

    # Raw result

    ret = aws.get_raw_text()
    print(ret)

    # Label Image

    _ = aws.detect_and_draw_text()

    # Key Value Pair in image

    _ = aws.analyse_and_draw_text()
