from __future__ import print_function

import json
import urllib
import boto3
import time


bucketName = "acsstest"

#Location of source folder in bucket, Don not include start and end slash.
bucketSourceFolder = "StoredCCTVCaptures"

# Use cloudfront to use a custom domain!
# example: "https://acss.webaddressgoeshere.com"
buacketAccessURL = "https://s3-eu-west-1.amazonaws.com/"

print('Loading function')


def lambda_handler(event, context):
               
    s3 = boto3.resource('s3')
    
    client = boto3.client('s3')
    bucket = s3.Bucket(bucketName)

    objectPrefix = bucketSourceFolder + "/" + getFolder()  + "/"
    


    response = client.list_objects(
        Bucket='acsstest',
        EncodingType='url',
        MaxKeys=9900,
        Prefix=objectPrefix
    )
    
    # if response["Contents"] is None:
        # print("hi null : ")
    # else:
        # print("go go go ")
        
    if not response["Contents"]:
        print("List is empty")    
        
    
    
    # if len(response["Contents") > 0:
    #     for s3Object in  response["Contents"]:
    #         print (s3Object["Key"])
  

    
    # for key, value in response['Contents'].iteritems():
    #   print (key, value)
    
    
    
"""
Returns the name of the folder that is required for the date?..
"""
def getFolder():
    
    # Get the folder for today
    todaysFolder = time.strftime("%Y/%m/%d")
    
    return todaysFolder
