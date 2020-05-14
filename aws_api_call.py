###################
# Developer: Hardik Munjal
###################
# Package Imports
import io
import json
import os

import boto3
from PIL import Image, ImageDraw
from utilities.utility import IMG_PATH


# Variables Declarations


# Code
class AwsTextExtraction:
    def __init__(self, img, d_type="prod"):
        self.image = Image.open(IMG_PATH + img)
        img_format = self.image.format
        imgByteArr = io.BytesIO()
        self.image.save(imgByteArr, format=img_format)
        self.aws_object = boto3.client(aws_access_key_id='XXXXXXXXXXXX' #your aws key,
                                       aws_secret_access_key='XXXX', #your aws secret key
                                       service_name='textract',
                                       region_name='XXXX', #region of your aws account
                                       endpoint_url='https://textract.us-east-1.amazonaws.com')
        self.image_bytes = imgByteArr.getvalue()
        self.coord_dict = {}
        self.d_type = d_type
        self.blocks_detect, self.blocks_analyse = self.get_response()

    def get_response(self):
        if self.d_type == "dev":
            if not os.path.exists(IMG_PATH + 'analyse_dummy.json') or os.stat(
                    IMG_PATH + 'analyse_dummy.json').st_size == 0:
                response_a = self.aws_object.analyze_document(Document={'Bytes': self.image_bytes},
                                                              FeatureTypes=["TABLES", "FORMS"])
                with open(IMG_PATH + 'analyse_dummy.json', 'w', encoding='utf-8') as f:
                    json.dump(response_a, f, ensure_ascii=False, indent=4)
            else:
                with open(IMG_PATH + 'analyse_dummy.json') as json_file:
                    response_a = json.load(json_file)

            if not os.path.exists(IMG_PATH + 'detect_dummy.json') or os.stat(
                    IMG_PATH + 'detect_dummy.json').st_size == 0:
                response_d = self.aws_object.detect_document_text(Document={'Bytes': self.image_bytes})
                with open(IMG_PATH + 'detect_dummy.json', 'w', encoding='utf-8') as f:
                    json.dump(response_d, f, ensure_ascii=False, indent=4)
            else:
                with open(IMG_PATH + 'detect_dummy.json') as json_file:
                    response_d = json.load(json_file)
        else:
            response_d = self.aws_object.detect_document_text(Document={'Bytes': self.image_bytes})
            response_a = self.aws_object.analyze_document(Document={'Bytes': self.image_bytes},
                                                          FeatureTypes=["TABLES", "FORMS"])

        return response_d['Blocks'], response_a['Blocks']

    @staticmethod
    def show_bouding_box(draw, box, width, height, boxcolor):

        left = width * box['Left']
        top = height * box['Top']
        draw.rectangle([left, top, left + (width * box['Width']), top + (height * box['Height'])], outline=boxcolor)

    @staticmethod
    def show_selected_element(draw, box, width, height, boxcolor):

        left = width * box['Left']
        top = height * box['Top']
        draw.rectangle([left, top, left + (width * box['Width']), top + (height * box['Height'])], fill=boxcolor)

    # Displays information about a block returned by text detection and text analysis
    @staticmethod
    def display_block_information(block):
        print('Id: {}'.format(block['Id']))
        if 'Text' in block:
            print('    Detected: ' + block['Text'])
        print('    Type: ' + block['BlockType'])

        if 'Confidence' in block:
            print('    Confidence: ' + "{:.2f}".format(block['Confidence']) + "%")

        if block['BlockType'] == 'CELL':
            print("    Cell information")
            print("        Column:" + str(block['ColumnIndex']))
            print("        Row:" + str(block['RowIndex']))
            print("        Column Span:" + str(block['ColumnSpan']))
            print("        RowSpan:" + str(block['ColumnSpan']))

        if 'Relationships' in block:
            print('    Relationships: {}'.format(block['Relationships']))
        print('    Geometry: ')
        print('        Bounding Box: {}'.format(block['Geometry']['BoundingBox']))
        print('        Polygon: {}'.format(block['Geometry']['Polygon']))

        if block['BlockType'] == "KEY_VALUE_SET":
            print('    Entity Type: ' + block['EntityTypes'][0])

        if block['BlockType'] == 'SELECTION_ELEMENT':
            print('    Selection element detected: ', end='')

            if block['SelectionStatus'] == 'SELECTED':
                print('Selected')
            else:
                print('Not selected')

        if 'Page' in block:
            print('Page: ' + block['Page'])

    def detect_and_draw_text(self):
        width, height = self.image.size
        print('Detected Document Text')
        # Create image showing bounding box/polygon the detected lines/text
        img = self.image.copy()
        for block in self.blocks_detect:
            self.display_block_information(block)
            draw = ImageDraw.Draw(img)
            # Draw WORD - Green -  start of word, red - end of word
            if block['BlockType'] == "WORD":
                draw.line([(width * block['Geometry']['Polygon'][0]['X'],
                            height * block['Geometry']['Polygon'][0]['Y']),
                           (width * block['Geometry']['Polygon'][3]['X'],
                            height * block['Geometry']['Polygon'][3]['Y'])], fill='green',
                          width=2)

                draw.line([(width * block['Geometry']['Polygon'][1]['X'],
                            height * block['Geometry']['Polygon'][1]['Y']),
                           (width * block['Geometry']['Polygon'][2]['X'],
                            height * block['Geometry']['Polygon'][2]['Y'])],
                          fill='red',
                          width=2)

            # Draw box around entire LINE
            if block['BlockType'] == "LINE":
                points = []

                for polygon in block['Geometry']['Polygon']:
                    points.append((width * polygon['X'], height * polygon['Y']))

                draw.polygon(points, outline='black')

                # Uncomment to draw bounding box
                box = block['Geometry']['BoundingBox']
                left = width * box['Left']
                top = height * box['Top']
                draw.rectangle([left, top, left + (width * box['Width']), top + (height * box['Height'])],
                               outline='black')

        # Display the image
        img.show()
        print(self.coord_dict)
        # display image for 10 seconds
        return len(self.blocks_detect)

    def analyse_and_draw_text(self):
        width, height = self.image.size
        print('Detected Document Text')
        img_copy = self.image.copy()
        # Create image showing bounding box/polygon the detected lines/text
        for block in self.blocks_analyse:
            # Uncomment to display block information
            # self.display_block_information(block)
            draw = ImageDraw.Draw(img_copy)
            if block['BlockType'] == "KEY_VALUE_SET":
                if block['EntityTypes'][0] == "KEY":
                    self.show_bouding_box(draw, block['Geometry']['BoundingBox'], width, height, 'red')
                else:
                    self.show_bouding_box(draw, block['Geometry']['BoundingBox'], width, height, 'green')

            if block['BlockType'] == 'TABLE':
                self.show_bouding_box(draw, block['Geometry']['BoundingBox'], width, height, 'blue')

            if block['BlockType'] == 'CELL':
                self.show_bouding_box(draw, block['Geometry']['BoundingBox'], width, height, 'yellow')
            if block['BlockType'] == 'SELECTION_ELEMENT':
                if block['SelectionStatus'] == 'SELECTED':
                    self.show_selected_element(draw, block['Geometry']['BoundingBox'], width, height, 'blue')

                points = []
                for polygon in block['Geometry']['Polygon']:
                    points.append((width * polygon['X'], height * polygon['Y']))
                draw.polygon(points, outline='blue')

        # Display the image
        img_copy.show()
        return len(self.blocks_analyse)

    def get_raw_text(self):
        print("\nText\n========")
        text = ""
        for item in self.blocks_detect:
            if item["BlockType"] == "LINE":
                text = text + " " + item["Text"]
        return text

    def get_text_in_reading_order(self):
        # Detect columns and print lines
        columns = []
        lines = []
        for item in self.blocks_detect:
            if item["BlockType"] == "LINE":
                column_found = False
                for index, column in enumerate(columns):
                    bbox_left = item["Geometry"]["BoundingBox"]["Left"]
                    bbox_right = item["Geometry"]["BoundingBox"]["Left"] + item["Geometry"]["BoundingBox"]["Width"]
                    bbox_centre = item["Geometry"]["BoundingBox"]["Left"] + item["Geometry"]["BoundingBox"]["Width"] / 2
                    column_centre = column['left'] + column['right'] / 2

                    if (column['left'] < bbox_centre < column['right']) or (
                            bbox_left < column_centre < bbox_right):
                        # Bbox appears inside the column
                        lines.append([index, item["Text"]])
                        column_found = True
                        break
                if not column_found:
                    columns.append({'left': item["Geometry"]["BoundingBox"]["Left"],
                                    'right': item["Geometry"]["BoundingBox"]["Left"] + item["Geometry"]["BoundingBox"][
                                        "Width"]})
                    lines.append([len(columns) - 1, item["Text"]])

        lines.sort(key=lambda x: x[0])
        return lines
