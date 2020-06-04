from django.db import models
from django.urls import reverse            
import uuid                                 
from django.contrib.auth.models import User
from datetime import date, datetime
from django.utils import timezone

from PIL import Image


class Genre(models.Model):
    name = models.CharField(max_length=100) 
    
    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Language(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name



class Book(models.Model):
    book_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, related_name='my_book', on_delete=models.CASCADE, null=True, blank=True)
    owner_nonuser = models.CharField(max_length=200, verbose_name='Nem-felhasználó', help_text="Valaki, aki nem regisztrált felhasználó az oldalon vagy még nem a barátod.", null=True, blank=True)
    last_name_author = models.CharField(verbose_name='Szerző vezetékneve', max_length=100)
    first_name_author = models.CharField(verbose_name='Szerző keresztneve', max_length=100)
    title = models.CharField(verbose_name='Cím', max_length=200)
    genre = models.ForeignKey(Genre, verbose_name='Műfaj', on_delete=models.SET_NULL, null=True, default='2')  
    language = models.ForeignKey(Language, verbose_name='Nyelv', on_delete=models.SET_NULL, null=True, default='11')
    recommended = models.BooleanField(verbose_name='Ajánlom másoknak', default=False, help_text='Van ilyen könyved, és szívesen kölcsönadnád barátaidnak.')
    wished = models.BooleanField(verbose_name='Kívánságlistámra teszem', default=False, help_text='Neked nincs meg, de szívesen elolvasnád.')
    loaned = models.BooleanField(verbose_name='Kölcsönadtam', default=False, help_text='Csak ajánlott könyvet tudsz kölcsönadni. (Miután visszakaptad, csak "pipáld vissza" és mentsd el, az adatok törlődni fognak.)')
    borrower = models.ForeignKey(User, related_name='borrowed_book', verbose_name='Neki (felhasználó)', on_delete=models.SET_NULL, null=True, blank=True)
    borrower_nonuser = models.CharField(max_length=200, verbose_name='Neki (nem-felhasználó)', help_text="Valaki, aki nem regisztrált felhasználó az oldalon vagy még nem a barátod.", null=True, blank=True)
    loan_date = models.DateField(verbose_name='Ezen a napon', blank=True, null=True)
    comment = models.TextField(max_length=300, verbose_name='Komment', blank=True, help_text='Ajánlott/kölcsönadott és kívánságlistádon szereplő könyveid esetében a barátaid ezt látják.')

    class Meta:
        ordering = ['last_name_author', 'first_name_author', 'title']


    def __str__(self):
        return f'{self.last_name_author}, {self.first_name_author}: {self.title}'

  
    def get_absolute_url(self):
        return reverse('book-detail', args=[str(self.book_id)])
    



class FriendRequest(models.Model):
    user = models.ForeignKey(User, related_name='request_user', on_delete=models.CASCADE)
    requested_friend = models.ForeignKey(User, related_name='requested_friend', on_delete=models.CASCADE)
    request_datetime = models.DateTimeField(default = timezone.now)
    confirmed_request = models.BooleanField(default=False)

    class Meta:
        ordering = ["request_datetime"]

    def __str__(self):
        return f'{self.user} sent a friend request to {self.requested_friend}'



class RejectedFriendship(models.Model):
    rejecter = models.ForeignKey(User, related_name='rejecter', on_delete=models.CASCADE)
    rejected = models.ForeignKey(User, related_name='rejected', on_delete=models.CASCADE)
    rejection_datetime = models.DateTimeField(default = timezone.now)
    notif_deleted = models.BooleanField(default=False)


    def __str__(self):  
        return f'{self.rejecter} has rejected {self.rejected}'



class Friendship(models.Model):
    confirmed_user = models.ForeignKey(User, related_name='confirmed_user', on_delete=models.CASCADE) 
    requested_user = models.ForeignKey(User, related_name='requested_user', on_delete=models.CASCADE)
    confirmation_datetime = models.DateTimeField(default = timezone.now)

    def __str__(self):  
        return f'{self.confirmed_user} - {self.requested_user} friendship'



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics') # it should be deleted in case the user deletes himself

    def __str__(self):
        return f'{self.user.username}\'s profile'
    
    def save(self, *args, **kwargs):
        super().save( *args, **kwargs)
        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)


