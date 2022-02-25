
def unlock_first_level_and_mission(user, course):
    from api.models import Level, UnlockedLevel, Mission, UnlockedMission
    print("====================")
    print(f"*** FOR USER '{user}' ***")
    all_levels = Level.objects.filter(course = course)
    print(f"-> Checking if levels exists in '{course}'")
    if all_levels.count() > 0:
        print("-> yes exists")
        first_level = all_levels[0]
        # Adding in UnlockLevel model
        print(f"->-> Unlocking first level '{first_level}'")
        unlocked_level_object = UnlockedLevel.objects 
        if not unlocked_level_object.filter(level = first_level, user = user).exists():
            unlocked_level_object.create(
                level = first_level,
                user = user
            )
            print(f"->-> '{first_level}' Unlocked")

            all_missions = Mission.objects.filter(level = first_level)
            print(f"->-> Checking if mission exists '{first_level}'")
            if all_missions.count() > 0:
                print("yes exists")
                first_mission = all_missions[0]

                # Adding in UnlockMission
                print(f"->->-> Unlocking first mission '{first_mission}'")
                unlocked_mission_object = UnlockedMission.objects 
                if not unlocked_mission_object.filter(mission = first_mission, user = user).exists():
                    unlocked_mission_object.create(
                        mission = first_mission,
                        user = user
                    )
                print(f"->->-> '{first_mission}' unlocked")
        else:
            print("->-> level already unlocked")
        print("====================")
        return

        print("Not mission exist")
    print("Not Level exist")
    print("====================")



def get_related_courses_mini(user, category):
    from api.models import Course
    if user.is_fee_paid:
        all_courses = Course.objects.all()
    else:
        all_courses = Course.objects.filter(available_on_free_trial = True) 
    if category:
        all_courses = all_courses.filter(category = category)
    return all_courses