from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required


from .models import Topic, Room, Message, User
from .forms import RoomForm, MessageForm, MyUserCreationForm, UserUpdateForm


def home(request):
    q = request.GET.get('q') if request.GET.get('q') else ''
    topics = Topic.objects.all()
    rooms = Room.objects.filter(Q(topic__name__icontains=q) | Q(
        name__icontains=q) | Q(description__icontains=q))

    if len(rooms) <= 0:
        context = {'error': "Nothing Found."}
        return render(request, '404.html', context)

    room_count = rooms.count()

    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {'topics': topics, 'rooms': rooms,
               'room_count': room_count, 'room_messages': room_messages}

    return render(request, 'discord/home.html', context)


def topics(request):
    topics = Topic.objects.all()

    if len(topics) <= 0:
        context = {'error': 'No Topics Available'}
        return render(request, '404.html', context)

    if request.method == 'POST':
        q = request.POST.get('q') if request.POST.get('q') is not None else ''
        topics = Topic.objects.filter(name__icontains=q)

    context = {'topics': topics}
    return render(request, 'discord/topics.html', context)


def room(request, pk):
    try:
        room = Room.objects.get(id=pk)
        room_messages = room.message_set.all()
        participants = room.participants.all()
    except Room.DoesNotExist:
        error = 'Room does not exist.'
        context = {'error': error}
        return render(request, '404.html', context)

    if request.method == 'POST':
        comment = request.POST.get('body')

        Message.objects.create(
            user=request.user,
            room=room,
            body=comment
        )

        if request.user != room.user:
            room.participants.add(request.user)

        return redirect('room', room.id)

    context = {'room': room, 'room_messages': room_messages,
               'participants': participants}
    return render(request, 'discord/room.html', context)


def login_user(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)

        except User.DoesNotExist:
            messages.error(request, "User does not exist.")
            return redirect('login')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Email or Password did not match.")
            return redirect('login')

    context = {}
    return render(request, 'discord/login.html', context)


@login_required(login_url='home')
def logout_user(request):
    logout(request)
    return redirect('login')


def signup_user(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.email = user.email.lower()
            user.save()
            login(request, user)
            return redirect('home')
        # else:
        #     messages.error(request, 'Something is wrong.')
        #     return redirect('signup')

    context = {'form': form}
    return render(request, 'discord/signup.html', context)


@login_required(login_url='login')
def profile(request, pk):
    try:
        user = User.objects.get(id=pk)
        topics = Topic.objects.all()
        rooms = user.room_set.all()
        room_messages = user.message_set.all()
        # user_profile = user.userprofile.all()
    except User.DoesNotExist:
        context = {'error': 'User does not exist'}
        return render(request, '404.html', context)

    context = {'user': user, 'topics': topics,
               'rooms': rooms, 'room_messages': room_messages}

    return render(request, 'discord/profile.html', context)


@login_required(login_url='login')
def edit_profile(request, pk):
    try:
        user = User.objects.get(id=pk)
    except User.DoesNotExist:
        context = {'error': 'User does not exist'}
        return render(request, '404.html', context)

    form = UserUpdateForm(instance=user)

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=user)

        if form.is_valid():
            form.save()
            return redirect('profile', user.id)

    context = {'user': user, 'form': form}
    return render(request, 'discord/edit-profile.html', context)


@login_required(login_url='login')
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            user=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )

        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'discord/create-room.html', context)


@login_required(login_url='login')
def update_room(request, pk):
    try:
        room = Room.objects.get(id=pk)
    except Room.DoesNotExist:
        context = {'error': "Room does not exist."}
        return render(request, '404.html', context)

    if request.user != room.user:
        messages.error(request, "You are not allowed for this operation")
        return redirect('home')

    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        room.topic = topic
        room.name = request.POST.get('name')
        room.description = request.POST.get('description')
        room.save()

        return redirect('home')

    context = {'form': form, 'room': room, 'topics': topics}
    return render(request, 'discord/update-room.html', context)


@login_required(login_url='login')
def delete_room(request, pk):
    try:
        room = Room.objects.get(id=pk)
    except Room.DoesNotExist:
        context = {'error': "Room not found."}
        return render(request, '404.html', context)

    if request.user != room.user:
        messages.error(request, 'You are not allowed for this operation.')
        return redirect('home')

    if request.method == 'POST':
        room.delete()
        return redirect('home')

    context = {'obj': room}
    return render(request, 'discord/delete.html', context)


@login_required(login_url='login')
def update_message(request, pk):
    try:
        room_message = Message.objects.get(id=pk)
    except Message.DoesNotExist:
        context = {'error': 'Message does not exist'}
        return render(request, '404.html', context)

    form = MessageForm(instance=room_message)

    if request.user != room_message.user:
        messages.error(request, 'Your are not allowed for this operations.')
        return redirect('room', room_message.room.id)

    if request.method == 'POST':
        form = MessageForm(request.POST, instance=room_message)

        if form.is_valid():
            form.save()
            return redirect('room', room_message.room.id)

    context = {'form': form}
    return render(request, 'discord/update-message.html', context)


@login_required(login_url='login')
def delete_message(request, pk):
    try:
        room_message = Message.objects.get(id=pk)
    except Message.DoesNotExist:
        context = {'error': 'Message does not exist'}
        return render(request, '404.html', context)

    if request.user != room_message.user:
        messages.error(request, "You are not allowed for this operation.")
        return redirect('room', room_message.room.id)

    if request.method == 'POST':
        room_message.delete()
        return redirect('room', room_message.room.id)

    context = {'obj': room_message}

    return render(request, 'discord/delete.html', context)
