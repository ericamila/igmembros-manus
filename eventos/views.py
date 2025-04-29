from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Event
from .forms import EventForm

def event_list(request):
    events = Event.objects.all().order_by('date', 'time')
    return render(request, 'eventos/event_list.html', {
        'events': events,
        'active_menu': 'eventos',
    })

def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'eventos/event_detail.html', {
        'event': event,
        'active_menu': 'eventos',
    })

def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save()
            messages.success(request, 'Evento criado com sucesso!')
            return redirect('eventos:event_detail', pk=event.pk)
    else:
        form = EventForm()
    
    return render(request, 'eventos/event_form.html', {
        'form': form,
        'title': 'Novo Evento',
        'active_menu': 'eventos',
    })

def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk)
    
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evento atualizado com sucesso!')
            return redirect('eventos:event_detail', pk=event.pk)
    else:
        form = EventForm(instance=event)
    
    return render(request, 'eventos/event_form.html', {
        'form': form,
        'event': event,
        'title': 'Editar Evento',
        'active_menu': 'eventos',
    })

def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Evento excluído com sucesso!')
        return redirect('eventos:event_list')
    
    return render(request, 'eventos/event_confirm_delete.html', {
        'event': event,
        'active_menu': 'eventos',
    })
