from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib import admin
from teenApp.entities.child import Child
from teenApp.entities.reward import Reward
from .forms import TaskForm 
from django.http import HttpResponse, JsonResponse
from teenApp.entities.task import Task
from teenApp.entities.mentor import Mentor
from teenApp.entities.redemption import Redemption
from teenApp.entities.shop import Shop
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from teenApp.use_cases.assign_task import AssignTaskToChildren
from teenApp.use_cases.assign_points import AssignPointsToChildren
from teenApp.use_cases.assign_bonus_points import AssignBonusPoints
from teenApp.use_cases.manage_child import ManageChild
from .forms import RedemptionForm, IdentifyChildForm, TaskImageForm, BonusPointsForm
import random
from datetime import datetime
from django.utils.timezone import now
from django.db.models import Sum, F
from django.db.models.functions import TruncMonth
from django.templatetags.static import static
from django.http import HttpResponse
import json
from django.contrib.auth import logout
from teenApp.interface_adapters.forms import DateRangeForm,DateRangeMForm

@login_required
def logout_view(request):
    logout(request)
    return redirect('two_factor:login')

@login_required
def home_redirect(request):
    if request.user.groups.filter(name='Children').exists():
        return redirect('child_home')
    elif request.user.groups.filter(name='Mentors').exists():
        return redirect('mentor_home')
    elif request.user.groups.filter(name='Shops').exists():
        return redirect('shop_home')
    else:
        return redirect('default_home')

def default_home(request):
    return HttpResponse("Home")

@login_required
def child_home(request):
    child = Child.objects.get(user=request.user)

    greetings = {
        0: f"Wishing you a strong start to the week to collect points!",  # Sunday
        1: f"It's Monday! Stay positive and keep working towards your goals!",
        2: f"It's Tuesday! Keep pushing forward and make today count!",
        3: f"It's Wednesday! You're halfway through the week, stay focused!",
        4: f"It's Thursday! Almost there, finish the week strong!",
        5: f"Happy Friday! Enjoy your day and make the most out of it!",  # Friday
        6: f"It's Saturday! Relax and recharge for the upcoming week!",
    }
    
    today = datetime.today().weekday()+1
    greeting = greetings.get(today, f"Hey {child.user.username}, have a great day!")
    
    new_tasks = child.assigned_tasks.filter(new_task=True, viewed=False)
    new_tasks_count = new_tasks.count()

    if request.method == 'POST' and 'close_notification' in request.POST:
        new_tasks.update(viewed=True)
        new_tasks.update(new_task=False)

    return render(request, 'child_home.html', {'child': child, 'greeting': greeting, 'new_tasks_count': new_tasks_count, 'new_tasks': new_tasks})

@login_required
def child_redemption_history(request):
    child = Child.objects.get(user=request.user)
    form = DateRangeForm(request.GET or None)
    redemptions = Redemption.objects.filter(child=child).order_by('-date_redeemed')
    default_date = date(2201, 1, 1)  # תאריך ברירת מחדל

    if form.is_valid():
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
    else:
        start_date = None
        end_date = None

    if start_date and end_date:
        redemptions = redemptions.filter(date_redeemed__range=(start_date, end_date))

    return render(request, 'child_redemption_history.html', {'redemptions': redemptions, 'form': form})


@login_required
def child_completed_tasks(request):
    child = Child.objects.get(user=request.user)
    form = DateRangeForm(request.GET or None)
    tasks_with_bonus = []
    default_date = date(2201, 1, 1)  # תאריך ברירת מחדל

    if form.is_valid():
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
    else:
        start_date = None
        end_date = None

    tasks = child.tasks_completed.all()
    if start_date and end_date:
        tasks = tasks.filter(completed_date__range=(start_date, end_date))

    for task in tasks:
        completion_date = task.completed_date.date() if task.completed_date else default_date
        tasks_with_bonus.append({
            'title': task.title,
            'points': task.points,
            'completion_date': completion_date,
            'mentor': ", ".join(mentor.user.username for mentor in task.assigned_mentors.all())
        })
        if task.total_bonus_points > 0:
            tasks_with_bonus.append({
                'title': f"{task.title} - Bonus",
                'points': task.total_bonus_points,
                'completion_date': completion_date,
                'mentor': ", ".join(mentor.user.username for mentor in task.assigned_mentors.all())
            })

    return render(request, 'child_completed_tasks.html', {'tasks_with_bonus': tasks_with_bonus, 'form': form})


