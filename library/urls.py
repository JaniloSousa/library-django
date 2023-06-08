from django.urls import path, include
from library import views

app_name = "library"
urlpatterns = [
    path('', views.home, name="home"),
    path('search/', views.search, name="search"),

    # book CRUD
    path('book/create/', views.create, name="create"), # create
    path('book/<int:book_id>/', views.book, name="book"), # read
    path('book/<int:book_id>/update/', views.update, name="update"), # update
    path('book/<int:book_id>/delete/', views.delete, name="delete"), # delete

    # user "CRUD"
    path('user/create/', views.register, name="register"), # create
    path('user/login/', views.login, name="login"), # entrar
    path('user/logout/', views.logout, name="logout"), # sair
    path('user/update/', views.user_update, name="user_update"), # atualizar

    # about
    path('about/', views.about, name="about"),
]
