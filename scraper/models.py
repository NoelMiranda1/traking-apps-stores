from django.db import models

# Create your models here.

class AppToMonitor(models.Model):
    STORE_CHOICES = [
        ('google_play', 'Google Play'),
        ('app_store', 'App Store'),
    ]
    
    app_id = models.CharField(max_length=255)
    store = models.CharField(max_length=20, choices=STORE_CHOICES)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['app_id', 'store']
    
    def __str__(self):
        return f"{self.app_id} ({self.store})"

class AppInfo(models.Model):
    STORE_CHOICES = [
        ('google_play', 'Google Play'),
        ('app_store', 'App Store'),
    ]
    
    app_id = models.CharField(max_length=255)
    store = models.CharField(max_length=20, choices=STORE_CHOICES)
    version = models.CharField(max_length=50)
    app_name = models.CharField(max_length=255)
    last_updated = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.app_name} ({self.store})"