@login_required
def mentor_home(request):
    mentor = get_object_or_404(Mentor, user=request.user)
    tasks = Task.objects.filter(assigned_mentors=mentor)

    for task in tasks:
        if task.is_overdue():
            task.completed = True
            task.save()

    total_tasks = tasks.count()
    completed_tasks = tasks.filter(completed=True).count()
    open_tasks = total_tasks - completed_tasks
    efficiency_rate = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0

    children = []
    for child in mentor.children.all():
        completed = child.completed_tasks.count()
        assigned = child.assigned_tasks.count()
        efficiency = (completed / assigned) * 100 if assigned > 0 else 0
        performance_color = "#d4edda" if efficiency >= 75 else "#f8d7da" if efficiency < 50 else "#fff3cd"
        children.append({
            'child': child,
            'efficiency_rate': efficiency,
            'performance_color': performance_color,
        })

    context = {
        'mentor': mentor,
        'total_tasks': total_tasks,
        'open_tasks': open_tasks,
        'completed_tasks': completed_tasks,
        'efficiency_rate': efficiency_rate,
        'children': children,
        'tasks': tasks,
    }
    return render(request, 'mentor_home.html', context)

@login_required
def mentor_children_details(request):
    mentor = Mentor.objects.get(user=request.user)
    children = mentor.children.all()
    return render(request, 'mentor_children_details.html', {'children': children})

@login_required
def shop_redeem_points(request):
    id_form = IdentifyChildForm()

    if request.method == 'POST':
        if 'identifier' in request.POST:
            id_form = IdentifyChildForm(request.POST)
            if id_form.is_valid():
                identifier = id_form.cleaned_data['identifier']
                secret_code = id_form.cleaned_data['secret_code']
                try:
                    child = Child.objects.get(identifier=identifier, secret_code=secret_code)
                    child.secret_code = get_random_digits()
                    child.save()
                    shop = Shop.objects.get(user=request.user)

                    # Calculate the points used by the shop in the current month
                    now = datetime.now()
                    start_of_month = now.replace(day=1)
                    redemptions_this_month = Redemption.objects.filter(shop=shop, date_redeemed__gte=start_of_month)
                    points_used_this_month = redemptions_this_month.aggregate(total_points=Sum('points_used'))['total_points'] or 0

                    remaining_points = shop.max_points - points_used_this_month

                    rewards = Reward.objects.filter(
                        shop=shop,
                        points_required__lte=min(child.points, remaining_points)
                    )
                    if not rewards.exists():
                        return render(request, 'shop_no_rewards.html')
                    request.session['child_id'] = child.id  # Save child ID to session
                    request.session['selected_rewards'] = json.dumps([])  # Reset selected rewards
                    return render(request, 'shop_redeem_points.html', {
                        'child': child,
                        'id_form': id_form,
                        'rewards': rewards,
                        'selected_rewards': []
                    })
                except Child.DoesNotExist:
                    return render(request, 'shop_invalid_identifier.html')
        elif 'complete_transaction' in request.POST:
            child_id = request.session.get('child_id')
            if not child_id:
                return redirect('shop_redeem_points')  # Redirect if child_id is not found in session

            child = get_object_or_404(Child, id=child_id)
            shop = Shop.objects.get(user=request.user)

            # Calculate the points used by the shop in the current month
            now = datetime.now()
            start_of_month = now.replace(day=1)
            redemptions_this_month = Redemption.objects.filter(shop=shop, date_redeemed__gte=start_of_month)
            points_used_this_month = redemptions_this_month.aggregate(total_points=Sum('points_used'))['total_points'] or 0

            remaining_points = shop.max_points - points_used_this_month

            selected_rewards = request.POST.get('selected_rewards')
            selected_rewards = json.loads(selected_rewards)
            total_points = sum(r['quantity'] * r['points'] for r in selected_rewards)

            if child.points >= total_points and total_points <= remaining_points:
                points_used = 0
                for reward in selected_rewards:
                    reward_obj = get_object_or_404(Reward, id=reward['reward_id'])
                    points_used += reward['quantity'] * reward['points']
                    child.subtract_points(reward['quantity'] * reward['points'])
                    Redemption.objects.create(child=child, points_used=reward['quantity'] * reward['points'], shop=reward_obj.shop)
                request.session['selected_rewards'] = json.dumps([])
                request.session.pop('child_id', None)  # Clear child_id from session
                
                if child.user.email:
                    NotificationManager.sent_mail(f'Dear {child.user.first_name}, your redemption is complete. You have redeemed {points_used} points.', child.user.email)
                
                return render(request, 'shop_redemption_success.html', {'child': child, 'points_used': points_used, 'receipt': selected_rewards})
            else:
                return render(request, 'shop_not_enough_points.html')

    if request.method == 'GET':
        if 'child_id' in request.session:
            child_id = request.session.get('child_id')
            child = get_object_or_404(Child, id=child_id)
            shop = Shop.objects.get(user=request.user)

            # Calculate the points used by the shop in the current month
            now = datetime.now()
            start_of_month = now.replace(day=1)
            redemptions_this_month = Redemption.objects.filter(shop=shop, date_redeemed__gte=start_of_month)
            points_used_this_month = redemptions_this_month.aggregate(total_points=Sum('points_used'))['total_points'] or 0

            remaining_points = shop.max_points - points_used_this_month

            rewards = Reward.objects.filter(
                shop=shop,
                points_required__lte=min(child.points, remaining_points)
            )
            if not rewards.exists():
                return render(request, 'shop_no_rewards.html')
            selected_rewards = json.loads(request.session.get('selected_rewards', '[]'))
            return render(request, 'shop_redeem_points.html', {
                'child': child,
                'id_form': id_form,
                'rewards': rewards,
                'selected_rewards': selected_rewards
            })

    # Clear session when loading the page initially or when transaction is complete
    request.session.pop('child_id', None)
    request.session['selected_rewards'] = json.dumps([])

    return render(request, 'shop_redeem_points.html', {'id_form': id_form})


