from django.db import models
from twilio.rest import Client
import os

# Create your models here.

class TwilioNotif(models.Model):
    test_result = models.PositiveIntegerField()

    def __str__(self):
        return str(self.test_result)
    
    def save(self, *args, **kwargs):
        if self.test_result < 80:
            # Retrieve Twilio credentials from environment variables
            account_sid = os.getenv("TWILIO_ACCOUNT_SID")
            auth_token = os.getenv("TWILIO_AUTH_TOKEN")
            phone_number = os.getenv("TWILIO_PHONE_NUMBER")
            
            # Create Twilio client with retrieved credentials
            client = Client(account_sid, auth_token)

            # Send message using Twilio client
            message = client.messages.create(
                body=f'Hi, your test result is {self.test_result}. Great job',
                from_=phone_number,  # Use retrieved phone number
                to='+918355921551'  # Update recipient number as needed
            )

            print(message.sid)
        
        return super().save(*args, **kwargs)