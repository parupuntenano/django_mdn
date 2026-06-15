from django.shortcuts import render
from .models import Book, Author, Genre, BookInstance
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin


def index(request):
    num_books = Book.objects.count()
    num_instances = BookInstance.objects.count()
    num_authors = Author.objects.count()
    num_genres = Genre.objects.count()

    num_instances_available = (
        BookInstance.objects.filter(
            status__exact="a"
        ).count()
    )

    num_visits = request.session.get("num_visits", 0)

    request.session["num_visits"] = num_visits + 1

    context = {
        "num_books": num_books,
        "num_instances": num_instances,
        "num_authors": num_authors,
        "num_genres": num_genres,
        "num_instances_available": num_instances_available,
        "num_visits": num_visits,
    }

    return render(request, "catalog/index.html", context)

class BookListView(generic.ListView):
    model = Book
    paginate_by = 10

    def get_queryset(self):
        return Book.objects.all()

class BookDetailView(generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    model = Author

class AuthorDetailView(generic.DetailView):
    model = Author

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(
            borrower=self.request.user,
            status__exact="o",
        )
    
class LoanedBooksAllListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    generic.ListView
):
    model = BookInstance
    permission_required = "catalog.can_mark_returned"
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(
            status__exact="o"
        )