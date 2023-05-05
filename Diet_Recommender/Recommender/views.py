from flask import Flask, request, render_template, redirect, url_for, flash, Blueprint, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from .. import db, IMAGE_DIR
from ..models import User, Profile, Information, Diet_model, Exercise_model

from werkzeug.utils import secure_filename
import random
import string
import os
import json
import pandas as pd
import pickle
import itertools
import json
from sklearn import tree
from sklearn.cluster import KMeans
from datetime import datetime, timedelta, date


Recommender = Blueprint('Recommender', __name__,
                        template_folder='templates/Recommender')

# BMI CALCULATOR


def bmi_calc(weight, height):
    bmi = round(weight/(height**2), 2)
    return bmi

# BMR CALCULATOR


def bmr_calc(weight, height, age, gender):
    if gender == 'male':
        bmr = 66.5 + (13.75 * int(weight)) + \
            (5 * int(height)) - (6.755 * int(age))
    else:
        bmr = 655.1 + (9.6 * int(weight)) + \
            (1.8 * int(height)) - (4.7 * int(age))

    return round(bmr)

# RANDOM STRING GENERATOR


def randstr():
    '''Creates a random string of alphanumeric characters.'''
    return ''.join(random.choice(string.ascii_uppercase + string.digits)
                   for _ in range(30))


@Recommender.route('/Dashboard')
def Dashboard():
    try:
        pro = Information.query.filter_by(
            user_id=current_user.id).order_by(Information.id.desc()).first()
        height = pro.height
        weight = pro.weight
        bmi = bmi_calc(weight, height)
        print("init",bmi)
        activity = pro.activity
        pro_graph = Information.query.filter_by(user_id=current_user.id)
        list_graph = []
        for i in pro_graph:
            list_graph.append([i.date_table.strftime(
                '%d-%m-%Y'), bmi_calc(i.weight, i.height)])
        if len(list_graph) == 0:
            print("your bmi is",bmi)
            return render_template('Dashboard.html', user=current_user, height=height, weight=weight, bmi=bmi, activity=activity.capitalize())
        print("your bmi is 1",bmi)
        return render_template('Dashboard.html', user=current_user, height=height, weight=weight, bmi=bmi, activity=activity.capitalize(), graph=list_graph)
    except:
        print("your bmi is 2",bmi)
        return render_template('Dashboard.html', user=current_user)


@Recommender.route('/delete')
def delete_acc():
    User.query.filter_by(id=current_user.id).delete()
    Profile.query.filter_by(user_id=current_user.id).delete()
    Information.query.filter_by(user_id=current_user.id).delete()
    Diet_model.query.filter_by(user_id=current_user.id).delete()
    Exercise_model.query.filter_by(user_id=current_user.id).delete()
    logout_user()
    db.session.commit()
    flash('Account Deleted')
    return redirect(url_for('Authentication.login'))


@Recommender.route('/delete_info')
def delete_info():
    Information.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return redirect(url_for('.History'))


@Recommender.route('/profile', methods=["GET", "POST"])
def profile():
    if request.method == "POST":
        age = request.form.get('age')
        phone = request.form.get('phone')
        gender = request.form.get('gender')
        height = request.form.get('height')
        weight = request.form.get('weight')
        activity = request.form.get('activity')
        diabetic = request.form.get('type')
        image = request.files['image']

        try:
            pro = Profile.query.filter_by(user_id=current_user.id).first()
            if age != "":
                pro.age = age
            if phone != "":
                pro.Phone = phone
            if image.filename != "":
                safefilename = secure_filename(
                    randstr() + '-' + image.filename)
                imgpath = '{}/{}'.format(IMAGE_DIR, safefilename)
                image_filename = safefilename
                image_data = image.read()
                try:
                    os.remove('{}/{}'.format(IMAGE_DIR, pro.img_filename))
                except:
                    None
                pro.img_filename = image_filename
                with open(imgpath, 'wb') as f:
                    f.write(image_data)

        except:
            profile = Profile(Phone=phone, age=age, gender=gender,
                              img_filename=image.filename, user_id=current_user.id)
            db.session.add(profile)
        try:
            info_pre = Information.query.filter_by(
                user_id=current_user.id).order_by(Information.id.desc()).first()
            if height == "":
                height = info_pre.height
            if weight == "":
                weight = info_pre.weight
        except:
            None

        date_table = datetime.today()
        info = Information(height=height, weight=weight, activity=activity,
                           Diabetic=diabetic, date_table=date_table, user_id=current_user.id)
        db.session.add(info)
        db.session.commit()
    try:
        pro = Profile.query.filter_by(user_id=current_user.id).first()
        age = pro.age
        phone = pro.Phone
        gender = pro.gender
        image_filename = pro.img_filename
        ava_pro = "available"
    except:
        ava_pro = "Not_available"

    try:
        info = Information.query.filter_by(
            user_id=current_user.id).order_by(Information.id.desc()).first()
        height = info.height
        weight = info.weight
        activity = info.activity
        diabetic = info.Diabetic
        ava_info = "available"
    except:
        ava_info = "Not_available"

    if ava_pro == "available" and ava_info == "available":
        return render_template('Profile.html', user=current_user, age=age, phone=phone, gender=gender, img_filename=image_filename, height=height, weight=weight, activity=activity, diabetic=diabetic)
    elif ava_pro == "available" and ava_info == "Not_available":
        return render_template('Profile.html', user=current_user, age=age, phone=phone, gender=gender, img_filename=image_filename)
    elif ava_pro == "Not_available" and ava_info == "available":
        return render_template('Profile.html', user=current_user, height=height, weight=weight, activity=activity, diabetic=diabetic)
    else:
        return render_template('Profile.html', user=current_user)


