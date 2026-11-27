from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from tasks.forms import (
    TaskForm,
    TaskSearchForm,
    WorkerCreationForm,
    WorkerUpdateForm,
)
from tasks.models import Position, Task, TaskType

Worker = get_user_model()


def index(request: HttpRequest) -> HttpResponse:
    context = {
        "num_tasks": Task.objects.count(),
        "num_completed_tasks": Task.objects.filter(is_completed=True).count(),
        "num_workers": Worker.objects.count(),
        "num_positions": Position.objects.count(),
        "num_task_types": TaskType.objects.count(),
        "num_visits": request.session.get("num_visits", 0) + 1,
    }
    request.session["num_visits"] = context["num_visits"]
    return render(request, "tasks/index.html", context=context)


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["search_form"] = TaskSearchForm(initial={"name": name})
        return context

    def get_queryset(self):
        queryset = Task.objects.select_related(
            "task_type"
        ).prefetch_related("assignees")
        form = TaskSearchForm(self.request.GET)
        if form.is_valid():
            name = form.cleaned_data.get("name")
            if name:
                return queryset.filter(
                    Q(name__icontains=name) | Q(description__icontains=name)
                )
        return queryset


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task

    def get_queryset(self):
        return Task.objects.select_related(
            "task_type"
        ).prefetch_related("assignees__position")


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy("tasks:task-list")


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy("tasks:task-list")


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    success_url = reverse_lazy("tasks:task-list")


class TaskToggleStatusView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        task = get_object_or_404(Task, pk=pk)
        task.is_completed = not task.is_completed
        task.save(update_fields=["is_completed"])
        return redirect(request.META.get("HTTP_REFERER", "tasks:task-list"))


class WorkerListView(LoginRequiredMixin, ListView):
    model = Worker
    paginate_by = 5

    def get_queryset(self):
        return Worker.objects.select_related("position").annotate(
            tasks_count=Count("tasks")
        )


class WorkerDetailView(LoginRequiredMixin, DetailView):
    model = Worker

    def get_queryset(self):
        return Worker.objects.select_related("position").prefetch_related(
            "tasks__task_type"
        )


class WorkerCreateView(LoginRequiredMixin, CreateView):
    model = Worker
    form_class = WorkerCreationForm
    success_url = reverse_lazy("tasks:worker-list")


class WorkerUpdateView(LoginRequiredMixin, UpdateView):
    model = Worker
    form_class = WorkerUpdateForm
    success_url = reverse_lazy("tasks:worker-list")


class WorkerDeleteView(LoginRequiredMixin, DeleteView):
    model = Worker
    success_url = reverse_lazy("tasks:worker-list")


class PositionListView(LoginRequiredMixin, ListView):
    model = Position
    paginate_by = 10


class PositionCreateView(LoginRequiredMixin, CreateView):
    model = Position
    fields = "__all__"
    success_url = reverse_lazy("tasks:position-list")


class PositionUpdateView(LoginRequiredMixin, UpdateView):
    model = Position
    fields = "__all__"
    success_url = reverse_lazy("tasks:position-list")


class PositionDeleteView(LoginRequiredMixin, DeleteView):
    model = Position
    success_url = reverse_lazy("tasks:position-list")


class TaskTypeListView(LoginRequiredMixin, ListView):
    model = TaskType
    paginate_by = 10


class TaskTypeCreateView(LoginRequiredMixin, CreateView):
    model = TaskType
    fields = "__all__"
    success_url = reverse_lazy("tasks:task-type-list")


class TaskTypeUpdateView(LoginRequiredMixin, UpdateView):
    model = TaskType
    fields = "__all__"
    success_url = reverse_lazy("tasks:task-type-list")


class TaskTypeDeleteView(LoginRequiredMixin, DeleteView):
    model = TaskType
    success_url = reverse_lazy("tasks:task-type-list")
