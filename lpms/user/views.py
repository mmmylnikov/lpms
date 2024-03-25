from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView

from user.models import User
from user.forms import UserUpdateForm


class UserDetailView(DetailView):
    model = User

    def get_slug_field(self) -> str:
        return 'username'

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        context["teams"] = self.object.team_set.all()
        return context


class UserUpdateView(UpdateView):
    model = User
    form_class = UserUpdateForm

    def get_success_url(self) -> str:
        return reverse_lazy('user_detail_view',
                            kwargs={'slug': self.request.user.username})

    def get_slug_field(self) -> str:
        return 'username'
