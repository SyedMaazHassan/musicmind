from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    # path('', views.index, name="index"),
    # path('all-employees/', views.all_employees, name="all-employees"),
    # path('employee/<id>', views.single_employee, name="employee"),
    # path('delete-employee/<id>', views.delete_employee, name="delete-employee"),
    # path('edit-company-details/', views.edit_company_details,
    #      name="edit-company-details"),
    # path('upload-qr-code', views.upload_qr_code, name="upload-qr-code"),
    # path('save-employee', views.save_employee, name="save-employee"),
    # # path('login', views.login, name="login"),
    # path('logout/', views.logout, name="logout"),
    # path('dashboard/', views.dashboard, name="dashboard"),
    # path('buttons/', views.buttons, name="buttons"),
    # path('dropdowns/', views.dropdowns, name="dropdowns"),
    # path('typography/', views.typography, name="typography"),
    # path('basic_elements/', views.basic_elements, name="basic_elements"),
    # path('chartjs/', views.chartjs, name="chartjs"),
    # path('basictable/', views.basictable, name="basictable"),
    # path('icons/', views.icons, name="icons"),
    # path('login/', views.login, name="login"),
    # path('register', views.register, name="register"),
    # path('profile', views.profile, name="profile"),
    # path('error_404', views.error_404, name="error_404"),
    # path('error_500', views.error_500, name="error_500"),
    # path('documentation', views.documentation, name="documentation"),
    # path('reset_password/', auth_views.PasswordResetView.as_view(
    #     template_name='password_reset.html'), name='reset_password'),
    # path('reset_password_done/', auth_views.PasswordResetDoneView.as_view(
    #     template_name='password_reset_sent.html'), name='password_reset_done'),
    # path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
    #     template_name='password_reset_form.html'), name='password_reset_confirm'),
    # path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(
    #     template_name='password_reset_done.html'), name='password_reset_complete'),
    # path('check_user_email', views.check_user_email, name="check_user_email"),
    # path('change-password/', views.change_password, name="change-password"),
    # path('update-employee-status', views.update_employee_status,
    #      name="update-employee-status"),



]

urlpatterns = urlpatterns + \
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
