from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import FoodItem, NGO, Volunteer, FoodRequest
from .forms import FoodForm

# ==========================================
# 1. CORE PAGES & GENERAL SYSTEM VIEWS
# ==========================================
def home(request):
    total_batches = FoodItem.objects.count()
    available_now = FoodItem.objects.filter(status='Available').count()
    successful_deliveries = FoodRequest.objects.filter(status='delivered').count()
    recent_food = FoodItem.objects.filter(status='Available').order_by('-id')[:5]

    return render(request, 'home.html', {
        'total_batches': total_batches,
        'available_now': available_now,
        'successful_deliveries': successful_deliveries,
        'recent_food': recent_food,
    })


def food_list(request):
    all_food = FoodItem.objects.filter(status='Available') 
    return render(request, 'food_list.html', {'foods': all_food})


def add_food(request):
    if request.method == "POST":
        form = FoodForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('food_list') 
    else:
        form = FoodForm()
    return render(request, 'add_food.html', {'form': form})


# ==========================================
# 2. NGO & VOLUNTEER REGISTRATION LOGIC
# ==========================================
def register_ngo(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        ngo_name = request.POST.get('ngo_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        
        if User.objects.filter(username=email).exists():
            messages.error(request, "An account with this email already exists.")
            return redirect('register_ngo')
            
        # Create base user account using email as the username
        user = User.objects.create_user(username=email, email=email, password=password)
        
        # Save directly to NGO model (auto-generates NGO-1001 tracking code)
        profile = NGO.objects.create(
            user=user, 
            ngo_name=ngo_name, 
            address=address, 
            phone=phone
        )
        
        return render(request, 'registration_success.html', {
            'unique_id': profile.ngo_id, 
            'role': 'NGO'
        })
        
    return render(request, 'ngo_register.html')


def register_volunteer(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        v_name = request.POST.get('v_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        area = request.POST.get('area', '').strip()
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "This username is already taken.")
            return redirect('register_volunteer')
            
        # Create user account using the provided username
        user = User.objects.create_user(username=username, password=password)
        
        # Save directly to Volunteer model (auto-generates VOL-1001 tracking code)
        profile = Volunteer.objects.create(
            user=user, 
            city=area,  # Maps input area to database city field
            phone=phone
        )
        
        return render(request, 'registration_success.html', {
            'unique_id': profile.volunteer_id, 
            'role': 'Volunteer'
        })
        
    return render(request, 'volunteer_register.html')


# ==========================================
# 3. OPERATION REQUESTS & DASHBOARDS
# ==========================================
@login_required
def request_food(request):
    try:
        ngo_profile = request.user.ngo
    except Exception:
        return render(request, 'home.html', {'error': 'You must be registered as an NGO to request food.'})

    if request.method == 'POST':
        f_id = request.POST.get('food_id')
        reaz = request.POST.get('reason', 'General Request')
        
        if not f_id:
            return render(request, 'request_food.html', {'error': 'Please select a food item.'})

        try:
            food_item = get_object_or_404(FoodItem, id=f_id)
            
            new_req = FoodRequest()
            new_req.food = food_item
            new_req.ngo_name = ngo_profile.ngo_name
            new_req.address = ngo_profile.address
            new_req.reason = reaz
            new_req.status = 'pending'
            new_req.save() 

            food_item.status = 'Requested'
            food_item.save()
            
            return redirect('volunteer_dashboard')
            
        except Exception as e:
            print(f"DATABASE ERROR: {e}")
            return render(request, 'request_food.html', {
                'error': f'Database Error: {e}', 
                'available_food': FoodItem.objects.filter(status='Available')
            })

    available_food = FoodItem.objects.filter(status='Available')
    return render(request, 'request_food.html', {'available_food': available_food})


@login_required
def volunteer_dashboard(request):
    # Open unassigned pool of logistics requests
    pending_requests = FoodRequest.objects.filter(assigned_to__isnull=True, status='pending')
    
    # Active tasks claimed by current session worker
    my_tasks = FoodRequest.objects.filter(assigned_to=request.user)
    success_count = my_tasks.filter(status='delivered').count()

    return render(request, 'volunteer_dashboard.html', {
        'pending_requests': pending_requests,
        'my_tasks': my_tasks,
        'success_count': success_count
    })


@login_required
def accept_delivery(request, request_id):
    food_req = get_object_or_404(FoodRequest, id=request_id)
    
    if food_req.assigned_to is None:
        food_req.assigned_to = request.user
        food_req.status = 'delivered' 
        food_req.save()
        
        food_item = food_req.food
        food_item.status = 'Delivered'
        food_item.save()
        
    return redirect('volunteer_dashboard')


@login_required
def mark_delivered(request, request_id):
    food_request = get_object_or_404(FoodRequest, id=request_id)
    
    food_request.status = 'delivered'
    food_request.save()
    
    food_item = food_request.food
    food_item.status = 'Delivered'
    food_item.save()
    
    return redirect('volunteer_dashboard')


@login_required
def profile_view(request):
    user = request.user
    ngo_profile = None
    volunteer_profile = None

    if hasattr(user, 'ngo'):
        ngo_profile = user.ngo
    
    if hasattr(user, 'volunteer'):
        volunteer_profile = user.volunteer

    return render(request, 'profile.html', {
        'user': user,
        'ngo': ngo_profile,
        'volunteer': volunteer_profile
    })


# ==========================================
# 4. SECURE USER ID ACCELERATOR LOGIN
# ==========================================
# Make sure this decorator and function are completely aligned to the left margin!
@login_required
def ngo_dashboard(request):
    try:
        ngo_profile = request.user.ngo
    except Exception:
        return render(request, 'home.html', {'error': 'Unauthorized access.'})
        
    my_requests = FoodRequest.objects.filter(ngo_name=ngo_profile.ngo_name).order_by('-id')
    
    return render(request, 'ngo_dashboard.html', {
        'ngo': ngo_profile,
        'my_requests': my_requests
    })
def user_login(request):
    if request.method == 'POST':
        custom_id = request.POST.get('custom_id', '').strip()
        password = request.POST.get('password', '')
        
        user_account = None
        
        # 1. Trace the custom ID back to the base Django User account
        if custom_id.startswith('NGO-'):
            profile = NGO.objects.filter(ngo_id=custom_id).first()
            if profile:
                user_account = profile.user
                
        elif custom_id.startswith('VOL-'):
            profile = Volunteer.objects.filter(volunteer_id=custom_id).first()
            if profile:
                user_account = profile.user
        
        # 2. Authenticate using the underlying Django username
        if user_account is not None:
            # We pass user_account.username (which is what Django knows), NOT custom_id!
            user = authenticate(username=user_account.username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back! Logged in successfully.")
                
                # 3. Direct to correct dashboards
                if custom_id.startswith('NGO-'):
                    return redirect('ngo_dashboard')
                else:
                    return redirect('volunteer_dashboard')
            else:
                messages.error(request, "Authentication Failed: Incorrect password for this ID.")
        else:
            messages.error(request, f"Identity Error: Unique ID '{custom_id}' does not exist.")
            
    return render(request, 'login.html')

   