@Recommender.route('/Diet_download')
def Diet_download():
    return send_file('../Diet.csv',
                     mimetype='text/csv',
                     attachment_filename='Diet.csv',
                     as_attachment=True)


@Recommender.route('/Diet', methods=["GET", "POST"])
def Diet():
    if request.method == "POST":
        day = request.form.get('breakfast')
        day1 = request.form.get('breakfast1')
        today = date.today()

        try:
            data = day.split(":")
        except:
            data = []
            data1 = day1.split(":")
        try:
            if data[-1] == "today":
                try:
                    diet_table = Diet_model.query.filter(
                        Diet_model.user_id == current_user.id, Diet_model.date_table == today).first()
                    diet_table.breakfast
                    if diet_table.breakfast != "":
                        pass
                    else:
                        raise Exception
                except:
                    data = day.split(":")
                    di = Diet_model(breakfast=data[0], lunch=data[1], dinner=data[2],
                                    cal=data[3], date_table=today, user_id=current_user.id)
                    db.session.add(di)
                    db.session.commit()
        except:
            monday = data1[:4]
            tuesday = data1[4:8]
            wednesday = data1[8:12]
            thursday = data1[12:16]
            friday = data1[16:20]
            saturday = data1[20:24]
            sunday = data1[24:28]
            dictionary = [monday, tuesday, wednesday,
                          thursday, friday, saturday, sunday]
            start = date.today()
            end = (start - timedelta(days=date.today().weekday() %
                                     7)) + timedelta(days=6)
            count = 0
            for i in range(0, -(start-end).days+1):
                try:
                    diet_table = Diet_model.query.filter(
                        Diet_model.user_id == current_user.id, Diet_model.date_table == date.today()+timedelta(days=i)).first()
                    if diet_table.breakfast != "":
                        pass
                    else:
                        raise Exception
                except:
                    count += 1
            for j in range(0, count):
                di = Diet_model(breakfast=dictionary[len(dictionary)-count+j][0], lunch=dictionary[len(dictionary)-count+j][1], dinner=dictionary[len(
                    dictionary)-count+j][2], cal=dictionary[len(dictionary)-count+j][3], date_table=end-timedelta(days=count-1)+timedelta(days=j), user_id=current_user.id)
                db.session.add(di)
                db.session.commit()
    start = date.today() - timedelta(days=date.today().weekday() % 7)
    end = start + timedelta(days=6)

    total_diet = Diet_model.query.filter_by(user_id=current_user.id)
    total_diet_plan = 0
    for i in total_diet:
        total_diet_plan += 1

    week = 0
    dictionary = {"monday": "", "tuesday": "", "wednesday": "",
                  "thursday": "", "friday": "", "saturday": "", "sunday": ""}
    try:
        diet_table = Diet_model.query.filter(Diet_model.user_id == current_user.id, (
            Diet_model.date_table >= start) & (Diet_model.date_table <= end))

        for i in diet_table:
            data = [i.breakfast.replace("'", ""), i.lunch.replace(
                "'", ""), i.dinner.replace("'", "")]
            if i.date_table.strftime("%Y-%m-%d") == str(start):
                week += 1
                dictionary["monday"] = data
            if i.date_table.strftime("%Y-%m-%d") == str(start + timedelta(days=1)):
                week += 1
                dictionary["tuesday"] = data
            if i.date_table.strftime("%Y-%m-%d") == str(start + timedelta(days=2)):
                week += 1
                dictionary["wednesday"] = data
            if i.date_table.strftime("%Y-%m-%d") == str(start + timedelta(days=3)):
                week += 1
                dictionary["thursday"] = data
            if i.date_table.strftime("%Y-%m-%d") == str(start + timedelta(days=4)):
                week += 1
                dictionary["friday"] = data
            if i.date_table.strftime("%Y-%m-%d") == str(start + timedelta(days=5)):
                week += 1
                dictionary["saturday"] = data
            if i.date_table.strftime("%Y-%m-%d") == str(start + timedelta(days=6)):
                week += 1
                dictionary["sunday"] = data
        with open("Diet.csv", 'w') as file:
            file.write("*;breakfast;lunch;dinner\n")
            for i, j in dictionary.items():
                if j != "":
                    file.write(i+";"+j[0]+";"+j[1]+";"+j[2]+"\n")
                else:
                    file.write(i+"; ; ;\n")
        receipes = []
        try:
            diet_table_today = Diet_model.query.filter(
                Diet_model.user_id == current_user.id, Diet_model.date_table == date.today()).first()
            breakfast = diet_table_today.breakfast.split(",")
            lunch = diet_table_today.lunch.split(",")
            dinner = diet_table_today.dinner.split(",")

            with open("../../Dataset/recipe.csv", 'r') as file:
                lines_of = file.readlines()
                for line in lines_of:
                    array = line.split(";")
                    if array[0] in breakfast or array[0] in lunch or array[0] in dinner:
                        receipes.append([array[0], array[1]])
                while len(receipes) != 9:
                    recipe_name = []
                    with open("../../Dataset/meal.csv", 'r') as f:
                        lines = f.readlines()
                        for i in range(9-len(receipes)):
                            number = random.randrange(0, len(lines))
                            recipe_name.append(lines[number-1].split(',')[0])
                        for line in lines_of:
                            array = line.split(";")
                            if array[0] in recipe_name:
                                receipes.append([array[0], array[1]])
            return render_template('Diet.html', user=current_user, dictionary=dictionary, total=total_diet_plan, week=week, recipes=receipes)
        except:
            None

        return render_template('Diet.html', user=current_user, dictionary=dictionary, total=total_diet_plan, week=week)
    except:
        return render_template('Diet.html', user=current_user, total=total_diet_plan, week=week)


