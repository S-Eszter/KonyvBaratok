from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('mybooks/', views.MyBooksAllListView.as_view(), name='mybooks'),
    path('mybooks/recommended/', views.MyBooksRecommendedListView.as_view(), name='mybooks-recom'),
    path('mybooks/loaned/', views.MyBooksLoanedListView.as_view(), name='mybooks-loaned'),
    path('mybooks/wished/', views.MyBooksWishedListView.as_view(), name='mybooks-wished'),
    path('mybooks/<uuid:pk>', views.BookDetailView.as_view(), name='book-detail'),
]

urlpatterns += [   
    path('borrowedbooks/', views.BorrowedBooksByUserListView.as_view(), name='borrowed-books'),
    path('borrowedbooks/fromnonusers', views.book_of_nonuser_create_form, name='borrowed-books-fromnonusers'),
    path('recommendedbooks/byowner', views.RecommendedBooksByOwnerListView.as_view(), name='recom-books-byowner'),
    path('recommendedbooks/byauthor', views.RecommendedBooksByAuthorListView.as_view(), name='recom-books-byauthor'),
    path('recommendedbooks/bylanguage', views.RecommendedBooksByLanguageListView.as_view(), name='recom-books-bylang'),
    path('recommendedbooks/bygenre', views.RecommendedBooksByGenreListView.as_view(), name='recom-books-bygenre'),
    path('wishedbooks/byowner', views.WishedBooksByOwnerListView.as_view(), name='wished-books-byowner'),
    path('wishedbooks/byauthor', views.WishedBooksByAuthorListView.as_view(), name='wished-books-byauthor'),
]

urlpatterns += [  
    path('book/create/', views.book_create_form, name='book-create'),
    path('book/<uuid:pk>/update/', views.book_update_form, name='book-update'),
    path('book/<uuid:pk>/delete/', views.BookDelete.as_view(), name='book-delete'),
    path('book/<uuid:pk>/update/nonuserbook', views.book_of_nonuser_update_form, name='book-of-nonuser-update'),
    path('book/<uuid:pk>/delete/nonuserbook', views.BookOfNonUserDelete.as_view(), name='book-of-nonuser-delete'),
]

urlpatterns += [
    path('myfriends/', views.myfriends, name='myfriends'),
    path('myfriends/<int:pk>/deletefriend/', views.delete_friend, name='delete-friend'),
    path('myfriends/request/', views.request_friend, name='request-friend'),
    path('myfriends/request/<int:pk>/withdrawrequest/', views.withdraw_request, name='withdraw-request'),
    path('myfriends/friendnotifications/', views.friend_notif, name='friend-notif'),
    path('myfriends/<str:username>/recommendedbooks/', views.FriendRecommendedBooksListView.as_view(), name='friend-recom-books'),
    path('myfriends/<str:username>/wishedbooks/', views.FriendWishedBooksListView.as_view(), name='friend-wished-books'),
]