from django.shortcuts import render
from api.serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed
from django.shortcuts import get_object_or_404
# Create your views here.
from application.models import *
from api.models import *
from api.authentication import RequestAuthentication, ApiResponse
from api.support import beautify_errors
import copy
# from rest_framework.permissions import IsAuthenticated
# from rest_framework_simplejwt.authentication import JWTAuthentication

# from rest_framework_simplejwt.tokens import RefreshToken
# import jwt


def index(request):
    return render(request, "test.html")


class SubscriptionApi(APIView, ApiResponse):
    authentication_classes = [RequestAuthentication,]

    def __init__(self):
        ApiResponse.__init__(self)

    def get_multiple_subscriptions(self):
        all_subs = Subscription.objects.all()
        serializer = SubscriptionSerializer(all_subs, many=True)
        return {'subscriptions': serializer.data}

    def get_single_subscription(self, subs_id):
        single_sub = get_object_or_404(Subscription, subs_id = subs_id)
        serializer = SubscriptionSerializer(single_sub, many=False)
        return {'subscription': serializer.data}

    def get(self, request, subs_id=None):
        try:
            if subs_id:
                serialized_data = self.get_single_subscription(subs_id)
            else:
                serialized_data = self.get_multiple_subscriptions()
            self.postSuccess(serialized_data, "Subscriptions fetched successfully")
        except Exception as e:
            self.postError({ 'subscription': str(e) })
        return Response(self.output_object)

    


class MissionApi(APIView, ApiResponse):
    authentication_classes = [RequestAuthentication,]

    def __init__(self):
        ApiResponse.__init__(self)

    def get(self, request, mission_id=None):
        if not mission_id:
            self.postError({'mission_id': 'Mission id is missing'})
            return Response(self.output_object)
        try:
            single_mission = Mission.objects.get(mission_id = mission_id) 
            serializer = MissionDetailSerializer(single_mission, many = False)
            self.postSuccess({'mission': serializer.data}, "Mission fetched successfully")
        except Exception as e:
            self.postError({ 'mission': str(e) })
        return Response(self.output_object)


class LevelApi(APIView, ApiResponse):
    authentication_classes = [RequestAuthentication,]

    def __init__(self):
        ApiResponse.__init__(self)

    def get(self, request, level_id=None):
        if not level_id:
            self.postError({'level_id': 'Level id is missing'})
            return Response(self.output_object)
        try:
            single_level = Level.objects.get(level_id = level_id) 
            serializer = LevelDetailSerializer(single_level, many = False)
            self.postSuccess({'level': serializer.data}, "Level fetched successfully")
        except Exception as e:
            self.postError({ 'level': str(e) })
        return Response(self.output_object)


class CategoryApi(APIView, ApiResponse):
    authentication_classes = [RequestAuthentication,]

    def __init__(self):
        ApiResponse.__init__(self)

    def get_multiple_categories(self):
        all_categories = Category.objects.all()
        serializer = CategoryShortSerializer(all_categories, many=True)
        return {'categories': serializer.data}


    def get_single_category(self, cat_id, user_obj):
        single_cat = get_object_or_404(Category, cat_id = cat_id)
        serializer = CategoryDetailedSerializer(single_cat, many=False)
        proper_data = json.loads(json.dumps(serializer.data))
        # print(proper_data)
        unlocked_levels = UnlockedLevel.objects.filter(user = user_obj)

        all_courses = proper_data['courses']
        for course_index in range(len(all_courses)):
            course = all_courses[course_index]
            all_levels = course['levels']
            # print("=========================")
            # print("Course =>", course['name'])
            for level_index in range(len(all_levels)):
                level = all_levels[level_index]
                level['is_locked'] = True
                level['is_completed'] = False
                query_test = unlocked_levels.filter(level_id = level['level_id'])
                if query_test.exists():
                    level['is_locked'] = False
                    if query_test[0].is_completed:
                        level['is_completed'] = True
                # course['levels'][level_index] = level            
            # all_courses[course_index] = course
        # proper_data['courses'] = all_courses
        # print("=========================")
        return {'category': proper_data}

    def get(self, request, cat_id=None):
        try:
            if cat_id:
                user_object = SystemUser.objects.get(uid = request.headers['uid'])
                serialized_data = self.get_single_category(cat_id, user_object)
            else:
                serialized_data = self.get_multiple_categories()
            self.postSuccess(serialized_data, "Category(s) fetched successfully")
        except Exception as e:
            self.postError({ 'cat': str(e) })
        return Response(self.output_object)


