from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import Book, Author, Genre, BookInstance, Review, Reservation
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from .forms import RenewBookForm, ReviewForm, ReservationForm
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import permission_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required



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
    template_name = "catalog/bookinstance_list_borrowed_all.html"

    def get_queryset(self):
        return BookInstance.objects.filter(
            status__exact="o"
        )

@permission_required("catalog.can_mark_returned")
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(
        BookInstance,
        pk=pk
    )

    if request.method == "POST":
        form = RenewBookForm(request.POST)

        if form.is_valid():
            book_instance.due_back = form.cleaned_data["renewal_date"]
            book_instance.save()
            return HttpResponseRedirect(reverse("all-borrowed"))

    else:
        form = RenewBookForm(
            initial={"renewal_date": book_instance.due_back}
        )
    return render(
        request,
        "catalog/book_renew_librarian.html",
        {
            "form": form,
            "book_instance": book_instance,
        }
    )
class AuthorCreate(CreateView):
    model = Author
    fields = "__all__"

class AuthorUpdate(UpdateView):
    model = Author
    fields = "__all__"

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy("authors")

@login_required
def add_review(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if Review.objects.filter(book=book, reviewer=request.user).exists():
        return render(
            request,
            "catalog/review_form.html",
            {
                "form": ReviewForm(),
                "book": book,
                "error_message": "この本には既にレビューを投稿しています。"
            }
        )

    if request.method == "POST":
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.reviewer = request.user
            review.save()
            return HttpResponseRedirect(book.get_absolute_url())

    else:
        form = ReviewForm()

    return render(
        request,
        "catalog/review_form.html",
        {
            "form": form,
            "book": book,
        },
    )
@login_required
def reserve_book(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":
        form = ReservationForm(request.POST)

        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.book = book
            reservation.user = request.user
            reservation.save()
            return HttpResponseRedirect(book.get_absolute_url())
    else:
        form = ReservationForm()
    return render(
        request,
        "catalog/reservation_form.html",
        {
            "form": form,
            "book": book,
        },
    )

class MyReservationsListView(LoginRequiredMixin, generic.ListView):
    model = Reservation
    template_name = "catalog/my_reservations.html"
    context_object_name = "reservations"

    def get_queryset(self):
        return Reservation.objects.filter(
            user=self.request.user
        ).order_by("-created_at")

@login_required
def cancel_reservation(request, pk):
    reservation = get_object_or_404(
        Reservation,
        pk=pk,
        user=request.user,
    )

    reservation.delete()

    return HttpResponseRedirect(
        reverse("my-reservations")
    )