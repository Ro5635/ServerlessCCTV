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


    searchDate = event['searchDate']
    startTime  = event['startTime']
    finishTime = event['finishTime']

    if checkTime(startTime) and checkTime(finishTime) and checkDate(searchDate):

        objectPrefix = bucketSourceFolder + "/" + searchDate[0:4] + "/" + searchDate[4:6] + "/" + searchDate[6:8] + "/img"
    
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
            

            filteredKeys = filterBetweenTimes(startTime , finishTime, Foundkeys)



            # Get the keys signed
            urls = signKeys(client , filteredKeys)

            return urls

        
        else:
            print("There are no objects avalible")
            return(0)


    else:

        print("Quitting, Check Failed")






'''
        # Functions
'''


"""
checkDate

Validates the passed date, that date should be in the format YYYYMMDD
"""
def checkDate(date):

    if len(date) != 8:

        # Supplied date fails validation
        print("Supplied Date Fails Validation, 10 charactor date expected.")
        return False

    elif not (date.isdigit()):
        
        # Supplied date fails validation
        print("Supplied Date Fails Validation, only numbers should form the date.")
        return False
    
    else:

        # validation passed; return true
        
        return True




"""
checkTime

Checks that the passed time is within ranges, 

time : string: The time to check, expected in HHMM eg 0855 for 8:55 AM
returns : boolean : pass or fail check
"""
def checkTime(time):

    print("time check: ", int(time[2:4]) - 1 )
    if len(time) != 4:

        # Check fails, time length should be 4 charactors
        print("Supplied Time Fails Validation, there should be exactly 4 charactors supplied.")
        return False

    elif not (0 <= int(time[0:2]) <= 24 or int(time[0:2]) == "00") :

        # Check fails, hours are perculiar.
        print("Supplied Time Fails Validation, Hours are perculiar.")
        return False

    elif not (0 <= int(time[2:4]) <= 60 or int(time[2:4]) == "00") :

        # Check fails, Minutes are perculiar.
        print("Supplied Time Fails Validation, Minutes are perculiar.")
        return False

    else:

        return True



"""
Filter keys to between to given times

startHHMM : string : The start time, in HHMM form eg 0515 for 5:15 AM
finishHHMM : string : The finish time, in the HHMM form. eg 1444 for 2:44 PM 
keys : list : keys that are to be filtered

returns : list : all of the keys passed that pass teh filter requirments

"""
def filterBetweenTimes(startHHMM , finishHHMM, keys):

    filteredKeys = []

    # Debug; log the variables used:
    print("start: " , startHHMM[0:2])
    print("Finish: " , startHHMM[2:4])
    # print("Key: " ,  key[14:18])

    # Go through each key and see if it matches the time range
    for key in keys:
        
        # Get the time stamp from teh key:
        splitKey = key.split('/')
        timeStamp = splitKey[ ( len(splitKey) - 1 ) ]
        timeStamp = timeStamp[  ( len(timeStamp) - 8 )  : ( len(timeStamp) - 4) ]

        # Filter by the hours
        if  startHHMM[0:2] <= timeStamp[0:2] <= finishHHMM[0:2] :

            # if its either the start or end hours check the minute
            if timeStamp[0:2] == startHHMM[0:2] or timeStamp[0:2] == finishHHMM[0:2] :

                if startHHMM[2:4] <= timeStamp[2:4] and timeStamp[2:4]  <= finishHHMM[2:4] :

                    # Minutes within range, add to the filteredkeys list.
                    print("Appending Key after check min")
                    filteredKeys.append(key)

            else:
                print("Appending Key after check Hour only: " + key)
                filteredKeys.append(key)

        else:
            # print("Key not applicable: " + key)
            syntax = 7 + 2
    return filteredKeys



"""
Get all of the keys from a given response Contents list, this is the response
returned by the boto3.client object.
"""
def getObjectKeys(responseContents):
    
    keys = []
    
    for s3Object in responseContents:
        # print (s3Object["Key"])
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