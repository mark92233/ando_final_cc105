from django.db import models

# Create your models here.

class PredictionInput(models.Model):
    target_date = models.DateField()
    store_location = models.CharField(max_length=255)
    shift = models.CharField(max_length=50)
    prev_cups = models.FloatField(default=0.0)
    prev_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'prediction_input'
