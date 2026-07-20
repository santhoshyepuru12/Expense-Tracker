from django.db import models
from django.contrib.auth.models import User


class Expense(models.Model):
    CATEGORY_CHOICES = [
    ("Food", "Food"),
    ("Travel", "Travel"),
    ("Shopping", "Shopping"),
    ("Bills", "Bills"),
    ("Entertainment", "Entertainment"),
    ("Medical", "Medical"),
    ("Others", "Others"),
     ]
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=100)

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    category = models.CharField(
    max_length=50,
    choices=CATEGORY_CHOICES)

    date = models.DateField()

    description = models.TextField(blank=True)

    def __str__(self):
        return self.title
    
class Budget(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    month = models.DateField()

    def __str__(self):
        return f"{self.user.username} - {self.month}"