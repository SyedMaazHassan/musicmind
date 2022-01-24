from api.models import *
from rest_framework.authentication import BaseAuthentication
from rest_framework.response import Response
from rest_framework import exceptions
import copy
from django.urls import resolve
from api.models import *

class ApiResponse:
    def __init__(self):
        self.output_object = {
            'response': 404,
            'success': {
                'data': None,
                'message': None
            },
            'errors': None,
            'warnings': None
        }

    def unlock_first_level_mission(self, user, course):
        all_levels = Level.objects.filter(course = course)
        print("Checking if levels exists in this course")
        if all_levels.count() > 0:
            print("yes exists")
            first_level = all_levels[0]
            # Adding in UnlockLevel model
            print("Unlocking first level")
            unlocked_level_object = UnlockedLevel.objects 
            if not unlocked_level_object.filter(level = first_level, user = user).exists():
                unlocked_level_object.create(
                    level = first_level,
                    user = user
                )

                all_missions = Mission.objects.filter(level = first_level)
                print("Checking if mission exists in this level")
                if all_missions.count() > 0:
                    print("yes exists")
                    first_mission = all_missions[0]

                    # Adding in UnlockMission
                    print("Unlocking first mission")
                    unlocked_mission_object = UnlockedMission.objects 
                    if not unlocked_mission_object.filter(mission = first_mission, user = user).exists():
                        unlocked_mission_object.create(
                            mission = first_mission,
                            user = user
                        )
                    print("First mission unlocked")
                return

            print("Not mission exist")
        print("Not Level exist")

    def postSuccess(self, data, message):
        self.output_object['response'] = 200
        self.output_object['success']['data'] = data
        self.output_object['success']['message'] = message

    def postError(self, error_object):
        self.output_object['response'] = 404
        self.output_object['errors'] = error_object


class RequestAuthentication(BaseAuthentication, ApiResponse):
    def __init__(self):
        self.user_auth_list = ['CategoryApi', 'LevelApi', 'MissionApi', 'SubscriptionApi']
        ApiResponse.__init__(self)

    def authenticateApiKey(self, request):
        status = False
        message = None
        if 'api_key' not in request.headers:
            message = "API key is missing"
            return (status, message)
        try:
            API_Key.objects.get(key = request.headers['api_key'])
            status = True
        except API_Key.DoesNotExist:
            message = "Given api key is not valid or it has expired"
        except Exception as e:
            message = str(e).replace("['", '').replace("']", '')
        return (status, {'api_key': message}) 


    def authenticateUid(self, request):
        status = False
        message = None
        if 'uid' not in request.headers:
            message = "User credentials not provided in headers"
            return (status, message)
        try:
            SystemUser.objects.get(uid = request.headers['uid'])
            status = True
        except SystemUser.DoesNotExist:
            message = "User with given UID does not exist"
        except Exception as e:
            message = str(e).replace("['", '').replace("']", '')
        return (status, {'uid': message}) 


    def authenticate(self, request):
        api_check = self.authenticateApiKey(request)
        if not api_check[0]:
            self.postError(api_check[1])
            raise exceptions.AuthenticationFailed(self.output_object)

        requested_view = str(resolve(request.path_info).func.__name__)
        if requested_view in self.user_auth_list:
            user_check = self.authenticateUid(request)
            if not user_check[0]:
                self.postError(user_check[1])
                raise exceptions.AuthenticationFailed(self.output_object)

        return (True, None)