from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from .forms import EventForms
from .models import Event


# create events form
def create_event(request):
    if request.method == "POST":
        form = EventForms(request.POST)
        if form.is_valid():
            event = form.save()
            event.pk
            return redirect('event_success', pk=event.pk)
    else:
        form = EventForms()
    return render(request, 'create_event.html', {'form': form})


# editing form
def edit_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForms(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('event_success', pk=pk)
    else:
        form = EventForms(instance=event)
    return render(request, 'edit_event.html', {'form': form})


def event_success(request, pk):
    return render(request, 'event_success.html', {'pk': pk})
