# from ctypes import BigEndianStructure
from django.shortcuts import get_object_or_404, render, redirect
from .models import *
from django.contrib import messages
from django.http import HttpResponse, request
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required
from django.conf import settings
import os
# from pyzbar import pyzbar
from PIL import Image
from django.db.models import Q
import datetime
from django.core.paginator import Paginator
from .supporting_func import *
from api.models import *

def index(request):

    all_categories = Category.objects.all()
    
    for category in all_categories:
        for i in range(3):
            new_course = Course(
                name = f'Course {i + 1}',
                category = category
            )
            new_course.save()

            for j in range(3):
                new_level = Level(
                    name = f'Level {j + 1}',
                    tagline = f"Tagline of level {j + 1}",
                    course = new_course
                )
                new_level.save()

                for k in range(3):
                    new_mission = Mission(
                        name = f'Mission {k + 1}',
                        level = new_level
                    )
                    new_mission.save()

                    
        print(category)

    return render(request, "abcc.html")

# View function to update the user status of Activate/De-activate
@login_required
def update_employee_status(request):
    output = {
        'status': False,
        'message': None
    }

    company_admin = request.user
    company = get_company_by_admin(company_admin)

    # check if company is right
    if company:
        id = request.GET['id']
        is_active = request.GET['is_active']
        # Get empoyee from DB
        employee = get_object_or_404(Employee, id=id)
        if employee.company == company:
            # Check and changing status
            if is_active == 'true':
                employee.activate()
            else:
                employee.de_activate()
            employee.save()
            output['status'] = True
            output['message'] = "Record has been updated"

    # Returning output
    return JsonResponse(output)


# View function to change password
@login_required
def change_password(request):
    context = {
        "name": "change-password",
        "error": None
    }

    if request.method == "POST":
        # Get form submission
        old_password = request.POST['old_password']
        new_password = request.POST['new_password']
        new_confirm_password = request.POST['new_confirm_password']
        checkbox_check = False

        if 'checkbox_check' in request.POST:
            checkbox_check = request.POST['checkbox_check']
            if checkbox_check == "on":
                checkbox_check = True

        context['checked'] = checkbox_check
        context['old_password'] = old_password
        context['new_password'] = new_password
        context['new_confirm_password'] = new_confirm_password

        # Checking old password if user enters correct one or not
        if request.user.check_password(old_password):
            if new_password == new_confirm_password:
                # Validating password strength by our custom function
                password_validation = validate_password_strength(new_password)

                # Show status of password
                if password_validation['status']:
                    if old_password == new_password:
                        context['error'] = "Old password and new password can't be same!"
                    else:
                        # Set password if validation went right
                        request.user.set_password(new_password)
                        request.user.save()
                        messages.info(
                            request, "Your password has been changed successfully!")
                        return redirect("logout")
                else:
                    context['password_validation'] = password_validation
            else:
                context['error'] = "New password and confirm password doesn't match!"
        else:
            context['error'] = "Old password is invalid!"

    # Render template after changing the password successfully!
    return render(request, "change_password.html", context)


# View function to check email
def check_user_email(request):
    '''Check user email, weather user email exists in our record
       or not and give proper output'''
    output = {
        'status': False
    }
    try:
        if request.method == "GET" and request.is_ajax() and 'email' in request.GET:
            # Get email input through ajax request
            email = request.GET['email']
            if email:
                query = User.objects.filter(
                    email=email) | User.objects.filter(username=email)
                if query.exists():
                    # Return output
                    output['status'] = True
                    output['message'] = "Email exists!"
                else:
                    output['message'] = "Given email is not registered in our records!"
    except Exception as e:
        output['message'] = str(e)

    return JsonResponse(output)


# View function for logout
def logout(request):
    auth.logout(request)
    return redirect("index")


# View function for rendering the dashboard
@login_required
def dashboard(request):
    context = {
        "name": "dashboard"
    }

    # DUMMY code to add multiple employee at once (for testing)
    '''
    employee = ['Syed Maaz', 'Hassan', 'Sales manager', 'abc',
                'Special', datetime.datetime(2000, 1, 1).date()]

    for i in range(0, 25):
        email = f"hafiz{i}@gmail.com"
        phone = f"031346546{i}"
        telephone = f"021346546{i}"
        company = get_company_by_admin(request.user)
        new_employee = Employee(
            first_name=employee[0],
            last_name=employee[1],
            email=email,
            designation=employee[2],
            phone=phone,
            birthday=employee[5],
            company=company,
            telephone=telephone,
            projects=employee[3],
            specialized_in=employee[4]
        )
        new_employee.save()
    '''

    return render(request, "index.html", context)


# View function to delete the employee
@login_required
def delete_employee(request, id):
    try:
        # Getting employee from DB
        employee = Employee.objects.get(id=id)
        company = get_company_by_admin(request.user)
        if employee.company == company:
            employee.de_activate()
            employee.save()
            messages.info(request, "Employee has been deleted successfully!")
        else:
            raise ValueError(
                "This employee doesn't belong to your company, you can't delete it!")
    except Exception as e:
        messages.error(request, str(e))

    return redirect("index")


