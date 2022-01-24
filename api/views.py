from django.shortcuts import render
from api.serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed
from django.shortcuts import get_object_or_404
# Create your views here.
from api.models import *
from api.authentication import RequestAuthentication, ApiResponse
from api.support import beautify_errors
import copy
import json
# from rest_framework.permissions import IsAuthenticated
# from rest_framework_simplejwt.authentication import JWTAuthentication

# from rest_framework_simplejwt.tokens import RefreshToken
# import jwt


def index(request):
    return render(request, "abcc.html")
    # all_categories = Category.objects.all()
    
    # for category in all_categories:
    #     for i in range(3):
    #         new_course = Course(
    #             name = f'Course {i + 1}',
    #             category = category
    #         )
    #         new_course.save()

    #         for j in range(3):
    #             new_level = Level(
    #                 name = f'Level {j + 1}',
    #                 tagline = f"Tagline of level {j + 1}",
    #                 course = new_course
    #             )
    #             new_level.save()

    #             for k in range(3):
    #                 new_mission = Mission(
    #                     name = f'Mission {k + 1}',
    #                     level = new_level
    #                 )
    #                 new_mission.save()

                    
    #     print(category)



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

    def unlock_next_cat(self, user_obj, current_category):
        next_cat = current_category.get_next_cat()
        if next_cat:
            print("next category found")
            print("Unlocking first course...")
            all_courses = Course.objects.filter(category = next_cat)
            if all_courses.count() > 0:
                print("First course exists")
                print("Unlocking first level and mission")
                self.unlock_first_level_mission(user_obj, all_courses[0])

    def unlock_next_course(self, user_obj, current_course_obj):
        next_course = current_course_obj.get_next_course()
        if next_course:
            print("Next course found")
            print("Unlocking first level and mission")
            self.unlock_first_level_mission(user_obj, next_course)
        else:
            print("Next course not found")
            print("Unlocking next category...")
            self.unlock_next_cat(user_obj, current_course_obj.category)

    def unlock_next_level(self, user_obj, current_level_obj):
        next_level = current_level_obj.get_next_level()
        if next_level:
            print("Next level found!")
            query = UnlockedLevel.objects.filter(user = user_obj, level = next_level)
            if not query.exists():
                print("Next level unlocked")
                UnlockedLevel.objects.create(
                    level = next_level,
                    user = user_obj
                )

                all_missions = Mission.objects.filter(level = next_level)
                if all_missions.count() > 0:
                    first_mission = all_missions[0]
                    if not UnlockedMission.objects.filter(user = user_obj, mission = first_mission).exists():
                        UnlockedMission.objects.create(
                            mission = first_mission,
                            user = user_obj
                        )                    
        else:
            print("Next level not Found!")
            print("Unlocking next course...")
            self.unlock_next_course(user_obj, current_level_obj.course)

    def unlock_next_mission(self, user_obj, current_mission_obj):
        next_mission = current_mission_obj.get_next_mission()
        if next_mission:
            print("next mission FOUND...")
            # Check if not already exists
            query = UnlockedMission.objects.filter(user = user_obj, mission = next_mission)
            if not query.exists():
                UnlockedMission.objects.create(
                    mission = next_mission,
                    user = user_obj
                )
            print("Unlocked next mission")
        else:
            print("next mission not FOUND...")
            # Current mission is the last mission, its mean level is completed
            # Marking level as completed
            print("Marking this level as COMPLETED...")
            unlocked_level = UnlockedLevel.objects.get(user = user_obj, level = current_mission_obj.level)
            unlocked_level.is_completed = True
            unlocked_level.save()

            print("Unlocking next level...")
            self.unlock_next_level(user_obj, current_mission_obj.level)

    def check_access(self, mission, uid):
        user_obj = SystemUser.objects.get(uid = uid)
        query = UnlockedMission.objects.filter(
            user = user_obj,
            mission = mission
        )

        if query.exists():
            # current_level = mission.level

            # Marking mission as COMPLETED
            unlocked_mission = query[0]
            unlocked_mission.is_completed = True
            unlocked_mission.save()

            print("Unlocking next mission...")
            self.unlock_next_mission(user_obj, unlocked_mission.mission)

            # Check if all missions of current level is completed by this user
            # all_missions_of_this_level = Mission.objects.filter(level = current_level).count()
            # all_done_missions_by_user = UnlockedMission.objects.filter(is_completed = True, user = user_obj)
            # all_done_missions_of_this_level_by_user = 0
            # for done_mission in all_done_missions_by_user:
            #     if done_mission.mission.level == current_level:
            #         all_done_missions_of_this_level_by_user += 1

            # # If all missions completed, then mark this level completed
            # if all_done_missions_of_this_level_by_user == all_missions_of_this_level:
            #     unlocked_level = UnlockedLevel.objects.get(user = user_obj, level = current_level)
            #     unlocked_level.is_completed = True
            #     unlocked_level.save()
            #     # Unlocking the next mission

            return True

        return False

    def get(self, request, mission_id=None):
        if not mission_id:
            self.postError({'mission_id': 'Mission id is missing'})
            return Response(self.output_object)
        try:
            single_mission = Mission.objects.get(mission_id = mission_id) 
                        
            if not self.check_access(single_mission, request.headers['uid']):
                self.postError({'mission': 'This mission is locked'})
                return Response(self.output_object)
            
            serializer = MissionDetailSerializer(single_mission, many = False)
            self.postSuccess({'mission': serializer.data}, "Mission fetched successfully")
        except Exception as e:
            self.postError({ 'mission': str(e) })
        return Response(self.output_object)


