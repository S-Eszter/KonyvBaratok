import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.db.models import Q

from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from catalog.models import Book, Genre, Language, Friendship, FriendRequest, RejectedFriendship
from catalog.forms import FriendRequestForm, RequestManagementForm, SignUpForm, BookCreateForm, UserUpdateForm, ProfileUpdateForm, BookOfNonUserCreateForm

from pyuca import Collator

c = Collator()


# I. VIEWS CONNECTED TO USERS (SIGNUP, LOGIN, PROFILE, DELETE)

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save() 
            username = form.cleaned_data.get('username') 
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            messages.success(request, 'Sikeresen regisztráltad magad a KönyvBarátok oldalon!')
            return redirect('index')
    else:
        form = SignUpForm()
    
    return render(request, 'signup.html', {'form': form})



@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Sikeresen megváltoztattad a jelszavadat.')
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'change_password.html', {'form': form})



@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Sikeresen módosítottad az adataidat.')
            return redirect('profile') 

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'profile.html', context=context)



@login_required
def delete_profile(request):             # users can delete themselves 
    if request.method == 'POST':
        user = request.user
        user_instance = User.objects.get(username=user)

        # the deleted user's borrowed books:
        Book.objects.filter(borrower=user).update(borrower=None, borrower_nonuser=user.username)
        # the deleted user's loaned books:
        books_loaned = Book.objects.filter(owner=user, borrower__isnull=False)
        for book in books_loaned:
            book.owner = book.borrower
            book.borrower = None
            book.owner_nonuser = user.username
            book.recommended = False
            book.loaned = False
            book.save()

        user_instance.delete()
        return redirect('login')   
    
    return render(request, 'delete_profile.html', {})



# II. VIEWS CONNECTED TO FRIENDSHIPS   

@login_required
def request_friend(request):
    if request.method == 'POST':
        form = FriendRequestForm(request.user, request.POST)
        if form.is_valid():
            user = request.user
            rf = form.cleaned_data['requested_friend']
            rf_instance = User.objects.get(username=rf)
            instance = FriendRequest(user=user, requested_friend=rf_instance)
            instance.save()
            return redirect('request-friend') 
    
    else:
        form = FriendRequestForm(request.user) 

    requested_friends = FriendRequest.objects.filter(user=request.user).filter(confirmed_request=False)
    
    context = {
        'requested_friends': requested_friends,
        'form': form,
        'title': "Új barátok keresése"
    }  
    return render(request, 'requested_friend_form.html', context=context)



@login_required
def myfriends(request):
    friendship_list = Friendship.objects.filter(Q(confirmed_user=request.user) | Q(requested_user=request.user))
    cu_list = list(friendship_list.values_list('confirmed_user', flat=True))
    ru_list = list(friendship_list.values_list('requested_user', flat=True))
    merged_list = cu_list + ru_list
    friends = sorted(User.objects.filter(id__in=merged_list).exclude(username=request.user), key=lambda x: (c.sort_key(x.username)))
    
    context = {
        'friends': friends,
        'title': "Barátaim",  
    }  

    return render(request, 'myfriends.html', context=context)



@login_required
def delete_friend(request, pk):
    deleted_user = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        form= RequestManagementForm(request.POST)
        if form.is_valid():
            user = request.user
            user_to_handle = form.cleaned_data['user_to_handle']
            deleted_user = User.objects.get(username=user_to_handle)
            friendship_to_delete = Friendship.objects.filter(Q(confirmed_user=user, requested_user=deleted_user) | Q(confirmed_user=deleted_user, requested_user=user)).get()
            friendship_to_delete.delete()
            rf = FriendRequest.objects.filter(Q(user=user, requested_friend=deleted_user) | Q(user=deleted_user, requested_friend=user)).get()
            rf.delete()
            messages.success(request, f'Sikeresen törölted a barátaid közül: {deleted_user}')
            return redirect('myfriends')

        else:
            messages.error(request, 'Valami hiba történt...') 
            
    else:
        form = RequestManagementForm()

    context = {
        'deleted_user': deleted_user,
        'form': form,    
    }  
    return render(request, 'delete_friend.html', context=context)