class UserApi(APIView, ApiResponse):
    authentication_classes = [RequestAuthentication]
    def __init__(self):
        ApiResponse.__init__(self)

    def post(self, request, uid=None):
        try:
            data = request.data.copy()
            data['uid'] = uid
            serializer = UserSerializer(data = data)
            if serializer.is_valid():
                serializer.save()
                self.postSuccess({'user': serializer.data}, "User added successfully")
            else:
                self.postError(beautify_errors(serializer.errors))                 
        except Exception as e:
            self.postError({ 'uid': str(e) })
        return Response(self.output_object)

    def get(self, request, uid=None):
        try:
            if not uid:
                raise Exception("UID is missing")
            user = get_object_or_404(SystemUser, uid=uid)
            serializer = UserSerializer(user, many = False)
            self.postSuccess({'user': serializer.data}, "User fetched successfully")
        except Exception as e:
            self.postError({ 'uid': str(e) })
        return Response(self.output_object)

    def patch(self, request, uid=None):
        try:
            user_obj = get_object_or_404(SystemUser, uid=uid)
            serializer = UserSerializer(user_obj, data=request.data, partial = True)
            if serializer.is_valid():
                serializer.save()
                self.postSuccess({'user': serializer.data}, "User updated successfully")
            else:
                self.postError(beautify_errors(serializer.errors))                 
        except Exception as e:
            self.postError({ 'uid': str(e) })
        return Response(self.output_object)

    # def post(self, request, uid):



class AddUserApi(APIView):
    def post(self, request):
        api_key_check = check_api_key(request)
        if api_key_check['status']:
            return api_key_check['response']
        else:
            output = api_key_check['output']

        serializer = UserSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            output['message'] = "User is saved successfully!"
            output['data'] = serializer.data
        else:
            output['status'] = 404
            output['message'] = "Something went wrong!"
            output['errors'] = serializer.errors

        return Response(output)



class GetScriptApi(APIView):
    # authentication_process = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        api_key_check = check_api_key(request)
        if api_key_check['status']:
            return api_key_check['response']
        else:
            output = api_key_check['output']

        if id:
            try:
                script = get_object_or_404(Script, id=id)
                serializer = ScriptSerializer(script, many = False)
                output["data"] = serializer.data
                output["status"] = True
                    
            except Exception as e:
                output["status"] = False
                output["errors"] = [str(e)]            
        else:

            script = Script.objects.all()
            serializer = AllScriptSerializer(script, many=True)

            output["data"] = serializer.data
            if script.count() == 0:
                output["message"] = "No script exists"
            else:
                output["message"] = ""

        return Response(output)


# class GetEmployeeApi(APIView):
#     def get(self, request):
#         output = {}
#         is_deleted = request.data['is_deleted']
#         if is_deleted and is_deleted == "true":
#             all_employees = Employee.objects.filter(
#                 is_deleted=True, is_active=False)
#         else:
#             all_employees = Employee.objects.filter(
#                 is_deleted=False, is_active=True)

#         # Getting students
#         # Serializing -> converting to JSON
#         serializer = EmployeeSerializer(all_employees, many=True)
#         output['status'] = 200
#         output['payload'] = serializer.data
#         return Response(output)


# class SaveEmployeeApi(APIView):
#     def post(self, request):
#         output = {}
#         data = request.data