@Recommender.route('/History', methods=["GET", "POST"])
def History():
    breakfast = ""
    lunch = ""
    dinner = ""
    exercise = ""
    active = "all"
    if request.method == "POST":
        diet_date = request.form.get("diet")
        exercise_date = request.form.get("exercise")

        if diet_date != None:
            chosen = datetime.strptime(diet_date, "%Y-%m-%d")
            active = "diet"
            try:
                diet = Diet_model.query.filter(
                    Diet_model.user_id == current_user.id, Diet_model.date_table == chosen.date()).first()
                breakfast = diet.breakfast
                lunch = diet.lunch
                dinner = diet.dinner
            except:
                None
        else:
            chosen = datetime.strptime(exercise_date, "%Y-%m-%d")
            active = "exercise"
            try:
                Exercise = Exercise_model.query.filter(
                    Exercise_model.user_id == current_user.id, Exercise_model.date_table == chosen.date()).first()
                exercise = Exercise.exercises
            except:
                None
    try:
        info = Information.query.filter_by(
            user_id=current_user.id).order_by(Information.id.desc())
        return render_template('History.html', user=current_user, info=info, breakfast=breakfast, lunch=lunch, dinner=dinner, exercise=exercise, active=active)
    except:
        return render_template('History.html', user=current_user)


@Recommender.route('/About')
def About():
    return render_template('About.html', user=current_user)