@login_required
def withdraw_request(request, pk):
    rf_to_withdraw = get_object_or_404(User, pk=pk)   #requested_friend

    if request.method == 'POST':
        form= RequestManagementForm(request.POST)
        if form.is_valid():
            user = request.user
            user_to_handle = form.cleaned_data['user_to_handle']
            rf_to_withdraw = User.objects.get(username=user_to_handle)
            fr_instance = FriendRequest.objects.get(user=user, requested_friend=rf_to_withdraw)
            fr_instance.delete()
            messages.success(request, 'Sikeresen visszavontad a jelölésedet.')
            return redirect('request-friend')

        else:
            messages.error(request, 'Valami hiba történt...') 
            
    else:
        form = RequestManagementForm()

    context = {
        'rf_to_withdraw': rf_to_withdraw,
        'form': form,   
    }  
    return render(request, 'withdraw_request.html', context=context)



@login_required
def friend_notif(request):
    if request.method == 'POST':
        form= RequestManagementForm(request.POST)
        
        if form.is_valid():
            user = request.user
            user_to_handle = form.cleaned_data['user_to_handle']

            if user_to_handle.startswith('c'):
                uth = user_to_handle[1:]
                cu_instance = User.objects.get(username=uth)
                instance = Friendship(confirmed_user=cu_instance, requested_user=user)
                instance.save()
                fr = FriendRequest.objects.get(user=cu_instance, requested_friend=user)
                fr.confirmed_request = True
                fr.save()
                messages.success(request, f'{uth} és Te mostantól barátok vagytok.')
                return redirect('friend-notif')

            elif user_to_handle.startswith('r'):
                uth = user_to_handle[1:]
                rejected = User.objects.get(username=uth)
                instance = RejectedFriendship(rejecter=user, rejected=rejected)
                instance.save()
                fr = FriendRequest.objects.get(user=rejected, requested_friend=user)
                fr.delete()
                messages.success(request, f'{uth} barátnak jelölését sikeresen visszautasítottad.')
                return redirect('friend-notif')

            elif user_to_handle.startswith('d'):
                uth = user_to_handle[1:]
                rejecter = User.objects.get(username=uth)
                rej_fs = RejectedFriendship.objects.get(rejecter=rejecter, rejected=user)
                rej_fs.notif_deleted = True    # maybe the instance should be deleted instead of this
                rej_fs.save()
                return redirect('friend-notif')

            else:
                messages.error(request, 'Valami hiba történt...')
                return redirect('friend-notif')    

        else:
            messages.error(request, 'Valami hiba történt...') 
            
    else:
        form = RequestManagementForm()

    requests = FriendRequest.objects.filter(requested_friend=request.user).filter(confirmed_request=False)
    rejected_requests = RejectedFriendship.objects.filter(rejected=request.user).filter(notif_deleted=False)

    context = {
        'requests': requests,
        'rejected_requests': rejected_requests,
        'title': 'Értesítések'
    }

    return render(request, 'friend_notif.html', context=context)



# III. VIEWS CONNECTED TO BOOKS

@login_required
def index(request):
    
    num_books = Book.objects.filter(owner=request.user, owner_nonuser__isnull=True).count()
    loaned_books = Book.objects.filter(owner=request.user).filter(loaned=True).count()
    borrowed_books_fromuser = Book.objects.filter(borrower=request.user).count()
    borrowed_books_fromnonuser = Book.objects.filter(owner=request.user, owner_nonuser__isnull=False).count()
    borrowed_books = borrowed_books_fromuser + borrowed_books_fromnonuser
    friends = Friendship.objects.filter(Q(confirmed_user=request.user) | Q(requested_user=request.user))
    num_friends = friends.count()
    num_req_friend = FriendRequest.objects.filter(user=request.user, confirmed_request=False).count()
    num_requests = FriendRequest.objects.filter(requested_friend=request.user, confirmed_request=False).count()

    context = {
        'num_books': num_books,
        'loaned_books': loaned_books,
        'borrowed_books': borrowed_books,
        'num_friends': num_friends,
        'num_req_friend': num_req_friend,
        'num_requests': num_requests,
        'title': 'Home'    
    }

    return render(request, 'index.html', context=context)



