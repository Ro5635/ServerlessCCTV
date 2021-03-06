"""
Gets the most 5 recent images, returns the signed acces keys with a lifetime of 500 seconds.

    TO DO:

        - Actualy get the most recent!
        - Handle getting from previus day if neccasary...




author: Robert Curran robert@robertcurran.co.uk
date: 2/11/16


"""
from __future__ import print_function

import json
import urllib
import boto3
import time


bucketName = "acsstest"

#AWS data centre name; example eu-west-1.
dataCentre = "eu-west-1"

#Location of source folder in bucket, Do not include start and end slash.
bucketSourceFolder = "StoredCCTVCaptures"

# Use cloudfront to use a custom domain!
# example: "https://acss.webaddressgoeshere.com"
buacketAccessURL = "https://s3-eu-west-1.amazonaws.com/" + bucketName + "/"


def lambda_handler(event, context):
               
    s3 = boto3.resource('s3')
    
    client = boto3.client('s3')
    bucket = s3.Bucket(bucketName)

    objectPrefix = bucketSourceFolder + "/" + getFolder()  + "/img"
    
    print("getting prefix: " , objectPrefix)


    response = client.list_objects(
        Bucket='acsstest',
        EncodingType='url',
        MaxKeys=5,
        Prefix=objectPrefix
    )
    
    #Does the searched location contain any objects?
    if 'Contents' in response.keys():
        
        # Get the keys for all of the objects in that folder
        Foundkeys = getObjectKeys(response["Contents"])
        
        urls = []
        
        for key in Foundkeys:
            
            #Build the URL
            url = buacketAccessURL + key
            
            # Get the URL signed
            Params = { 'Bucket': bucketName, 'Key': key }
            
            signedURL = client.generate_presigned_url('get_object', Params, ExpiresIn = 500)
            
            #Add the signed URL to the data structure
            urls.append(signedURL)
        
        return urls
    
    
    else:
        print("There are no objects avalible")

    
"""
Get all of the keys from a given response Contents list, this is the response
returned by the boto3.client object.
"""
def getObjectKeys(responseContents):
    
    keys = []
    
    for s3Object in responseContents:
        print (s3Object["Key"])
        keys.append(s3Object["Key"])
    
    return keys
    
"""
Returns the name of the folder that is required for the date?..
"""
def getFolder():
    
    # Get the folder for today
    todaysFolder = time.strftime("%Y/%m/%d")

    return todaysFolder
