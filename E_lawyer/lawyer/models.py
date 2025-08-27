from django.db import models
from E_lawyer.client.models import *

# Create your models here.

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(ClientDetails, on_delete=models.CASCADE)  # Linked to Client
    lawyer = models.ForeignKey(LawyerDetails, on_delete=models.CASCADE)  # Linked to Lawyer

    def __str__(self):
        return f"{self.sender.username}: {self.message[:50]}"
    
class VideoCallRoom(models.Model):
    lawyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lawyer')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client', null=True, blank=True)
    room_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=[('waiting', 'Waiting'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='waiting')
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Room {self.room_id} between {self.lawyer} and {self.client}"