# View function to submit QR code
@login_required
def upload_qr_code(request):
    if request.method == "POST":
        qr_code = request.FILES['upload_qr_input']

        # saving into a model to save file in the folder
        new_scan = Scan(my_file=qr_code)
        new_scan.save()

        # getting base path
        BASE_DIR = settings.BASE_DIR
        # Making full path of the file
        file_path = os.path.join(BASE_DIR, "media", str(new_scan.my_file))
        # Calling a function which is using pyzbar
        # to detect and scan qr code
        image = Image.open(file_path)
        qr_content = read_qr(image)

        # printing the value of QR code
        if qr_content and len(qr_content) > 0:
            try:
                scanned_url = qr_content
                # for verification
                employee_id = scanned_url.split("/")[-1]

                query = Employee.objects.filter(id=employee_id)
                if query.exists():
                    employee = query[0]
                    company = get_company_by_admin(request.user)
                    if employee.company == company:

                        new_scan.delete()
                        os.remove(file_path)

                        return redirect(scanned_url)

                        # return redirect(f"/employee/{employee.id}/1")
                    else:
                        messages.error(
                            request, "Since this employee doesn't belong to your company, you can't acccess this profile!")
                else:
                    messages.error(
                        request, "No employee exists with this QR code!")

            except Exception as e:
                messages.error(request, str(e))
        else:
            messages.error(
                request, "QR code not detected in the image OR picture is very unclear!")

        return redirect("index")

    return redirect("login")


# View function for all employee page
@login_required
def all_employees(request):
    all_employees = []
    try:
        # Get company by admin
        company = get_company_by_admin(request.user)
        previous = next = None
        view = request.GET.get('view')
        search_query = request.GET.get('query')
        page = request.GET.get('page')

        # Handling which type of employees should be shown
        if not view:
            all_employees = Employee.objects.filter(company=company)
        else:
            if view == 'all':
                all_employees = Employee.objects.filter(company=company)
            elif view == 'active':
                all_employees = Employee.objects.filter(
                    company=company, is_deleted=False, is_active=True)
            elif view == 'in-active':
                all_employees = Employee.objects.filter(
                    company=company, is_deleted=True, is_active=False)
            else:
                all_employees = Employee.objects.filter(company=company)

        # Handling page number
        if not page:
            page = 1

        # Handling search query and search in DB
        if search_query:
            search_query = search_query.strip()
            filtered_records = all_employees.filter(
                Q(first_name__icontains=search_query) | Q(last_name__icontains=search_query) | Q(
                    email__icontains=search_query) | Q(designation__icontains=search_query) | Q(phone__icontains=search_query)
            )
            filtered_records = filtered_records.filter(company=company)

            all_employees = filtered_records
        else:
            all_employees = all_employees

        # Making pagination
        paginator = Paginator(all_employees, 10)
        focused_page = paginator.page(page)
        page = int(page)

        if focused_page.has_next():
            next = int(page) + 1

        if focused_page.has_previous():
            previous = int(page) - 1

        # Posting results of pagination
        all_employees = paginator.get_page(page)
        all_employees = list(all_employees.object_list)[::-1]
        page_range = list(paginator.page_range)

    except Exception as e:
        messages.error(
            request, "Page with given filter didn't have any records!")
        return redirect("all-employees")

    # preparing data to send to frontend
    context = {
        "name": "all-employees",
        "company": company,
        "previous": previous,
        "next": next,
        "focused_page": None,
        "num_pages": page_range,
        "length": len(page_range),
        "current_page": page,
        "all_employees": all_employees
    }

    return render(request, "all-employees.html", context)


# View function to save employee
@ login_required
def save_employee(request):
    if request.method == "POST":
        # Get form submission
        profile_picture = None
        is_active = False
        telephone = None
        if 'profile_picture' in request.FILES:
            profile_picture = request.FILES['profile_picture']
        if 'is_active' in request.POST:
            is_active = True
        if 'telephone' in request.POST:
            telephone = request.POST['telephone']

        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone = request.POST['phone']
        designation = request.POST['designation']
        department = request.POST['department']
        projects = request.POST['projects']
        specialized_in = request.POST['specialized_in']

        # Get current admin
        current_admin = CompanyAdmin.objects.get(user=request.user)
        # Get current company
        company = Company.objects.get(company_admin=current_admin)

        # Check if this user has already been created
        query = Employee.objects.filter(
            email=email,  company=company) | Employee.objects.filter(phone=phone, company=company)

        if query.count() == 0:
            # Creating new employee
            new_employee = Employee(
                first_name=first_name,
                last_name=last_name,
                email=email,
                designation=designation,
                phone=phone,
                department=department,
                company=company,
                is_active=is_active,
                projects=projects,
                specialized_in=specialized_in
            )
            if profile_picture:
                new_employee.profile_picture = profile_picture
            if telephone:
                new_employee.telephone = telephone

            # Save
            new_employee.save()
            messages.info(request, "New employee has been registered!")
        else:
            messages.error(request, "This employee already exists!")

        return redirect("/all-employees/")

    return redirect("login")