@login_required
def shop_cancel_transaction(request):
    # Clear session data related to the transaction
    request.session.pop('child_id', None)
    request.session['selected_rewards'] = json.dumps([])
    return JsonResponse({'status': 'ok'})

@login_required
def shop_home(request):
    shop = Shop.objects.get(user=request.user)
    start_of_month = now().replace(day=1)
    redemptions_this_month = Redemption.objects.filter(shop=shop, date_redeemed__gte=start_of_month)
    points_used_this_month = redemptions_this_month.aggregate(total_points=Sum('points_used'))['total_points'] or 0
    points_left_to_redeem = max(0, shop.max_points - points_used_this_month)

    context = {
        'shop': shop,
        'points_used_this_month': points_used_this_month,
        'points_left_to_redeem': points_left_to_redeem,
    }
    return render(request, 'shop_home.html', context)

def get_random_digits(n=3):
    return ''.join(str(random.randint(0, 9)) for _ in range(n))

@login_required
def mentor_completed_tasks_view(request):
    mentor = get_object_or_404(Mentor, user=request.user)
    form = DateRangeForm(request.GET or None)
    task_data = []

    if form.is_valid():
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
    else:
        start_date = None
        end_date = None

    tasks = Task.objects.filter(assigned_mentors=mentor, completed=True)
    if start_date and end_date:
        tasks = tasks.filter(deadline__range=(start_date, end_date))

    for task in tasks:
        task_info = {
            'task': task,
            'form': TaskImageForm(instance=task),
            'completed_by': task.completed_by.all(),
            'completed_count': task.completed_by.count(),
        }
        task_data.append(task_info)

    return render(request, 'mentor_completed_tasks_view.html', {'task_data': task_data, 'form': form})
@login_required
def shop_redemption_history(request):
    shop = request.user.shop
    redemptions = Redemption.objects.filter(shop=shop).order_by('-date_redeemed')
    monthly_redemptions = (
        redemptions.annotate(month=TruncMonth('date_redeemed'))
                   .values('month')
                   .annotate(total_points=Sum('points_used'))
                   .annotate(max_points=F('shop__max_points')) 
                   .order_by('-month')
    )

    last_redemptions = redemptions[:10]  # Get the last 10 redemptions

    context = {
        'shop': shop,
        'monthly_redemptions': monthly_redemptions,
        'recent_redemptions': last_redemptions,
    }
    return render(request, 'shop_redemption_history.html', context)

def rewards_view(request):
    # Prefetch related rewards to minimize database hits
    shops = Shop.objects.prefetch_related('rewards').all()

    # Get current child from request user
    child = request.user.child

    # Prepare a new list to hold shops with modified data
    shops_with_images = []
    for shop in shops:
        start_of_month = now().replace(day=1)
        redemptions_this_month = Redemption.objects.filter(shop=shop, date_redeemed__gte=start_of_month)
        points_used_this_month = redemptions_this_month.aggregate(total_points=Sum('points_used'))['total_points'] or 0
        # Assign default image if none exists
        shop_image = shop.img.url if shop.img else static('images/logo.png')
        
        # Prepare rewards, assigning default images if necessary
        rewards_with_images = [
            {
                'title': reward.title,
                'img_url': reward.img.url if reward.img else static('images/logo.png'),
                'points': reward.points_required,
                'sufficient_points': child.points >= reward.points_required
            }
            for reward in shop.rewards.all()
        ]
        
        # Append modified shop data to the list
        shops_with_images.append({
            'name': shop.name,
            'img': shop_image,
            'rewards': rewards_with_images,
            'used_points': points_used_this_month
        })

    context = {'shops': shops_with_images, 'child_points': child.points}
    return render(request, 'reward.html', context)

