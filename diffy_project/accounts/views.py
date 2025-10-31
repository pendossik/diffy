from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout

User = get_user_model()

#@csrf_exempt    # временно отключаем csrf-защиту для упрощения тестирования
def register(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST request allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecoderError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return JsonResponse({'error': 'username and password required'}, status = 400)
    
    if len(username) < 2:
        return JsonResponse({'error': 'The username must be at least 2 smb long'}, status=400)
    if len(password) < 8:
        return JsonResponse({'error': 'The password must be at least 8 smb long'}, status=400)
    
    if User.objects.filter(username=username).exists():
        return JsonResponse({'error': 'Username already taken'}, status=409)
    
    user = User.objects.create_user(username=username, password=password)

    return JsonResponse({'message': 'User registered successfully'}, status = 201)


# @csrf_exempt
def login_user(request):
    if request.method != "POST":
        return JsonResponse({'error': 'Only POST request allowed'}, status=405)
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JsonResponse({'error': 'username and password required'}, status=405)
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'message': f'You are welcome, {username}!'})
        else:
            return JsonResponse({'error': 'uncorrenct login data'}, status=400)
        
    except json.JSONDecoderError:
        return JsonResponse({'error': 'uncorrect format of JSON'}, status=400)
    

def current_user(request):
    if request.user.is_authenticated:
        return JsonResponse({'username': request.user.username})
    else:
        return JsonResponse({'username' : None})


def logout_user(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            logout(request)
            return JsonResponse({'message' : 'Succesfully logOUT'})
        else:
            return JsonResponse({'message' : 'You are not logged in'})
    return JsonResponse({'error': 'Only POST request allowed'}, status=405)

def register_page(request):
    return render(request, 'accounts/register.html')


def login_page(request):
    return render(request, 'accounts/login.html')

def profile_page(request):
    return render(request, 'accounts/profile.html')