# View function to update employee
@ login_required
def update_employee(request):
    return redirect("login")


# View function to render single employee profile
def single_employee(request, id):
    # Check if coming request is authenticated
    if request.user.is_authenticated:
        if request.method == "POST":
            # Update employee form
            if id and len(id) > 0:
                employee = Employee.objects.filter(id=id)
                if employee.exists():
                    employee = employee[0]

                    company = get_company_by_admin(request.user)
                    if employee.company == company:

                        if 'profile_picture' in request.FILES and request.FILES['profile_picture']:
                            employee.profile_picture = request.FILES['profile_picture']
                        is_active = False
                        telephone = None
                        is_deleted = True

                        if 'is_active' in request.POST:
                            employee.activate()
                        else:
                            employee.de_activate()

                        if 'telephone' in request.POST:
                            employee.telephone = request.POST['telephone']

                        # Updating all the details of the database
                        employee.first_name = request.POST['first_name']
                        employee.last_name = request.POST['last_name']
                        employee.email = request.POST['email']
                        employee.phone = request.POST['phone']
                        employee.designation = request.POST['designation']
                        employee.department = request.POST['department']
                        employee.projects = request.POST['projects']
                        employee.specialized_in = request.POST['specialized_in']
                        employee.save()

                        messages.info(
                            request, "Employee info has been updated successfully!")
                    else:
                        messages.error(
                            request, "This employee doesn't belong to your company!")
                else:
                    messages.error(request, "No employee exists with this id!")
            else:
                messages.error(request, "Invalid id!")

            return redirect(f"/employee/{id}")

    context = {
        "employee": None,
        "index": 1
    }
    # Getting requested employee profile
    employee = Employee.objects.filter(id=id)

    if employee.exists():
        employee = employee[0]
        context['employee'] = employee

    # Rendering the profile version based on
    # the authenticated or not authenticated request
    if request.user.is_authenticated:
        return render(request, "profile.html", context)
    else:
        return render(request, "temp-profile.html", context)


# View function to edit the company details
@ login_required
def edit_company_details(request):
    company = get_company_by_admin(request.user)
    if request.method == "POST":
        try:
            # Get form submission of the edit company details
            name = request.POST['name']
            tagline = request.POST['tagline']
            description = request.POST['description']
            founded_in = request.POST['founded_in']
            error_message = "Kindly provide valid values for all fields!"
            # Checking which parameters needs to be changed
            if name:
                company.name = name
            else:
                raise ValueError(error_message)
            if tagline:
                company.tagline = tagline
            else:
                raise ValueError(error_message)
            if description:
                company.description = description
            else:
                raise ValueError(error_message)
            if founded_in:
                company.founded_in = founded_in
            else:
                raise ValueError(error_message)

            # Get template input separately to test
            if 'template_input' in request.POST and request.POST['template_input']:
                template_id = request.POST['template_input']
                template_query = CardTemplate.objects.filter(id=template_id)
                if template_query.exists():
                    template = template_query[0]
                    company.card_template = template

            company.save()
            messages.info(
                request, "Company information has been updated successfully!")
        except Exception as e:
            messages.error(request, "Provide the valid information!")

        return redirect("edit-company-details")

    # Data preparation to send to the frontend
    context = {
        "name": "edit-company-details"
    }
    context['card_templates'] = CardTemplate.objects.all()
    context['company'] = company
    return render(request, "edit-company-details.html", context)


# View functions not in use right now
'''
def buttons(request):
    return render(request, "buttons.html")


def dropdowns(request):
    return render(request, "dropdowns.html")


def typography(request):
    return render(request, "typography.html")


def basic_elements(request):
    return render(request, "basic_elements.html")


def chartjs(request):
    return render(request, "chartjs.html")


def basictable(request):
    return render(request, "basic-table.html")


def icons(request):
    return render(request, "mdi.html")
'''

# View function to login the user after
# Validation


def login(request):
    if request.user.is_authenticated:
        return redirect("index")

    if request.method == "POST":
        # GET form submission
        email = request.POST['email']
        password = request.POST['password']
        context = {
            'email': email,
            'password': password
        }
        user = auth.authenticate(username=email, password=password)
        if user is not None:
            # Log the user in, if credentials are correct
            auth.login(request, user)

            redirection = request.POST['redirection']
            if redirection and len(redirection) > 0:
                return redirect(redirection)
            else:
                return redirect("index")
        else:
            # Through error
            messages.error(request, "Incorrect login details!")
            return render(request, "login.html", context)
            # return redirect("login")
    else:
        return render(request, "login.html")


# View functions not in use right now
'''
def register(request):
    return render(request, "register.html")


def error_404(request):
    return render(request, "error-404.html")


def error_500(request):
    return render(request, "error-500.html")


def documentation(request):
    return render(request, "documentation.html")


def profile(request):
    return render(request, "profile.html")
'''
