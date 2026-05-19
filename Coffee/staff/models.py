from django.db import models

class User(models.Model):
    # Django handles the primary key (id) automatically, 
    # but you can define user_id explicitly to match your SQL.
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Users'

class Account(models.Model):
    account_id = models.AutoField(primary_key=True)
    
    # OneToOneField enforces the 'UNIQUE' constraint from your SQL
    # on_delete=models.CASCADE matches your 'ON DELETE CASCADE'
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='account'
    )
    
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=50)

    class Meta:
        db_table = 'Accounts'