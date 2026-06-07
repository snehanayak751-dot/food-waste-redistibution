from django.db import models
from django.contrib.auth.models import User

# ==========================================
# 1. FOOD ITEM MODEL
# ==========================================
class FoodItem(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Requested', 'Requested'),
        ('In Transit', 'In Transit'),
        ('Delivered', 'Delivered'),
    ]
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    quantity = models.CharField(max_length=100)
    donor_name = models.CharField(max_length=255, default="Restaurant")
    expiry_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')

    def __str__(self):
        return f"{self.name} ({self.status})"


# ==========================================
# 2. NGO PROFILE MODEL (With Custom Auto-ID Sequence)
# ==========================================
class NGO(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ngo_id = models.CharField(max_length=20, unique=True, editable=False)
   
    ngo_name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=15)

    def save(self, *args, **kwargs):
        if not self.ngo_id:
            # Query the database for the last added record to increment sequence
            last_ngo = NGO.objects.all().order_by('id').last()
            if last_ngo and last_ngo.ngo_id:
                try:
                    last_num = int(last_ngo.ngo_id.split('-')[1])
                    self.ngo_id = f"NGO-{last_num + 1}"
                except (ValueError, IndexError):
                    self.ngo_id = "NGO-1001"
            else:
                self.ngo_id = "NGO-1001"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ngo_name} ({self.ngo_id})"


# ==========================================
# 3. VOLUNTEER PROFILE MODEL (With Custom Auto-ID Sequence)
# ==========================================
class Volunteer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Automatically tracks unique platform alphanumeric IDs
    volunteer_id = models.CharField(max_length=20, unique=True, editable=False)
    phone = models.CharField(max_length=15)
    city = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        if not self.volunteer_id:
            # Query the database for the last added record to increment sequence
            last_vol = Volunteer.objects.all().order_by('id').last()
            if last_vol and last_vol.volunteer_id:
                try:
                    last_num = int(last_vol.volunteer_id.split('-')[1])
                    self.volunteer_id = f"VOL-{last_num + 1}"
                except (ValueError, IndexError):
                    self.volunteer_id = "VOL-1001"
            else:
                self.volunteer_id = "VOL-1001"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Volunteer {self.volunteer_id} - {self.user.username}"


# ==========================================
# 4. FOOD REQUEST TRANSACTION MODEL
# ==========================================
class FoodRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('claimed', 'Claimed'),
        ('delivered', 'Delivered'),
    ]
    food = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    ngo_name = models.CharField(max_length=200)
    address = models.TextField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Request for {self.food.name} by {self.ngo_name}"


# ==========================================
# 5. GENERIC BACKUP PROFILE MODEL
# ==========================================
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return self.user.username