@login_required
def book_create_form(request):
    if request.method == 'POST':
        form = BookCreateForm(request.user, request.POST)
        if form.is_valid():
            form.instance.owner = request.user
            form.save()
            messages.success(request, 'Sikeresen létrehoztál egy új könyvet.')
            return redirect('mybooks')

    else:
        form = BookCreateForm(request.user)
    
    context = {
        'form': form,
        'title': 'Új könyv létrehozása'    
    }  

    return render(request, 'book_form.html', context=context)



@login_required
def book_of_nonuser_create_form(request):
    if request.method == 'POST':
        form = BookOfNonUserCreateForm(request.POST)
        if form.is_valid():
            form.instance.owner = request.user # the owner created the book instance, the owner_nonuser is the real owner of the book
            form.save()
            messages.success(request, 'Sikeresen létrehoztál egy új könyvet.')
            return redirect('borrowed-books')

    else:
        form = BookOfNonUserCreateForm()

    context = {
        'form': form,
        'title': 'Ismerőstől kapott könyv létrehozása',
    }  

    return render(request, 'book_of_nonuser_form.html', context=context)



@login_required
def book_update_form(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookCreateForm(request.user, request.POST, instance=book)
        if form.is_valid():
            form.instance.owner = request.user
            form.save()
            messages.success(request, 'Sikeresen módosítottad a könyv adatait.')
            return redirect('book-detail', pk=pk )

    else:
        form = BookCreateForm(request.user, instance=book)
    
    context = {
        'form': form,
        'title': "Könyv módosítása"
    }  
    return render(request, 'book_form.html', context=context)



@login_required
def book_of_nonuser_update_form(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookOfNonUserCreateForm(request.POST, instance=book)
        if form.is_valid():
            form.instance.owner = request.user
            form.save()
            messages.success(request, 'Sikeresen módosítottad a könyv adatait.')
            return redirect('borrowed-books')

    else:
        form = BookOfNonUserCreateForm(instance=book)
    
    context = {
        'form': form,
        'title': "Ismerőstől kapott könyv módosítása"
    }  
    return render(request, 'book_of_nonuser_form.html', context=context)


class MyBooksAllListView(LoginRequiredMixin,generic.ListView): 
    model = Book
    context_object_name = 'my_book_list'   
    template_name = 'catalog/my_book_list.html'
    paginate_by = 50


    def get_queryset(self):
        books = sorted(Book.objects.filter(owner=self.request.user).filter(owner_nonuser__isnull=True), key=lambda x: (c.sort_key(x.last_name_author), c.sort_key(x.first_name_author), c.sort_key(x.title))) 
        return books 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Könyveim"
        return context



class MyBooksRecommendedListView(LoginRequiredMixin,generic.ListView):
    model = Book
    context_object_name = 'my_recom_books'  
    template_name = 'catalog/my_recom_books.html'
    paginate_by = 50

    def get_queryset(self):
        books = sorted(Book.objects.filter(owner=self.request.user).filter(recommended=True), key=lambda x: (c.sort_key(x.last_name_author), c.sort_key(x.first_name_author), c.sort_key(x.title))) 
        return books 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Ajánlott könyveim"
        return context



class MyBooksLoanedListView(LoginRequiredMixin,generic.ListView):
    model = Book
    context_object_name = 'my_loaned_books'  
    template_name = 'catalog/my_loaned_books.html'
    paginate_by = 50

    def get_queryset(self):
        books = sorted(Book.objects.filter(owner=self.request.user).filter(loaned=True), key=lambda x: (c.sort_key(x.last_name_author), c.sort_key(x.first_name_author), c.sort_key(x.title))) 
        return books 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Kölcsönadott könyveim"
        return context



class MyBooksWishedListView(LoginRequiredMixin,generic.ListView):
    model = Book
    context_object_name = 'my_wished_books'  
    template_name = 'catalog/my_wished_books.html'
    paginate_by = 50

    def get_queryset(self):
        books = sorted(Book.objects.filter(owner=self.request.user).filter(wished=True), key=lambda x: (c.sort_key(x.last_name_author), c.sort_key(x.first_name_author), c.sort_key(x.title)))
        return books

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Kívánságlistám"
        return context


class BookDetailView(generic.DetailView):
    model = Book


class BorrowedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    model = Book
    context_object_name = 'borrowed_books'
    template_name ='catalog/my_borrowed_books.html'
    paginate_by = 50
    
    def get_queryset(self):
        books = sorted(Book.objects.filter(borrower=self.request.user), key=lambda x: (c.sort_key(x.last_name_author), c.sort_key(x.first_name_author), c.sort_key(x.title))) 
        return books
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Kölcsönkért könyvek"
        context['books_of_nonusers'] = sorted(Book.objects.filter(owner=self.request.user).filter(owner_nonuser__isnull=False), key=lambda x: (c.sort_key(x.last_name_author), c.sort_key(x.first_name_author), c.sort_key(x.title)))
        return context

        

class BookDelete(LoginRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('mybooks')
    success_message = "Sikeresen törölted a könyvet."

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(BookDelete, self).delete(request, *args, **kwargs)



class BookOfNonUserDelete(LoginRequiredMixin, DeleteView):
    model = Book
    template_name = 'catalog/bookofnonuser_confirm_delete.html'
    success_url = reverse_lazy('borrowed-books')
    success_message = "Sikeresen törölted a könyvet."

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(BookOfNonUserDelete, self).delete(request, *args, **kwargs)



class RecommendedBooksByOwnerListView(LoginRequiredMixin,generic.ListView):
    model = Book
    context_object_name = 'recom_books'   
    template_name = 'catalog/recom_books_byowner.html'
    paginate_by = 50

    def get_queryset(self):
        friend_list = Friendship.objects.filter(Q(confirmed_user=self.request.user) | Q(requested_user=self.request.user))
        cu_list = list(friend_list.values_list('confirmed_user', flat=True))
        ru_list = list(friend_list.values_list('requested_user', flat=True))
        merged_list = cu_list + ru_list
        books = sorted(Book.objects.filter(owner__id__in=merged_list).exclude(owner=self.request.user).filter(recommended=True), key=lambda x: (c.sort_key(x.owner.username), c.sort_key(x.last_name_author), c.sort_key(x.first_name_author), c.sort_key(x.title)))
        return books

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Ajánlott könyvek - barátok szerint rendezve"
        return context



class RecommendedBooksByAuthorListView(LoginRequiredMixin,generic.ListView):
    model = Book
    context_object_name = 'recom_books'  
    template_name = 'catalog/recom_books_byauthor.html'
    paginate_by = 50

    def get_queryset(self):
        friend_list = Friendship.objects.filter(Q(confirmed_user=self.request.user) | Q(requested_user=self.request.user))
        cu_list = list(friend_list.values_list('confirmed_user', flat=True))
        ru_list = list(friend_list.values_list('requested_user', flat=True))
        merged_list = cu_list + ru_list
        books = sorted(Book.objects.filter(owner__id__in=merged_list).exclude(owner=self.request.user).filter(recommended=True), key=lambda x: (c.sort_key(x.last_name_author), c.sort_key(x.first_name_author), c.sort_key(x.title)))
        return books

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Ajánlott könyvek - szerző szerint rendezve"
        return context



class RecommendedBooksByLanguageListView(LoginRequiredMixin,generic.ListView):
    model = Book
    context_object_name = 'recom_books'  
    template_name = 'catalog/recom_books_bylang.html'
    paginate_by = 50

    def get_queryset(self):
        friend_list = Friendship.objects.filter(Q(confirmed_user=self.request.user) | Q(requested_user=self.request.user))
        cu_list = list(friend_list.values_list('confirmed_user', flat=True))
        ru_list = list(friend_list.values_list('requested_user', flat=True))
        merged_list = cu_list + ru_list
        books = sorted(Book.objects.filter(owner__id__in=merged_list).exclude(owner=self.request.user).filter(recommended=True), key=lambda x: (c.sort_key(x.language.name), c.sort_key(x.last_name_author), c.sort_key(x.first_name_author), c.sort_key(x.title)))
        return books

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Ajánlott könyvek - nyelvek szerint rendezve"
        return context


class RecommendedBooksByGenreListView(LoginRequiredMixin,generic.ListView):
    model = Book
    context_object_name = 'recom_books'   
    template_name = 'catalog/recom_books_bygenre.html'
    paginate_by = 50

    def get_queryset(self):
        friend_list = Friendship.objects.filter(Q(confirmed_user=self.request.user) | Q(requested_user=self.request.user))
        cu_list = list(friend_list.values_list('confirmed_user', flat=True))
        ru_list = list(friend_list.values_list('requested_user', flat=True))
        merged_list = cu_list + ru_list
        books = sorted(Book.objects.filter(owner__id__in=merged_list).exclude(owner=self.request.user).filter(recommended=True), key=lambda x: (c.sort_key(x.genre.name), c.sort_key(x.last_name_author), c.sort_key(x.first_name_author), c.sort_key(x.title)))
        return books

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Ajánlott könyvek - műfaj szerint rendezve"
        return context



class WishedBooksByOwnerListView(LoginRequiredMixin,generic.ListView):
    model = Book
    context_object_name = 'wished_books'   
    template_name = 'catalog/wished_books_byowner.html'
    paginate_by = 50

    def get_queryset(self):
        friend_list = Friendship.objects.filter(Q(confirmed_user=self.request.user) | Q(requested_user=self.request.user))
        cu_list = list(friend_list.values_list('confirmed_user', flat=True))
        ru_list = list(friend_list.values_list('requested_user', flat=True))
        merged_list = cu_list + ru_list
        books = sorted(Book.objects.filter(owner__id__in=merged_list).exclude(owner=self.request.user).filter(wished=True), key=lambda x: (c.sort_key(x.owner.username), c.sort_key(x.last_name_author), c.sort_key(x.first_name_author), c.sort_key(x.title)))
        return books

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Kívánságlisták - barát szerint rendezve"
        return context



class WishedBooksByAuthorListView(LoginRequiredMixin,generic.ListView):
    model = Book
    context_object_name = 'wished_books'   
    template_name = 'catalog/wished_books_byauthor.html'
    paginate_by = 50

    def get_queryset(self):
        friend_list = Friendship.objects.filter(Q(confirmed_user=self.request.user) | Q(requested_user=self.request.user))
        cu_list = list(friend_list.values_list('confirmed_user', flat=True))
        ru_list = list(friend_list.values_list('requested_user', flat=True))
        merged_list = cu_list + ru_list
        books = sorted(Book.objects.filter(owner__id__in=merged_list).exclude(owner=self.request.user).filter(wished=True), key=lambda x: (c.sort_key(x.last_name_author), c.sort_key(x.first_name_author), c.sort_key(x.title)))
        return books

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Kívánságlisták - szerző szerint rendezve"
        return context




class FriendRecommendedBooksListView(LoginRequiredMixin,generic.ListView):
    model = Book
    context_object_name = 'friend_recom_books'  
    template_name = 'catalog/friend_recom_books.html'
    paginate_by = 50

    def get_queryset(self):
        friend = get_object_or_404(User, username=self.kwargs.get('username'))
        books = sorted(Book.objects.filter(owner=friend).filter(recommended=True), key=lambda x: (c.sort_key(x.last_name_author), c.sort_key(x.first_name_author), c.sort_key(x.title))) 
        return books 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        friend = get_object_or_404(User, username=self.kwargs.get('username'))
        context['friend'] = friend
        context['title'] = f'{friend} ajánlott könyvei'
        return context


class FriendWishedBooksListView(LoginRequiredMixin,generic.ListView):
    model = Book
    context_object_name = 'friend_wished_books'  
    template_name = 'catalog/friend_wished_books.html'
    paginate_by = 50

    def get_queryset(self):
        friend = get_object_or_404(User, username=self.kwargs.get('username'))
        books = sorted(Book.objects.filter(owner=friend).filter(wished=True), key=lambda x: (c.sort_key(x.last_name_author), c.sort_key(x.first_name_author), c.sort_key(x.title))) 
        return books

    def get_context_data(self, **kwargs):  
        context = super().get_context_data(**kwargs)
        friend = get_object_or_404(User, username=self.kwargs.get('username'))
        context['friend'] = friend
        context['title'] = f'{friend} kívánságlistája'
        return context