@Recommender.route('/diet_algo/<day>')
def diet_algo(day):
    today = date.today()
    info = Profile.query.filter_by(
        user_id=current_user.id).order_by(Profile.id.desc()).first()
    try:
        pro = Information.query.filter_by(
            user_id=current_user.id).order_by(Information.id.desc()).first()
        height = pro.height
        weight = pro.weight
        gender = info.gender
        typei = "Type"+str(pro.Diabetic)
        age = info.age
    except:

        flash('Change Profile in profile tab')
        if day == "today":
            return {"list_diet": [""]}
        else:
            return {"list_diet_whole": [""]}

    meal = pd.read_csv(os.path.join(os.path.abspath(
        os.path.dirname(__file__)), '../../Dataset/meal.csv'))

    bmr = bmr_calc(weight, height, age, gender)
    filename = os.path.join(os.path.abspath(
        os.path.dirname(__file__)), 'finalized_model2.sav')
    kmeans = pickle.load(open(filename, 'rb'))
    cluster0_lower = 2000
    cluster0_higher = 1880
    cluster1_lower = 1389
    cluster1_higher = 1605
    cluster2_lower = 800
    cluster2_higher = 1388

    val = pd.Series([bmr])
    val = val.to_numpy()
    val = val.reshape(-1, 1)
    clu = kmeans.predict(val)[0]
    if clu == 0:
        cluster0_lower_breakfast = cluster0_lower * 0.4
        cluster0_higher_breakfast = cluster0_higher * 0.4
        cluster0_lower_lunch = cluster0_lower * 0.3
        cluster0_higher_lunch = cluster0_higher * 0.3
        cluster0_lower_dinner = cluster0_lower * 0.3
        cluster0_higher_dinner = cluster0_higher * 0.3
    if clu == 1:
        cluster0_lower_breakfast = cluster1_lower * 0.4
        cluster0_higher_breakfast = cluster1_higher * 0.4
        cluster0_lower_lunch = cluster1_lower * 0.3
        cluster0_higher_lunch = cluster1_higher * 0.3
        cluster0_lower_dinner = cluster1_lower * 0.3
        cluster0_higher_dinner = cluster1_higher * 0.3
    if clu == 2:
        cluster0_lower_breakfast = cluster2_lower * 0.4
        cluster0_higher_breakfast = cluster2_higher * 0.4
        cluster0_lower_lunch = cluster2_lower * 0.3
        cluster0_higher_lunch = cluster2_higher * 0.3
        cluster0_lower_dinner = cluster2_lower * 0.3
        cluster0_higher_dinner = cluster2_higher * 0.3

    Breakfast = []
    calories_Breakfast = []

    Lunch = []
    calories_Lunch = []

    Dinner = []
    calories_Dinner = []

    for i, (j, k) in enumerate(zip(meal["Breakfast"], meal[typei])):
        if j == 1 and k == 1:
            Breakfast.append(meal["Meals"][i])
            calories_Breakfast.append(meal["Cal/gm"][i])

    for i, (j, k) in enumerate(zip(meal["Lunch"], meal[typei])):
        if j == 1 and k == 1:
            Lunch.append(meal["Meals"][i])
            calories_Lunch.append(meal["Cal/gm"][i])

    for i, (j, k) in enumerate(zip(meal["Dinner"], meal[typei])):
        if j == 1 and k == 1:
            Dinner.append(meal["Meals"][i])
            calories_Dinner.append(meal["Cal/gm"][i])

    food_breakfast = list(itertools.combinations(calories_Breakfast, 3))

    count = 0
    all_food_breakfast = []
    for i in food_breakfast:
        if sum(i) >= cluster0_lower_breakfast and sum(i) <= cluster0_higher_breakfast:
            li = []
            count += 1
            for j in i:
                ind = calories_Breakfast.index(j)
                li.append(Breakfast[ind])

            all_food_breakfast.append(li)

    food_lunch = list(itertools.combinations(calories_Lunch, 3))
    count = 0
    all_food_lunch = []
    for i in food_lunch:
        if sum(i) >= cluster0_lower_lunch and sum(i) <= cluster0_higher_lunch:
            li = []
            count += 1
            for j in i:
                ind = calories_Lunch.index(j)
                li.append(Lunch[ind])

            all_food_lunch.append(li)

    food_dinner = list(itertools.combinations(calories_Dinner, 3))

    count = 0
    all_food_dinner = []
    for i in food_dinner:
        if sum(i) >= cluster0_lower_dinner and sum(i) <= cluster0_higher_dinner:
            li = []
            count += 1
            for j in i:
                ind = calories_Dinner.index(j)
                li.append(Dinner[ind])

            all_food_dinner.append(li)

    breaki = []
    lunchi = []
    dinneri = []

    for i in all_food_breakfast:
        cal = 0
        for food in i:
            ind = Breakfast.index(food)
            cal += calories_Breakfast[ind]

        if cal < (bmr * 0.4):

            breaki.append(i)

    for j in all_food_lunch:
        cal = 0
        for food in j:
            ind = Lunch.index(food)
            cal += calories_Lunch[ind]
        if cal < bmr * 0.3:
            lunchi.append(j)

    for k in all_food_dinner:
        cal = 0
        for food in k:
            ind = Dinner.index(food)
            cal += calories_Dinner[ind]
        if cal < (bmr * 0.3):
            dinneri.append(k)
    list_diet = []
    if day == "today":
        try:
            diet_table = Diet_model.query.filter(
                Diet_model.user_id == current_user.id, Diet_model.date_table == today).first()
            flash('Today\'s Diet Already taken')
            print(diet_table.breakfast)
            return {"list_diet": ""}
        except:
            flash('Today\'s Diet Already taken')
            for i in range(10):
                inte = random.randrange(0, len(lunchi))
                b = breaki[random.randrange(0, len(breaki))]
                l = lunchi[inte]
                d = dinneri[random.randrange(0, len(dinneri))]
                cal = 0

                for i, j, k in zip(b, l, d):
                    ind = Breakfast.index(i)
                    cal += calories_Breakfast[ind]

                    ind = Lunch.index(j)
                    cal += calories_Lunch[ind]

                    ind = Dinner.index(k)
                cal += calories_Dinner[ind]
                list_diet.append([b, l, d, cal])
            return {"list_diet": list_diet, "breakfast": list_diet[0][0]}
    else:
        try:
            week_diet = ["monday", "tuesday", "wednesday",
                         "thursday", "friday", "saturday", "sunday"]
            count = 0
            start = date.today()
            end = (start - timedelta(days=date.today().weekday() %
                                     7)) + timedelta(days=6)

            for i in range(0, -(start-end).days+1):
                try:
                    diet_table = Diet_model.query.filter(
                        Diet_model.user_id == current_user.id, Diet_model.date_table == date.today()+timedelta(days=i)).first()
                    if diet_table.breakfast != "":
                        pass
                    else:
                        raise Exception
                except:
                    count += 1
            if count != 0:
                for j in range(10):
                    list_dict1 = {}
                    for co in range(count):
                        inte = random.randrange(0, len(lunchi))
                        b = breaki[random.randrange(0, len(breaki))]
                        l = lunchi[inte]
                        d = dinneri[random.randrange(0, len(dinneri))]
                        cal = 0

                        for i, j, k in zip(b, l, d):
                            ind = Breakfast.index(i)
                            cal += calories_Breakfast[ind]

                            ind = Lunch.index(j)
                            cal += calories_Lunch[ind]

                            ind = Dinner.index(k)
                            cal += calories_Dinner[ind]

                        list_dict1[week_diet[len(
                            week_diet)-count+co]] = {"breakfast": b, "lunch": l, "dinner": d, "cal": cal}
                    list_diet.append(list_dict1)

                return {"list_diet_whole": list_diet}
            else:
                flash("Diet already taken")
                return {"list_diet_whole": ""}
        except:
            flash("Diet already taken")
            return {"list_diet_whole": ""}


