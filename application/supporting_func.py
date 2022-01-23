from application.models import *
from django.shortcuts import redirect


def validate_password_strength(value):
    """Validates that a password is as least 7 characters long and has at least
    1 digit and 1 letter.
    """
    min_length = 7

    error_list = []

    # Check password length on the password update function
    if len(value) < min_length:
        error_list.append(
            f'Password must be at least {min_length} characters long.')

    # check for digit if digit exists in password
    if not any(char.isdigit() for char in value):
        error_list.append(
            f'Password must contain at least 1 digit.')

    # check for if letter exists in the password or not
    if not any(char.isalpha() for char in value):
        error_list.append(
            f'Password must contain at least 1 letter.')

    # Showing error if exists, otherwise return True
    if len(error_list) == 0:
        return {
            'status': True,
            'value': value
        }
    else:
        return {
            'status': False,
            'value': error_list
        }


def get_company_by_admin(user_object):
    '''
        Get company object from database by filter out
        Accepts user object as input
        Search in the database
        Output the company that is associated with the 
        given user object
    '''
    try:
        # Filter query to get CompanyAdmin object
        company_admin = CompanyAdmin.objects.get(user=user_object)
        # Filter query to get Company object
        company = Company.objects.get(company_admin=company_admin)
        return company
    except:
        return redirect("logout")


def read_qr(image):
    '''
        get image as input
        read it, detect the QR code init
        and decode the QR code
        return the result
    '''
    from pyzbar import pyzbar
    try:
        qr_code = pyzbar.decode(image)[0]
        # convert into string
        data = qr_code.data.decode("utf-8")
        return data
    except:
        return False