@login_required
def list_view(request):
    tasks = Task.objects.all()
    return render(request, 'list_tasks.html', {'tasks': tasks})

@login_required
def mentor_active_list(request):
    mentor = Mentor.objects.get(user=request.user)
    tasks = Task.objects.filter(assigned_mentors=mentor)
    return render(request, 'list_tasks.html', {'tasks': tasks})

@login_required
def child_active_list(request):
    try:
        child = Child.objects.get(user=request.user)
        tasks = Task.objects.filter(assigned_children=child, completed=False)
        tasks.update(new_task=False)
        return render(request, 'list_tasks.html', {'tasks': tasks})
    except Child.DoesNotExist:
        return render(request, 'list_tasks.html', {'error': 'You are not authorized to view this page.'})


@login_required
def mentor_task_list(request):
    current_date = timezone.now().date()
    mentor = get_object_or_404(Mentor, user=request.user)
    form = DateRangeForm(request.GET or None)
    tasks = Task.objects.filter(assigned_mentors=mentor)

    if form.is_valid():
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        tasks = tasks.filter(deadline__range=(start_date, end_date))

    return render(request, 'mentor_task_list.html', {'tasks': tasks, 'form': form})

@login_required
def assign_task(request, task_id):
    mentor = Mentor.objects.get(user=request.user)
    task = get_object_or_404(Task, id=task_id)
    children = mentor.children.all()

    if request.method == 'POST':
        selected_children_ids = request.POST.getlist('children')
        for child_id in selected_children_ids:
            child = get_object_or_404(Child, id=child_id)
            task.assigned_children.add(child)
            task.new_task = True
            task.save()
        task.assigned_mentors.add(mentor)
        messages.success(request, f"Task '{task.title}' successfully assigned to selected children.")
        return redirect('mentor_task_list')

    return render(request, 'assign_task.html', {'task': task, 'children': children})

@login_required
def assign_points(request, task_id):
    mentor = Mentor.objects.get(user=request.user)
    task = get_object_or_404(Task, id=task_id)
    children = mentor.children.filter(id__in=task.assigned_children.values_list('id', flat=True))

    if request.method == 'POST':
        selected_children_ids = request.POST.getlist('children')
        for child_id in selected_children_ids:
            child = get_object_or_404(Child, id=child_id)
            child.add_points(task.points)
            task.completed_by.add(child)
        messages.success(request, f"Points successfully assigned for task '{task.title}' to selected children.")
        return redirect('points_assigned_success', task_id=task.id)

    return render(request, 'assign_points.html', {'task': task, 'children': children})