@Recommender.route('/exercise_algo/<day>')
def exercise_algo(day):
    today = date.today()
    start_date = today - timedelta(days=date.today().weekday() % 7)
    end_date = (today - timedelta(days=date.today().weekday() %
                                  7)) + timedelta(days=6)
    info = Profile.query.filter_by(
        user_id=current_user.id).order_by(Profile.id.desc()).first()
    try:
        pro = Information.query.filter_by(
            user_id=current_user.id).order_by(Information.id.desc()).first()
        height = pro.height
        weight = pro.weight
        gender = info.gender
        activity = pro.activity
        age = info.age
    except:
        flash('Change Profile in profile tab')
        if day == "today":
            return {"list_diet": [""]}
        else:
            return {"list_diet_whole": [""]}

    if pro.activity == 'low':
        activity = 1
    elif pro.activity == 'medium':
        activity = 2
    else:
        activity = 0

    cal = bmr_calc(weight, height, age, gender)
    filename = os.path.join(os.path.abspath(
        os.path.dirname(__file__)), 'finalized_model.sav')
    clf = pickle.load(open(filename, 'rb'))
    predicted = clf.predict(pd.DataFrame([[age, activity, cal]], columns=[
                            'age_category', 'activity', 'cal']))[0]
    resistant = ["free weights", "normal gym training",
                 "light weight lifting", "weight machines", "heavy weight"]
    yoga = ["Mountain Pose (Tadasana)", "Raised Arms Pose (Urdhva Hastansana)", "Standing Forward Bend (Uttanasana)", "Garland Pose (Malasana)", "Lunge",
            "Plank", "Staff Pose (Dandasana)", "Seated Forward Bend (Paschimottanasana)", "Head to Knee Pose (Janu Sirsasana)", "Happy Baby (Ananda Balasana)"]
    aerobics = ["walking", "stair climbing", "jogging", "cycling",
                "kick boxing", "brisk walking", "biking", "swimming", "dancing"]
    if age > 60:
        aerobics = ["walking", "jogging", "cycling", "brisk walking"]
    exercises = []
    if day == "today":
        try:
            exercise_today = Exercise_model.query.filter(
                Exercise_model.user_id == current_user.id, Exercise_model.date_table == today).first()
            print(exercise_today.date_table)
            flash("Exercise already Suggested")
            return {"list_diet": ""}
        except:
            for i in range(10):
                exercise_list = []
                if predicted == "Resistant":
                    for j in range(2):
                        exercise_list.append(
                            resistant[random.randrange(0, len(resistant))])
                elif predicted == "Yoga":
                    for i in range(2):
                        exercise_list.append(
                            yoga[random.randrange(0, len(yoga))])
                elif predicted == "Aerobics":
                    for i in range(2):
                        exercise_list.append(
                            aerobics[random.randrange(0, len(aerobics))])
                exercises.append(exercise_list)
            return {"list_exercise": exercises}
    else:
        try:
            week_diet = ["monday", "tuesday", "wednesday",
                         "thursday", "friday", "saturday", "sunday"]
            count = 0
            for i in range(0, -(today-end_date).days+1):
                try:
                    exercise_table = Exercise_model.query.filter(
                        Exercise_model.user_id == current_user.id, Exercise_model.date_table == date.today()+timedelta(days=i)).first()
                    if exercise_table.exercises != "":
                        pass
                    else:
                        raise Exception
                except:
                    count += 1
            if count != 0:
                for j in range(10):
                    list_dict1 = {}
                    for co in range(count):
                        exercise_list = []
                        if predicted == "Resistant":
                            for j in range(2):
                                exercise_list.append(
                                    resistant[random.randrange(0, len(resistant))])
                        elif predicted == "Yoga":
                            for i in range(2):
                                exercise_list.append(
                                    yoga[random.randrange(0, len(yoga))])
                        elif predicted == "Aerobics":
                            for i in range(2):
                                exercise_list.append(
                                    aerobics[random.randrange(0, len(aerobics))])

                        list_dict1[week_diet[len(
                            week_diet)-count+co]] = exercise_list
                    exercises.append(list_dict1)
                return {"list_exercise_whole": exercises}
            else:
                flash("Exercise already taken")
                return {"list_exercise_whole": ""}
        except:
            flash("Exercise already taken")
            return {"list_exercise_whole": ""}


