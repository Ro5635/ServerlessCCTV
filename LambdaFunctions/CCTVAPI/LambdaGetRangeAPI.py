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

    if len(event['startHour']) == 2:
        
        startHour = event['startHour']
    
    elif  len(event['startHour']) == 1:

        # And this is why I prefer type safe languages...
        startHour = "0" +  event['startHour']

    else:
        
        return "No Hour Specified!"\


    # startMin = event['startMin']

    objectPrefix = bucketSourceFolder + "/" + event['startDate']  + "/img" + startHour
    
    print("getting prefix: " , objectPrefix)


    response = client.list_objects(
        Bucket='acsstest',
        EncodingType='url',
        MaxKeys=9999,
        Prefix=objectPrefix
    )
    
    #Does the searched location contain any objects?
    if 'Contents' in response.keys():
        
        # Get the keys for all of the objects in that folder
        Foundkeys = getObjectKeys(response["Contents"])
        




        # Get the keys signed
        urls = signKeys(client , Foundkeys)


    
    else:
        print("There are no objects avalible")








'''
        # Functions
'''



"""
checkTime

Checks that the passed time is within ranges, 

time : string: The time to check, expected in HHMM eg 0855 for 8:55 AM
returns : boolean : pass or fail check
"""
def checkTime(time):


    if !(len(time) == 4):

        # Check fails, time length should be 4 charactors
        print("Supplied Time Fails Validation, there should be exactly 4 charactors supplied.")
        return false

    elif !(0 <= time[02] <= 24) :

        # Check fails, hours are perculiar.
        print("Supplied Time Fails Validation, Hours are perculiar.")
        return false

    elif !(0 <= time[35] <= 60) 

        # Check fails, Minutes are perculiar.
        print("Supplied Time Fails Validation, Minutes are perculiar.")
        return false

    else:

        return true



"""
Filter keys to between to given times

startHHMM : string : The start time, in HHMM form eg 0515 for 5:15 AM
finishHHMM : string : The finish time, in the HHMM form. eg 1444 for 2:44 PM 
keys : list : keys that are to be filtered

returns : list : all of the keys passed that pass teh filter requirments

"""
def filterBetweenTimes(startHHMM , finishHHMM, keys):

    filteredKeys = []

    for key in keys:

        if  startHHMM[0:2] <= key[14:18] <= finishHHMM[2:4] :

            print("start: " , startHHMM[0:2])
            print("Finish: " , startHHMM[2:4])
            print("Key: " ,  key[14:18])

            filteredKeys.append(key)


    return filteredKeys



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


"""
Gets the signed URL for the given keys, returns as a lift of URLs in the same order as passed.

s3Client : The S3 client object from the boto3 lib
keys : S3 key
secondsActive : The number of seconds the signed link should remain active for (default 500)

"""
def signKeys(s3Client, keys, secondsActive = 500):

    urls = []

    for key in keys:

        # Get the URL signed
        Params = { 'Bucket': bucketName, 'Key': key }
            
        # Get the URL signed
        signedURL = s3Client.generate_presigned_url('get_object', Params, secondsActive)
            
        # Add the signed URL to the data structure
        urls.append(signedURL)

    return urls