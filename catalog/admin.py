from django.contrib import admin



from .models import Genre, Language, Book, FriendRequest, Friendship, RejectedFriendship, Profile

admin.site.register(Genre)
admin.site.register(Language)
admin.site.register(Profile)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('last_name_author', 'first_name_author', 'title', 'owner', 'owner_nonuser', 'borrower', 'borrower_nonuser', 'recommended', 'wished', 'loaned', 'loan_date', 'genre', 'language')
    list_filter = ('owner',)


@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'requested_friend', 'request_datetime', 'confirmed_request')
    list_filter = ('user', 'requested_friend')


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('confirmed_user', 'requested_user', 'confirmation_datetime')
    list_filter = ('confirmed_user', 'requested_user')


@admin.register(RejectedFriendship)
class RejectedFriendshipAdmin(admin.ModelAdmin):
    list_display = ('rejecter', 'rejected', 'rejection_datetime', 'notif_deleted')
    list_filter = ('rejecter', 'rejected')