@Recommender.route('/Exercise', methods=["GET", "POST"])
def Exercise():
    today = date.today()
    start_date = today - timedelta(days=date.today().weekday() % 7)
    end_date = (today - timedelta(days=date.today().weekday() %
                                  7)) + timedelta(days=6)
    if request.method == "POST":
        exercise_today = request.form.get("exercise")
        exercise_week = request.form.get("exercise1")

        try:
            exercise_today = exercise_today.split(":")
        except:
            exercise_week = exercise_week.split(":")
        if exercise_today != None:
            exercise_save = Exercise_model(
                exercises=exercise_today[0], date_table=today, user_id=current_user.id)
            db.session.add(exercise_save)
            db.session.commit()
        else:
            dictionary = [exercise_week[0], exercise_week[1], exercise_week[2],
                          exercise_week[3], exercise_week[4], exercise_week[5], exercise_week[6]]
            count = 0
            for i in range(0, -(today-end_date).days+1):
                try:
                    Exercise_table = Exercise_model.query.filter(
                        Exercise_model.user_id == current_user.id, Exercise_model.date_table == date.today()+timedelta(days=i)).first()
                    Exercise_table.date_table
                except:
                    count += 1
            for j in range(0, count):
                exercise_save = Exercise_model(exercises=dictionary[len(
                    dictionary)-count+j], date_table=end_date-timedelta(days=count-1)+timedelta(days=j), user_id=current_user.id)
                db.session.add(exercise_save)
                db.session.commit()

    total_exercise = Exercise_model.query.filter_by(user_id=current_user.id)
    total_exercise_plan = 0
    for i in total_exercise:
        total_exercise_plan += 1

    week = 0
    dictionary = {"monday": "", "tuesday": "", "wednesday": "",
                  "thursday": "", "friday": "", "saturday": "", "sunday": ""}
    try:
        Exercise_table = Exercise_model.query.filter(Exercise_model.user_id == current_user.id, (
            Exercise_model.date_table >= start_date) & (Exercise_model.date_table <= end_date))

        for i in Exercise_table:
            data = [i.exercises.replace("'", " ")]
            if i.date_table.strftime("%Y-%m-%d") == str(start_date):
                week += 1
                dictionary["monday"] = data[0]
            if i.date_table.strftime("%Y-%m-%d") == str(start_date + timedelta(days=1)):
                week += 1
                dictionary["tuesday"] = data[0]
            if i.date_table.strftime("%Y-%m-%d") == str(start_date + timedelta(days=2)):
                week += 1
                dictionary["wednesday"] = data[0]
            if i.date_table.strftime("%Y-%m-%d") == str(start_date + timedelta(days=3)):
                week += 1
                dictionary["thursday"] = data[0]
            if i.date_table.strftime("%Y-%m-%d") == str(start_date + timedelta(days=4)):
                week += 1
                dictionary["friday"] = data[0]
            if i.date_table.strftime("%Y-%m-%d") == str(start_date + timedelta(days=5)):
                week += 1
                dictionary["saturday"] = data[0]
            if i.date_table.strftime("%Y-%m-%d") == str(start_date + timedelta(days=6)):
                week += 1
                dictionary["sunday"] = data[0]
        with open("Exercise.csv", 'w') as file:
            file.write("*;Exercise\n")
            for i, j in dictionary.items():
                if j != "":
                    file.write(i+";"+j+"\n")
                else:
                    file.write(i+";\n")
        
        try:
            Exercise_table_today = Exercise_model.query.filter(
                Exercise_model.user_id == current_user.id, Exercise_model.date_table == date.today()).first()
            exercise = Exercise_table_today.exercises.split(",")
            exercises = []
            with open("../../Dataset/exercise_dataset.csv", 'r') as file:
                lines_of = file.readlines()
                for line in lines_of:
                    array = line.split(";")
                    if array[0] in exercise:
                        exercises.append([array[0], array[1]])
                while len(exercises) != 9:
                    exercise_name = []
                    data = ["free weights", "normal gym training", "light weight lifting", "weight machines", "heavy weight",
                            "Mountain Pose (Tadasana)", "Raised Arms Pose (Urdhva Hastansana)", "Standing Forward Bend (Uttanasana)", "Garland Pose (Malasana)", "Lunge", "Plank", "Staff Pose (Dandasana)", "Seated Forward Bend (Paschimottanasana)", "Head to Knee Pose (Janu Sirsasana)", "Happy Baby (Ananda Balasana)"]
                    for i in range(9-len(exercises)):
                        number = random.randrange(0, len(data))
                        exercise_name.append(data[number])
                    for line in lines_of:
                        array = line.split(";")
                        if array[0] in exercise_name:
                            exercises.append([array[0], array[1]])
            return render_template('Exercise.html', user=current_user, dictionary=dictionary, total=total_exercise_plan, week=week, exercise=exercises)
        except:
            None
        return render_template('Exercise.html', user=current_user, dictionary=dictionary, total=total_exercise_plan, week=week)
    except:
        return render_template('Exercise.html', user=current_user, total=total_exercise_plan, week=week)


@Recommender.route('/Exercise_download')
def Exercise_download():
    return send_file('../Exercise.csv',
                     mimetype='text/csv',
                     attachment_filename='Exercise.csv',
                     as_attachment=True)
