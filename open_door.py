from picamera import PiCamera
import time
import boto3
import random
import RPi.GPIO as GPIO
from time import sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
GPIO.output(18, 0) ### Close the LOCK

directory = '/home/ishika/groupproject-images' #folder name on your raspberry pi

P=PiCamera()
P.resolution= (800,600)
P.start_preview()
collectionId='groupproject-facialrecognition-doorlock' #collection name

rek_client=boto3.client('rekognition')
sns_client=boto3.client('sns')

if __name__ == "__main__":

        #camera warm-up time
        time.sleep(2)
        
        milli = int(round(time.time() * 1000))
        image = '{}/image_{}.jpg'.format(directory,milli)
        P.capture(image) #capture an image
        print('captured '+image)
        with open(image, 'rb') as image:
            try: #match the captured imges against the indexed faces
                match_response = rek_client.search_faces_by_image(CollectionId=collectionId, Image={'Bytes': image.read()}, MaxFaces=1, FaceMatchThreshold=85)
                if match_response['FaceMatches']:
                    print('Hello, ',match_response['FaceMatches'][0]['Face']['ExternalImageId'])
                    print('Similarity: ',match_response['FaceMatches'][0]['Similarity'])
                    print('Confidence: ',match_response['FaceMatches'][0]['Face']['Confidence'])
    
                else:
                    print('No faces matched')
            except:
                print('No face detected')
            finally:
                P.stop_preview()
                P.close() 
                print('Valid face detected!')
                number = random.randint(1000,9999)
                sns_client.publish(TopicArn='arn:aws:sns:ap-southeast-2:554402701917:groupproject-facialrecognition-doorlock', 
                                   Message='Your OTP is %s. Key in your OTP to open the Door.' % number, 
                                   Subject='Face Detection OTP')
                otp = input('OTP:')
                if (otp == number): # OTP Matches
                     GPIO.output(18, 1)
                     print('OTP Matches. Door now open!')
                     sleep(5)
                     GPIO.output(18, 0)
        time.sleep(1)

