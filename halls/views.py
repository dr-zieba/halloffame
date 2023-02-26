import urllib

from django.contrib.auth.views import LoginView
import requests
from django.forms.utils import ErrorList
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from .models import Hall, Video
from .forms import VideoForm, SearchForm
from django.conf import settings

# Create your views here.


def home(request):
    return render(request, "halls/home.html", {})


def dashboard(request):
    hall = Hall.objects.filter(user=request.user)
    context = {"hall": hall}
    return render(request, "halls/dashboard.html", context)


def add_video(request, pk):
    form = VideoForm()
    search_form = SearchForm()
    hall = Hall.objects.get(pk=pk)
    errors = None
    if not hall.user == request.user:
        raise Http404
    if request.method == "POST":
        form = VideoForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            parsed_url = urllib.parse.urlparse(form.url)
            video_id = urllib.parse.parse_qs(parsed_url.query).get("v")
            if video_id:
                form.youtube_id = video_id[0]
                response = requests.get(
                    f"https://youtube.googleapis.com/youtube/v3/videos?part=snippet&id={video_id[0]}&key={settings.YOUTUBE_API_KEY}"
                )
                json = response.json()
                title = json["items"][0]["snippet"]["title"]
                form.title = title
                form.hall = hall
                form.save()
                return redirect("detail-hall", pk)
            else:
                errors = "Not a youtube"

    context = {"form": form, "search_form": search_form, "hall": hall, "errors": errors}
    return render(request, "halls/add_video.html", context)


def video_search(request):
    form_search = SearchForm(request.GET)
    if form_search.is_valid():
        search = urllib.parse.quote(form_search.cleaned_data["search_term"])
        response = requests.get(
            f"https://youtube.googleapis.com/youtube/v3/search?part=snippet&maxResults=6&q={search}&key={settings.YOUTUBE_API_KEY}"
        )
        return JsonResponse(response.json())
    return JsonResponse({"Hello": "Not working..."})


class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("home")
    template_name = "registration/signup.html"

    def form_valid(self, form):
        view = super(SignUp, self).form_valid(form)
        username, password = form.cleaned_data.get("username"), form.cleaned_data.get(
            "password1"
        )
        user = authenticate(username=username, password=password)
        login(self.request, user)

        return redirect("home")


class CreateHall(generic.CreateView):
    model = Hall
    fields = ["title"]
    template_name = "halls/create_hall.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        form.instance.user = self.request.user
        super(CreateHall, self).form_valid(form)

        return redirect("home")


class DetailHall(generic.DetailView):
    model = Hall
    template_name = "halls/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["details"] = self.object.video_set.all()
        return context


class UpdateHall(generic.UpdateView):
    model = Hall
    fields = ["title"]
    template_name = "halls/update.html"

    def get_success_url(self, **kwargs):
        return reverse_lazy("detail-hall", args=(self.object.id,))


class DeleteHall(generic.DeleteView):
    model = Hall
    template_name = "halls/delete.html"
    # success_url = reverse_lazy('dashboard')

    def get_success_url(self, **kwargs):
        return reverse_lazy("detail-hall", args=(self.object.id,))


class DeleteVideo(generic.DeleteView):
    model = Video
    template_name = "halls/delete_video.html"
    # success_url = reverse_lazy('dashboard')

    def get_success_url(self):
        return reverse_lazy("detail-hall", args=(self.object.hall.id,))
