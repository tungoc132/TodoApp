from typing import Any
from django.forms.models import BaseModelForm
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404

from .models import Task
from .forms import RegisterForm, UserUpdateForm, ProfileUpdateForm, TaskForm
from django.views.generic.list import ListView
from django.views.generic.edit import DeleteView
from django.views.decorators.http import require_GET

from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

# Login account
class Login(LoginView):
    template_name = 'auth/login.html'
    fields = '__all__'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('alltasks')  

# Register new account
def regist(request):
    if request.method == 'GET':
        form = RegisterForm()
        redirect_authenticated_user = True
        return render(request, 'auth/regist.html', {'form' : form})
    
    if request.method == 'POST':
        form = RegisterForm(request.POST) 
        if form.is_valid():
            user = form.save(commit=False)
            # user.username = user.username.lower()
            user.save()
            # login(request, user)
            return redirect('login')
        else:
            return render(request, 'auth/regist.html', {'form': form})
 
# Update user information       
@login_required
def userUpdate(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('alltasks')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
        
    context = {
        'u_form' : u_form,
        'p_form' : p_form
    }
    return render(request, 'profile/profile_edit.html', context)

# Show all tasks
class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'alltasks'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['alltasks'] = context['alltasks'].filter(user=self.request.user)
        context['count'] = context['alltasks'].filter(complete=False).count()
        
        search_input = self.request.GET.get('search-area') or ''
        
        if search_input:
            context['alltasks'] = context['alltasks'].filter(title__icontains=search_input)
        context['search_input'] = search_input
        
        return context

# Create new task
def taskcreate(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return HttpResponseRedirect('/')
    else:
        form = TaskForm
    
    return render(request, 'todo/task_form.html', {'form': form})

# Update created task
def taskupdate(request, task_id):
    task = Task.objects.get(pk=task_id)
    form = TaskForm(request.POST or None, instance=task)

    if form.is_valid():
        form.save()
        return redirect('alltasks')
    
    return render(request, 'todo/task_update.html', {'task': task, 'form': form})

# Delete task
def taskdelete(request, task_id):
    task = Task.objects.get(pk=task_id)    
    if request.method == "POST":
        task.delete()
        return redirect('alltasks')
    
    return render(request, 'todo/confirm_delete.html', {'task': task,})