class LevelApi(APIView, ApiResponse):
    authentication_classes = [RequestAuthentication,]

    def __init__(self):
        ApiResponse.__init__(self)

    def check_access(self, level, user_obj):
        query = UnlockedLevel.objects.filter(
            user = user_obj,
            level = level
        )
        return query.exists()

    def get(self, request, level_id=None):
        if not level_id:
            self.postError({'level_id': 'Level id is missing'})
            return Response(self.output_object)
        try:
            single_level = Level.objects.get(level_id = level_id) 
            serializer = LevelDetailSerializer(single_level, many = False)
            # Get logged in user
            user_obj = SystemUser.objects.get(uid = request.headers['uid'])

            if not self.check_access(single_level, user_obj):
                self.postError({'level': 'This level is locked'})
                return Response(self.output_object)

            # Convert data into python dictionary to process
            proper_data = json.loads(json.dumps(serializer.data))
            # Get all unlocked missions
            unlocked_missions = UnlockedMission.objects.filter(user = user_obj)

            all_missions = proper_data['missions']
            for mission_index in range(len(all_missions)):
                mission = all_missions[mission_index]
                
                mission['is_locked'] = True
                mission['is_completed'] = False
                query_test = unlocked_missions.filter(mission_id = mission['mission_id'])
                if query_test.exists():
                    mission['is_locked'] = False
                    if query_test[0].is_completed:
                        mission['is_completed'] = True

            self.postSuccess({'level': proper_data}, "Level fetched successfully")

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

            for level_index in range(len(all_levels)):
                level = all_levels[level_index]
                level['is_locked'] = True
                level['is_completed'] = False
                query_test = unlocked_levels.filter(level_id = level['level_id'])
                if query_test.exists():
                    level['is_locked'] = False
                    if query_test[0].is_completed:
                        level['is_completed'] = True

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


    def unlock_video(self, uid):
        user = SystemUser.objects.get(uid = uid)
        # Get first category
        all_cats = Category.objects.all()
        if all_cats.count() > 0:
            first_cat = all_cats[0]
            all_courses = Course.objects.filter(category = first_cat)
            if all_courses.count() > 0:
                first_course = all_courses[0]
                self.unlock_first_level_mission(user, first_course)
             

    def post(self, request, uid=None):
        try:
            data = request.data.copy()
            data['uid'] = uid
            serializer = UserSerializer(data = data)
            if serializer.is_valid():
                serializer.save()
                # Unlocking level and missions for this new user
                self.unlock_video(uid)
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

            if user_obj.email != request.data['email']:
                self.postError({'email': 'To avoid problems with future signin, Email cannot be updated'})
                return Response(self.output_object)

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
