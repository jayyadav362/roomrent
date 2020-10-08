from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class State(models.Model):
    name = models.CharField(max_length=100,unique=True)
    slug = models.SlugField()

    def __str__(self):
        return self.name

    def save(self,*args,**kwargs):
        self.slug = slugify(self.name)
        super(State, self).save(*args,**kwargs)

class City(models.Model):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State,on_delete=models.CASCADE)
    slug = models.SlugField()

    def __str__(self):
        return self.name

    def save(self,*args,**kwargs):
        self.slug = slugify(self.name)
        super(City, self).save(*args,**kwargs)

class RoomOwner(models.Model):
    ro_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User,on_delete=models.CASCADE)
    ro_image = models.ImageField(upload_to="profile")
    ro_contact = models.CharField(max_length=10,unique=True)
    ro_street = models.TextField(max_length=300)
    ro_id_proof = models.ImageField(upload_to="profile/proof")
    ro_house = models.CharField(max_length=100)
    ro_house_image = models.ImageField(upload_to="image")
    state = models.ForeignKey(State,on_delete=models.CASCADE)
    city = models.ForeignKey(City,on_delete=models.CASCADE)

    def __str__(self):
        return self.user_id.first_name

class RoomType(models.Model):
    rt_id = models.AutoField(primary_key=True)
    rt_title = models.CharField(max_length=200)
    slug = models.SlugField()

    def __str__(self):
        return self.rt_title

    def save(self,*args,**kwargs):
        self.slug = slugify(self.rt_title)
        super(RoomType, self).save(*args,**kwargs)


class Room(models.Model):
    r_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User,on_delete=models.CASCADE)
    r_title = models.CharField(max_length=200)
    r_rent = models.CharField(max_length=100)
    r_type = models.ForeignKey(RoomType,on_delete=models.DO_NOTHING)
    r_desc = models.TextField(max_length=300)
    r_image = models.ImageField(upload_to="image")
    slug = models.SlugField()
    r_status = models.CharField(max_length=20, default='1',choices=(("0", "Pending"), ("1", "Active")))
    r_doc = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.r_title

    def save(self,*args,**kwargs):
        self.slug = slugify(self.r_title)
        super(Room, self).save(*args,**kwargs)

class RoomRenter(models.Model):
    rr_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User,on_delete=models.CASCADE)
    rr_contact = models.CharField(max_length=10,unique=True)
    rr_image = models.ImageField(upload_to="profile")
    rr_street = models.TextField(max_length=300)
    state = models.ForeignKey(State,on_delete=models.DO_NOTHING)
    city = models.ForeignKey(City,on_delete=models.DO_NOTHING)
    rr_id_proof = models.ImageField(upload_to="profile/proof")

    def __str__(self):
        return self.user_id.first_name

class PaymentGenerate(models.Model):
    pg_id = models.AutoField(primary_key=True)
    pg_txn = models.CharField(max_length=100)
    user_id = models.ForeignKey(User,on_delete=models.DO_NOTHING)
    pg_amount = models.CharField(max_length=100)
    pg_month = models.CharField(max_length=100)
    pg_room_id = models.ForeignKey(Room,on_delete=models.DO_NOTHING)
    pg_doc = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField()

    def __str__(self):
        return self.pg_txn

    def save(self,*args,**kwargs):
        self.slug = slugify(self.pg_txn)
        super(PaymentGenerate, self).save(*args,**kwargs)

class PaymentPaid(models.Model):
    pp_id = models.AutoField(primary_key=True)
    pp_txn = models.CharField(max_length=100)
    user_id = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    pp_amount = models.CharField(max_length=100)
    pp_month = models.CharField(max_length=100)
    pp_room_id = models.ForeignKey(Room, on_delete=models.DO_NOTHING)
    pp_doc = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField()

    def __str__(self):
        return self.pp_txn

    def save(self, *args, **kwargs):
        self.slug = slugify(self.pp_txn)
        super(PaymentPaid, self).save(*args, **kwargs)

class RoomAllot(models.Model):
    ra_id = models.AutoField(primary_key=True)
    ra_room_id = models.ForeignKey(Room, on_delete=models.DO_NOTHING)
    user_id = models.ForeignKey(User, on_delete=models.DO_NOTHING,related_name='user_id')
    renter = models.ForeignKey(User, on_delete=models.DO_NOTHING,related_name='renter')
    ra_doc = models.DateTimeField(auto_now_add=True)
    ra_status = models.CharField(max_length=20, default='1',choices=(("0", "Request"), ("1", "Active"),("2","Pending")))
    slug = models.SlugField()

    def __str__(self):
        return self.ra_room_id.r_title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.ra_room_id.r_title)
        super(RoomAllot, self).save(*args, **kwargs)

