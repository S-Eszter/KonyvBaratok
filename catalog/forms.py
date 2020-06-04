import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from django.forms import ModelForm, ModelChoiceField
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from catalog.models import FriendRequest, Friendship, Book, Profile

from django.db.models import Q


class UserModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        if (obj.last_name and obj.first_name):
            return f'{obj.username} ({obj.last_name} {obj.first_name})'
        else:
            return obj.username        



class FriendRequestForm(ModelForm):
    
    class Meta:
        model = FriendRequest
        fields = ('requested_friend',)
        field_classes = {
            'requested_friend': UserModelChoiceField
        }
        labels = {'requested_friend': _('Lehetséges barátok')}


    def __init__(self, user, *args, **kwargs):
        super(FriendRequestForm, self).__init__(*args, **kwargs)
        self.fields['requested_friend'].queryset = User.objects.exclude(username=user).exclude(requested_friend__user=user).exclude(request_user__requested_friend=user).order_by('username')
        self.fields['requested_friend'].empty_label = 'Válassz barátot'
        



class DateInput(forms.DateInput):
    input_type = 'date'
    
    

class BookCreateForm(ModelForm):

    class Meta:
        model = Book
        fields = ('last_name_author', 'first_name_author', 'title', 'genre','language', 'wished', 'recommended', 'loaned', 'borrower', 'borrower_nonuser', 'loan_date', 'comment',)
        field_classes = {
            'borrower': UserModelChoiceField
        }
        widgets = {'loan_date' : DateInput(format='%Y-%m-%d')}

    
    def __init__(self, user, *args, **kwargs):
        super(BookCreateForm, self).__init__(*args, **kwargs)
        self.fields['borrower'].queryset = User.objects.exclude(username=user).filter(Q(confirmed_user__requested_user=user) | Q(requested_user__confirmed_user=user)).distinct().order_by('username')
        self.fields['borrower'].empty_label = 'Válassz a barátaid közül'
       

    def clean(self):
        cleaned_data = super().clean()
        recom = cleaned_data.get('recommended')
        wished = cleaned_data.get('wished')
        loaned = cleaned_data.get('loaned')
        borrower = cleaned_data.get('borrower')
        borrower_nonuser = cleaned_data.get('borrower_nonuser')
        loan_date = cleaned_data.get('loan_date')

        # main.js takes care of some of these things, hopefully...
        if wished == True:
            if recom == True:
                raise forms.ValidationError("Nem lehet egyszerre ajánlani és kívánságlistára tenni ugyanazt a könyvet.") 
            elif loaned == True:
                raise forms.ValidationError("Kívánságlistán szereplő könyvet nem lehet kölcsönadni.")

        if loaned == True:
            if borrower == None and borrower_nonuser == None:
                raise forms.ValidationError("Meg kell adnod, hogy kinek adtad kölcsön.")
            elif loan_date == None:
                raise forms.ValidationError("Meg kell adnod, hogy mikor adtad kölcsön.")
            elif recom == False:
                raise forms.ValidationError("Csak ajánlott könyvet lehet kölcsönadni.")
        
        if loaned == False:
            if borrower != None or borrower_nonuser != None or loan_date != None:
                raise forms.ValidationError('Ha nincs kölcsönadva a könyv, akkor nem lehet személyt és időpontot megadni.') 



class BookOfNonUserCreateForm(ModelForm):
    owner_nonuser = forms.CharField(max_length=200, label='Könyv tulajdonosa', help_text="Valaki, aki nem regisztrált felhasználó az oldalon vagy még nem a barátod.", required=True)
    loan_date = forms.DateField(label='Ezen a napon kaptam', required=True, widget=DateInput(format='%Y-%m-%d'))
    comment = forms.CharField(max_length=300, label='Komment', required=False, widget=forms.Textarea, help_text="Ezt csak Te látod, magadnak írod.")

    class Meta:
        model = Book
        fields = ('owner_nonuser', 'last_name_author', 'first_name_author', 'title', 'language', 'loan_date', 'comment',)
        



class RequestManagementForm(forms.Form):
    user_to_handle = forms.CharField(max_length=50)
   


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=False, help_text='Opcionális (megadásával barátaid könnyebben megtalálhatnak).', label='Keresztnév')
    last_name = forms.CharField(max_length=50, required=False, help_text='Opcionális (megadásával barátaid könnyebben megtalálhatnak).', label='Vezetéknév')
    
    class Meta:
        model = User
        fields = ('username', 'last_name', 'first_name', 'password1', 'password2', )



class UserUpdateForm(ModelForm):
    last_name = forms.CharField(max_length=50, required=False, label='Vezetéknév')
    first_name = forms.CharField(max_length=50, required=False, label='Keresztnév')

    class Meta:
        model = User
        fields = ('username', 'last_name', 'first_name')



class ProfileUpdateForm(ModelForm):
    class Meta:
        model = Profile
        fields = ('image',)
        labels = {'image': _('Kép')}