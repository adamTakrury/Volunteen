from django.urls import path
from teenApp.interface_adapters import views
from django.contrib.auth.models import User
from django.db import models

User.add_to_class('phone', models.CharField(unique=True, max_length=10, blank=True, null=True))

urlpatterns = [
    path('', views.home_redirect, name='home_redirect'),  # Redirects users to the appropriate home page
    path('child/', views.child_home, name='child_home'),  # Child home page
    path('mentor/', views.mentor_home, name='mentor_home'),  # Mentor home page
    path('list/', views.list_view, name='list'),  # List tasks from external API
    path('shop_redeem/', views.shop_redeem_points, name='shop_redeem_points'),  # Handle points redemption for children
    path('default_home/', views.default_home, name='default_home'),  # Default home page
    path('shop_home/', views.shop_home, name='shop_home'),  # Shop home page
    path('logout/', views.logout_view, name='logout_view'),  # Handle user logout
    path('redemption-history/', views.child_redemption_history, name='child_redemption_history'),
    path('completed-tasks/', views.child_completed_tasks, name='child_completed_tasks'),
    path('completed_tasks/', views.mentor_completed_tasks_view, name='mentor_completed_tasks'),
    path('shop_redemption_history/', views.shop_redemption_history, name='shop_redemption_history'),
    path('rewards/', views.rewards_view, name='reward'),  # List available rewards
    path('mentor/children-details/', views.mentor_children_details, name='mentor_children_details'), 
    path('mentor/active-list/', views.mentor_active_list, name='mentor_active_list'), 
    path('child/active-list/', views.child_active_list, name='child_active_list'), 
    path('mentor/assign-points/', views.assign_points, name='assign_points'),  # Assign points to children
    path('mentor/assign-points/<int:task_id>/', views.assign_points, name='assign_points'),  # Assign points to children for a specific task
    path('mentor/task-list/', views.mentor_task_list, name='mentor_task_list'),
    path('mentor/assign-task/<int:task_id>/', views.assign_task, name='assign_task'),
    path('cancel_transaction/', views.shop_cancel_transaction, name='shop_cancel_transaction'),
    path('child/points-history/', views.child_points_history, name='child_points_history'),
    path('mentor/assign-points/success/<int:task_id>/', views.points_assigned_success, name='points_assigned_success'),
    path('assign-bonus/', views.assign_bonus, name='assign_bonus'),
    path('cancel_transaction/', views.shop_cancel_transaction, name='shop_cancel_transaction'),
    path('points-leaderboard/', views.points_leaderboard, name='points_leaderboard'),
    path('mentor/edit-task/<int:task_id>/', views.edit_task, name='edit_task'),
    path('ajax/load-children/', views.load_children, name='load_children'),
    path('monthly-wall-of-fame/', views.monthly_wall_of_fame, name='monthly_wall_of_fame'),
    path('update-monthly-top-children/', views.update_monthly_top_children, name='update_monthly_top_children'),
    path('mentor/edit-task/<int:task_id>/', views.edit_task, name='edit_task'),
    path('identify-child/', views.shop_identify_child, name='shop_identify_child'),
    path('complete-transaction/', views.shop_complete_transaction, name='shop_complete_transaction'),

]