#         # Creating record
        # serializer = EmployeeSerializer(data=data)

        # if serializer.is_valid():
        #     serializer.save()
        #     output['status'] = 200
        #     output['message'] = "Employee is saved successfully!"
        #     output['details'] = serializer.data
        # else:
        #     output['status'] = 403
        #     output['message'] = "Something went wrong!"
        #     output['errors'] = serializer.errors

        # return Response(output)


# class UpdateEmployeeApi(APIView):
#     def update_details(self, request, partial=False):
#         output = {
#             'status': 403,
#             'message': "Request failed"
#         }
#         try:
#             id = request.data['id']
#             print(id)
#             student = Employee.objects.get(id=id)
#             if partial:
#                 serializer = EmployeeSerializer(
#                     instance=student, data=request.data, partial=True)
#             else:
#                 serializer = EmployeeSerializer(
#                     instance=student, data=request.data)
#             if serializer.is_valid():
#                 serializer.save()
#                 output['status'] = 200
#                 output['message'] = "Employee record updated successfully!"
#                 output['details'] = serializer.data
#             else:
#                 output['errors'] = serializer.errors
#         except Exception as e:
#             output['errors'] = str(e)

#         return output

#     def patch(self, request):
#         output = self.update_details(request, True)
#         return Response(output)

#     def put(self, request):
#         output = self.update_details(request, False)
#         return Response(output)


# class DeleteEmployeeApi(APIView):
#     def delete(self, request):
#         output = {}
#         print(request.data['id'])
#         try:
#             id = request.data['id']
#             employee = Employee.objects.get(id=id)
#             serializer = EmployeeSerializer(instance=employee, many=False)
#             employee.is_active = False
#             employee.is_deleted = True
#             employee.save()
#             output['status'] = 200
#             output['message'] = "Employee has been deleted!"
#             output['details'] = serializer.data
#         except Exception as e:
#             output['status'] = 200
#             output['message'] = "Request failed!"
#             output['details'] = str(e)

#         return Response(output)


# class UndeleteEmployeeApi(APIView):
#     def post(self, request):
#         output = {}
#         id = request.data['id']
#         try:
#             id = request.data['id']
#             employee = Employee.objects.get(id=id)
#             serializer = EmployeeSerializer(instance=employee, many=False)
#             employee.is_active = True
#             employee.is_deleted = False
#             employee.save()
#             output['status'] = 200
#             output['message'] = "Employee has been undeleted and active now!"
#             output['details'] = serializer.data
#         except Exception as e:
#             output['status'] = 200
#             output['message'] = "Request failed!"
#             output['details'] = str(e)

#         return Response(output)


# class GetCompanyApi(APIView):
#     def get(self, request):
#         output = {}
#         if 'id' in request.data:
#             id = request.data['id']
#             company = get_object_or_404(Company, id=id)
#             print(company)
#             # Serializing -> converting to JSON
#             serializer = CompanySerializer(company, many=False)
#             output['status'] = 200
#             output['payload'] = serializer.data
#         else:
#             output['status'] = 403
#             output['message'] = "Company ID is required!"

#         return Response(output)


# class UpdateCompanyApi(APIView):
#     def update_details(self, request, partial=False):
#         output = {
#             'status': 403,
#             'message': "Request failed"
#         }
#         try:
#             id = request.data['id']
#             student = Company.objects.get(id=id)
#             if partial:
#                 serializer = CompanySerializer(
#                     instance=student, data=request.data, partial=True)
#             else:
#                 serializer = CompanySerializer(
#                     instance=student, data=request.data)
#             if serializer.is_valid():
#                 serializer.save()
#                 output['status'] = 200
#                 output['message'] = "Company record updated successfully!"
#                 output['details'] = serializer.data
#             else:
#                 output['errors'] = serializer.errors
#         except Exception as e:
#             output['errors'] = str(e)

#         return output

#     def patch(self, request):
#         output = self.update_details(request, True)
#         return Response(output)

#     def put(self, request):
#         output = self.update_details(request, False)
#         return Response(output)