@login_required
def points_assigned_success(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    children = task.completed_by.all()
    return render(request, 'points_assigned_success.html', {'task': task, 'children': children})
from datetime import datetime

from datetime import datetime
from django.utils import timezone

from datetime import datetime, date
from django.utils import timezone

@login_required
def child_points_history(request):
    child = Child.objects.get(user=request.user)
    form = DateRangeForm(request.GET or None)
    points_history = []
    current_points = 0
    default_date = date(2201, 1, 1)  # תאריך ברירת מחדל

    if form.is_valid():
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
    else:
        start_date = None
        end_date = None

    tasks = child.tasks_completed.all()
    if start_date and end_date:
        tasks = tasks.filter(completed_date__range=(start_date, end_date))

    for task in tasks:
        completed_date = task.completed_date.date() if task.completed_date else default_date
        current_points += task.points
        points_history.append({
            'description': f"Completed Task: {task.title}",
            'points': f"+{task.points}",
            'date': completed_date,
            'balance': current_points
        })
        if task.total_bonus_points > 0:
            current_points += task.total_bonus_points
            points_history.append({
                'description': f"Bonus Points for Task: {task.title}",
                'points': f"+{task.total_bonus_points}",
                'date': completed_date,
                'balance': current_points
            })

    redemptions = Redemption.objects.filter(child=child)
    if start_date and end_date:
        redemptions = redemptions.filter(date_redeemed__range=(start_date, end_date))

    for redemption in redemptions:
        date_redeemed = redemption.date_redeemed if redemption.date_redeemed else default_date
        current_points -= redemption.points_used
        points_history.append({
            'description': f"Redeemed: {redemption.shop.name}",
            'points': f"-{redemption.points_used}",
            'date': date_redeemed.date(),  # המרת datetime ל date
            'balance': current_points
        })

    points_history.sort(key=lambda x: x['date'])  # סידור לפי תאריך

    return render(request, 'child_points_history.html', {'points_history': points_history, 'form': form})

from teenApp.interface_adapters.repositories import ChildRepository, TaskRepository, MentorRepository
assign_bonus_points = AssignBonusPoints(
    child_repository=ChildRepository(),
    task_repository=TaskRepository(),
    mentor_repository=MentorRepository()
)

@login_required
def assign_bonus(request):
    mentor = get_object_or_404(Mentor, user=request.user)
    
    if request.method == 'POST':
        form = BonusPointsForm(mentor, request.POST)
        if form.is_valid():
            task = form.cleaned_data['task']
            child = form.cleaned_data['child']
            bonus_points = form.cleaned_data['bonus_points']
            
            if bonus_points > 10:
                return render(request, 'assign_bonus.html', {'form': form, 'error': 'Maximum of 10 bonus points per assignment is allowed.'})
            
            try:
                assign_bonus_points.execute(task.id, child.id, mentor.id, bonus_points)
                return redirect('mentor_home')
            except ValueError as e:
                return render(request, 'assign_bonus.html', {'form': form, 'error': str(e)})
    else:
        form = BonusPointsForm(mentor)
    
    return render(request, 'assign_bonus.html', {'form': form})

@login_required
def load_children(request):
    task_id = request.GET.get('task_id')
    children = Child.objects.filter(assigned_tasks=task_id).order_by('user__username')
    return JsonResponse(list(children.values('id', 'user__username')), safe=False)

from django.shortcuts import render, redirect
from .forms import TaskForm  # Assuming you have a form for Task
@login_required
def add_task(request):
    mentor = get_object_or_404(Mentor, user=request.user)

    if request.method == 'POST':
        form = TaskForm(mentor=mentor, data=request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.mentor = mentor
            task.save()
            form.save_m2m()  # Save the many-to-many data for the form
            return redirect('mentor_home')
    else:
        form = TaskForm(mentor=mentor)

    return render(request, 'add_task.html', {'form': form})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from teenApp.entities.task import Task
from teenApp.entities.mentor import Mentor

@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    mentor = get_object_or_404(Mentor, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES, instance=task, mentor=mentor)
        if form.is_valid():
            form.save()
            return redirect('mentor_task_list')  # Redirect to mentor task list or another appropriate page
    else:
        form = TaskForm(instance=task, mentor=mentor)
    return render(request, 'edit_task.html', {'form': form, 'task': task})

def points_leaderboard(request):
    children = Child.objects.all().order_by('-points')
    return render(request, 'points_leaderboard.html', {'children': children})


@login_required
def monthly_wall_of_fame(request):
    form = DateRangeMForm(request.GET or None)
    top_children = []

    if form.is_valid():
        selected_month = form.cleaned_data['month']
        top_children = MonthlyTopChild.objects.filter(month=selected_month).order_by('position')

    return render(request, 'monthly_wall_of_fame.html', {'form': form, 'top_children': top_children})

def update_monthly_top_children():
    current_date = now()
    first_day_of_current_month = current_date.replace(day=1)
    first_day_of_next_month = (first_day_of_current_month + timedelta(days=32)).replace(day=1)
    
    children = Child.objects.all().order_by('-points')[:3]
    positions = [20, 10, 5]  # בונוסים לפי מיקום

    for i, child in enumerate(children):
        MonthlyTopChild.objects.create(
            child=child,
            points=child.points,
            month=first_day_of_current_month,
            position=i + 1
        )
        child.points += positions[i]
        child.save()

@login_required
def points_leaderboard(request):
    form = DateRangeForm(request.GET or None)
    children = Child.objects.all()

    if form.is_valid():
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        
        # Calculate points within the date range
        children = children.annotate(
            points_within_range=Sum(
                Case(
                    When(tasks_completed__completed_date__range=(start_date, end_date), then='tasks_completed__points'),
                    When(redemptions__date_redeemed__range=(start_date, end_date), then=-F('redemptions__points_used')),
                    default=Value(0),
                    output_field=IntegerField()
                )
            )
        ).order_by('-points_within_range')
    else:
        children = children.order_by('-points')

    return render(request, 'points_leaderboard.html', {'children': children, 'form': form})