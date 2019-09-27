from django.shortcuts import render, redirect, HttpResponse
from core import models
from django.http import JsonResponse
from django.views import View
from django.forms import ModelForm
from django.utils.safestring import mark_safe
from django.db import transaction
import datetime
from django.db.models import Q
from copy import deepcopy
import json
from BossFind import settings
# Create your views here.


def index(request):
    if request.is_ajax():
        temp = {}
        i = 1
        data_obj = models.User.objects.all()
        for obj in data_obj:
            temp[i] = [obj.username, obj.account, obj.get_userrole_display()]
            i += 1
        return JsonResponse(temp)
    return render(request, 'index.html')


def login(request):
    errors = {"errors": ""}
    if request.method == 'POST':
        account = request.POST.get('account')
        password = request.POST.get('password')
        errors["account"] = account
        errors["password"] = password
        user = models.User.objects.filter(account=account, password=password).first()
        if user:
            role = user.userrole
            request.session['user'] = user.pk
            if role == 1:
                return redirect('/index/')
            elif role == 2:
                return redirect('/candidate_index/')
            else:
                return redirect('/company/')
        else:
            errors["errors"] = "用户名或密码错误!"
    return render(request, 'login.html', {"errors": errors})


class GetData(View):
    def get(self, request, table_name):
        fun = getattr(self, table_name)
        temp = fun(request)
        return JsonResponse(temp)

    def post(self, request, table_name):
        func = getattr(self, table_name)
        return func(request)

    def company(self, request):
        data_list = models.Company.objects.all()
        temp = {}
        i = 1
        for data in data_list:
            temp[i] = [data.user.username, data.user.account, data.companyName, data.pk]
            i += 1
        return temp

    def candidate(self, request):
        data_list = models.Candidate.objects.all()
        temp = {}
        i = 1
        for data in data_list:
            temp[i] = [data.user.username, data.user.account, data.bio, data.pk]
            i += 1
        return temp


def candidate(request):
    return render(request, 'candidate.html')


# def candidate_add(request, table_name):
#     table_name = table_name.title()
#     table_obj = getattr(models, table_name)
#
#     class Form(ModelForm):
#         class Meta:
#             model = table_obj
#             fields = "__all__"
#     form = Form()
#     if request.method == "POST":
#         form = Form(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('/index/')
#     return render(request, 'add.html', {"forms": form})


class CandidateAdd(View):
    def get(self, request, table_name):
        return getattr(self, table_name)(request)

    def position(self, request):
        if request.method == "POST":
            positionName = request.POST.get("positionName")
            models.Position.objects.create(positionName=positionName)
            return redirect("/position/")
        return render(request, "add_position.html")

    def post(self, request, table_name):
        return getattr(self, table_name)(request)

    def candidate(self, request):
        if request.method == "POST":
            account = request.POST.get('account')
            username = request.POST.get('username')
            password = request.POST.get('password')
            try:
                with transaction.atomic():
                    user = models.User.objects.create(account=account, username=username, password=password)
                    models.Candidate.objects.create(user=user)
                return redirect("/candidate/")
            except Exception as e:
                return HttpResponse("用户已存在")
        return render(request, "add candidate.html")

    def company(self, request):
        if request.method == "POST":
            companyname = request.POST.get("companyname")
            account = request.POST.get("account")
            password = request.POST.get("password")
            username = request.POST.get("username")
            try:
                with transaction.atomic():
                    user = models.User.objects.create(account=account, username=username, userrole=3, password=password)
                    models.Company.objects.create(user=user, companyName=companyname)
                return redirect("/index/")
            except Exception as e:
                return HttpResponse("用户已存在")
        return render(request, "add company.html")


def logout(request):
    request.session.clear()
    request.session.flush()
    return redirect('/login/')


def date_format(str):

    str = str.strip()
    print(str)
    if str == '':
        return None
    else:
        print([int(d) for d in str.split('-')])
        return datetime.date(*[int(d) for d in str.split('-')])


def register(request):
    if request.is_ajax():
        response = {"code": 0, "msg": ""}
        username = request.POST.get("username")
        account = request.POST.get("account")
        password = request.POST.get("password")
        email = request.POST.get('email')
        gender = request.POST.get('gender')
        finishEdu = date_format(request.POST.get('finishEdu'))
        birthday = int(request.POST.get('age')) if not request.POST.get('age') == '' else None
        tel = request.POST.get('tel')
        # position = request.POST.getlist('position')
        bio = request.POST.get("bio")
        print(request.POST)
        try:
            with transaction.atomic():
                user = models.User.objects.create(
                    username=username, account=account, password=password,
                )
                candidate = models.Candidate.objects.create(user=user, bio=bio, gender=gender, email=email, tel=tel, finishEdu=finishEdu, birthday=birthday)
                # p_list = models.Position.objects.filter(pk__in=position)
                # for position in p_list:
                #     position.
                # models.Position.objects.filter()
                # candidate.position.add(*p_list)
            response["code"] = 1
            response["msg"] = "/candidate_index/"
            request.session["user"] = user.pk
        except Exception as e:
            print(e)
            response["msg"] = "用户名已存在!"
        finally:
            return JsonResponse(response)

    position_list = models.Position.objects.all()
    return render(request, 'sign up.html', {"positions": position_list})


def candidate_index(request):
    if request.is_ajax():
        response = {"code": 1, "msg": request.path_info}
        pk = request.POST.get("pk")
        company_job_obj = models.Provide.objects.filter(pk=pk).first()
        log_obj = models.Select.objects.filter(candidate__user=request.user).count() >= 3
        if not log_obj:
            try:
                with transaction.atomic():
                    models.Select.objects.create(provide=company_job_obj, candidate=request.user.candidate)

            except Exception as e:
                response["msg"] = '请选择职位!'
                response["code"] = 0
        else:
            response["msg"] = '您填报的职位过多!'
            response["code"] = 0
        return JsonResponse(response)
    search_dict = ["position__id", "city", "companyName__icontains"]
    position_id = int(request.GET.get("position__id")) if request.GET.get("position__id") else None
    city = request.GET.get("city")
    # company_name = request.GET.get("companyName__icontains")
    # position_set = models.Position.objects.all()
    # print(position_set)
    t = []
    q = Q()
    q.connector = 'and'
    positionRequest = deepcopy(request.GET)
    cityRequest = deepcopy(request.GET)
    nameRequest = deepcopy(request.GET)
    nameRequest.pop("companyName__icontains") if nameRequest.get("companyName__icontains") else None
    positionRequest.pop("position__id") if positionRequest.get("position__id") else None
    cityRequest.pop("city") if cityRequest.get("city") else None
    if not position_id:
        # print("in")
        t.append('<div class="every-position"><a class="active" href="/candidate_index/?{0}">All</a></div>'.format(positionRequest.urlencode()))
    else:
        t.append('<div class="every-position"><a href="/candidate_index/?{0}">All</a></div>'.format(positionRequest.urlencode()))
    for key, value in request.GET.items():
        if key in search_dict:
            q.children.append((key, value))

    for position in models.Position.objects.all():
        # if request.GET.get("position__positi")
        # print(position_id, position.pk)
        if position_id == position.pk:
            # print("in")
            temp = '''<div class="every-position"><a class="active" href="/candidate_index/?position__id={2}&{1}">{0}</a></div>'''.format(
                position.positionName,
                positionRequest.urlencode(),
                position.pk
            )
        else:
            temp = '''<div class="every-position"><a href="/candidate_index/?position__id={2}&{1}">{0}</a></div>'''.format(
                position.positionName,
                positionRequest.urlencode(),
                position.pk
            )
        t.append(temp)
    city_tag = []
    if not city:
        city_tag.append('<div class="every-city"><a class="active" href="/candidate_index/?{}">All</a></div>'.format(cityRequest.urlencode()))
    else:
        city_tag.append('<div class="every-city"><a href="/candidate_index/?{}">All</a></div>'.format(cityRequest.urlencode()))
    for c_dict in models.Company.objects.values('city').distinct():
        if city == c_dict['city']:
            temp = '<div class="every-city"><a class="active" href="/candidate_index/?city={}&{}">{}</a></div>'.format(
                c_dict['city'],
                cityRequest.urlencode(),
                c_dict['city']
            )
        else:
            temp = '<div class="every-city"><a href="/candidate_index/?city={}&{}">{}</a></div>'.format(
                c_dict['city'],
                cityRequest.urlencode(),
                c_dict['city']
            )
        city_tag.append(temp)
    city_tag = mark_safe("".join(city_tag))
    selected_company_id = models.Select.objects.filter(candidate__user=request.user).values_list("provide__company_id")
    selected_company_id = [tuple_pk[0] for tuple_pk in selected_company_id]
    company_list = models.Company.objects.filter(q).exclude(pk__in=selected_company_id).distinct()
    html_list = []
    for company in company_list:
        position_list = models.Provide.objects.filter(company__id=company.pk).values('position__positionName', 'id')
        select_list = ''
        for position in position_list:
            tag = '<option class="gray" values="{1}">{0}</option>'.format(
                position.get("position__positionName"),
                position.get("id")
            )
            select_list += tag
        temp = '''<div class="each">
        <div class="each_image"><img src="{5}"/></div>
        <div class="each_content">
            <div class="comp_name"><a href="/company/detail/{6}/">{0}</a></div>
            <ul class="comp_other">
                <li>{1}</li>
                <li>{2}</li>
                <li>{3}</li>
            </ul>

            <div class="select_position">
    <select style="height: 30px;margin-top: 5px;">
        <option class="gray" value="" disabled selected>--选择职位--</option>
        {4}
    </select>
            </div>

            <div class="btn_submit"><button type="button" class="btn btn-info choose-job" style="height:30px;margin-top: 5px;"><span class="glyphicon glyphicon-ok"></span></button></div>
        </div>
    </div>'''.format(company.companyName, company.city, company.get_size_display(), company.get_type_display(), select_list, company.head, company.pk)
        html_list.append(temp)
    # print(company_list)
    html_list = mark_safe("".join(html_list))
    return render(request, 'candidate_index.html', {"company_info_html": html_list, "position_html": mark_safe("".join(t)), "formRequest": nameRequest, "city_html": city_tag})


class DeleteHook(View):
    def get(self, request, table_name, pk):
        return getattr(self, table_name)(request, pk)

    def company(self, request, pk):
        obj = models.User.objects.filter(company__id=pk).delete()
        return redirect('/index/')

    def candidate(self, request, pk):
        # print(pk)
        obj = models.User.objects.filter(candidate__id=pk).delete()
        return redirect('/candidate/')

    def position(self, request, pk):
        models.Position.objects.filter(id=pk).delete()
        return redirect('/position/')


class EditHook(View):
    def get(self, request, table_name, pk):
        return getattr(self, table_name)(request, pk)

    def post(self, request, table_name, pk):
        return getattr(self, table_name)(request, pk)

    def company(self, request, pk):
        if request.method == "POST":
            account = request.POST.get("account")
            username = request.POST.get("username")
            password = request.POST.get("password")
            company_name = request.POST.get("companyname")
            models.User.objects.filter(company__id=pk).update(
                account=account, password=password, username=username,
            )
            models.Company.objects.filter(pk=pk).update(companyName=company_name)
            return redirect("/index/")


        if request.is_ajax():
            value_dict = models.User.objects.filter(company__id=pk).values(
                'username', 'company__companyName', 'account', 'password'
            )
            return JsonResponse(value_dict[0])
        return render(request, 'edit_company.html')

    def candidate(self, request, pk):
        if request.method == "POST":
            account = request.POST.get("account")
            username = request.POST.get("username")
            password = request.POST.get("password")
            models.User.objects.filter(candidate__id=pk).update(
                account=account, password=password, username=username,
            )
            return redirect("/candidate/")

        if request.is_ajax():
            value_dict = models.User.objects.filter(candidate__id=pk).values(
                'username', 'account', 'password'
            )
            return JsonResponse(value_dict[0])
        return render(request, 'edit_candidate.html')


def candidate_detail(request):
    if request.method == "POST":
        response = {"code": 0, "msg": ""}
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get('email')
        gender = request.POST.get('gender')
        finishEdu = date_format(request.POST.get('finishEdu'))
        birthday = int(request.POST.get('age')) if not request.POST.get('age') == '' else None
        tel = request.POST.get('tel')
        # position = request.POST.getlist('position')
        bio = request.POST.get("bio")
        print(request.POST)
        print(bio)
        try:
            with transaction.atomic():
                models.Candidate.objects.filter(user=request.user).update(email=email, gender=gender, finishEdu=finishEdu, birthday = birthday, tel=tel, bio=bio)
                models.User.objects.filter(pk=request.user.pk).update(username=username, password=password)
            response["msg"] = '/candidate_index/'
            response["code"] = 1
        except Exception as e:
            response["msg"] = '出现未知错误，请重新添加'
        finally:
            return JsonResponse(response)
    if request.is_ajax():
        obj = models.User.objects.filter(pk=request.user.pk).first()
        detail = models.Candidate.objects.filter(user=obj).first()
        temp = {
            "username": obj.username,
            "password": obj.password,
            'gender': detail.gender,
            'tel': detail.tel,
            "email": detail.email,
            'finishEdu': detail.finishEdu,
            'bio': detail.bio,
            'age': detail.birthday
        }
        return JsonResponse(temp)
    return render(request, 'candidate_detail.html')


def candidate_get_select(request):
    select_list = models.Select.objects.filter(candidate__user=request.user)
    response = {"code": 1, "data": []}
    if select_list:
        data = []
        for select in select_list:
            temp = {
                "companyName": select.provide.company.companyName,
                "positionName":select.provide.position.positionName,
                "status":select.get_status_display()
            }
            data.append(temp)
        response["data"] = data
    else:
        response["code"] = 0
    return JsonResponse(response, safe=False)


class Company(View):
    def post(self, request):
        PERMISSION_FILE_SUFFIX = ["jpeg", 'png', 'jpg']
        file_obj = request.FILES.get("avatar")
        print(file_obj)
        username = request.POST.get("username")
        company_type = request.POST.get("type")
        city = request.POST.get("city")
        size = request.POST.get("size")
        desc = request.POST.get("desc")
        position = json.loads(request.POST.get("position"))[0] if request.POST.get("position") else None
        password = request.POST.get("password")
        companyName = request.POST.get("companyName")
        if not file_obj:
            models.Company.objects.filter(user=request.user).update(
                city=city, size=size, desc=desc, companyName=companyName, type=company_type
            )
        else:
            _, suffix = file_obj.name.rsplit(".", 1)
            if suffix in PERMISSION_FILE_SUFFIX:
                path = settings.os.path.join(settings.BASE_DIR, "core", "static", "images", file_obj.name)
                data_base_path = "/static/images/{}".format(file_obj.name)
                print(path)
                # path = "/core/static/images/{}".format(file_obj.name)
                with open(path, 'wb+') as f:
                    for chunk in file_obj.chunks():
                        f.write(chunk)
                models.Company.objects.filter(user=request.user).update(
                    city=city, size=size, desc=desc, companyName=companyName, head=data_base_path,
                    type=company_type
                )

        obj = models.Company.objects.filter(user=request.user).first()
        request.user.username = username
        request.user.password = password if password else None
        request.user.save()
        if not position:
            obj.position.clear()
        else:
            temp = []
            positions = models.Company.objects.filter(user=request.user).values('position')
            positions = [d['position'] for d in positions]
            for p in position:
                if int(p) in positions:
                    pass
                else:
                    temp.append(p)
            obj.position.add(*temp)
        return HttpResponse("/company/")

    def get(self, request):

        return render(request, 'company_index.html', {"get_html": self})

    def position_provide(self):
        company_provide_position = models.Company.objects.filter(user=self.request.user).first().position.all()
        provide_position = models.Position.objects.all()
        tag = []
        for position in provide_position:
            if position in company_provide_position:
                temp = "<option selected value='{}'>{}</option>".format(position.pk, position.positionName)
            else:
                temp = "<option value='{}'>{}</option>".format(position.pk, position.positionName)
            tag.append(temp)
        return mark_safe("".join(tag))

    def company_size(self):
        choices = models.Company.size_choices
        company_obj = models.Company.objects.filter(user=self.request.user).first()
        tag = []
        for item_pk, item in choices:
            if item_pk == company_obj.size:
                temp = '<option value="{}" selected>{}</option>'.format(item_pk, item)
            else:
                temp = '<option value="{}">{}</option>'.format(item_pk, item)
            tag.append(temp)
        return mark_safe("".join(tag))

    def company_type(self):
        choices = models.Company.type_choices
        company_obj = models.Company.objects.filter(user=self.request.user).first()
        tag = []
        for item_pk, item in choices:
            if item_pk == company_obj.type:
                temp = '<option value="{}" selected>{}</option>'.format(item_pk, item)
            else:
                temp = '<option value="{}">{}</option>'.format(item_pk, item)
            tag.append(temp)
        return mark_safe("".join(tag))

    def get_data(self):
        obj_list = models.Select.objects.filter(provide__company__user=self.request.user)
        dic = {"通过": [], "未通过": [], "待审核": []}
        for obj in obj_list:
            if obj.status == 1:
                dic['通过'].append(obj)
            elif obj.status == 2:
                dic['未通过'].append(obj)
            else:
                dic['待审核'].append(obj)
        return dic

    def get_select_html(self):
        data = self.get_data()
        tag = []
        for key, item in data.items():
            for obj in item:
                print(obj.status)
                temp = '''<div class="each">
        <div class="blue"></div>
        <div class="each_content">
            <div class="name"><a href="/candidate/{}/detail/" title="点击查看ta的简历">{}</a></div>
            <div class="position"><span>{}</span></div>
            '''.format(obj.candidate.pk, obj.candidate.user.username, obj.provide.position.positionName)
                if key == '待审核':
                    temp += '''<button class="choose"><a href="/candidate/ensure/{0}/"><span class="glyphicon glyphicon-heart" style="color: palevioletred;"></span></a></button>
            <button class="choose"><a href="/candidate/refuse/{0}/"><span class="glyphicon glyphicon-remove" style="color: #3a87ad;"></span></a></button>
        </div>
    </div>'''.format(obj.pk)
                else:
                    temp += '''<div class="position"><span style="font-weight: bolder;font-size: 18px;color: #3a87ad;">{}</span></div>

        </div>
    </div>'''.format(obj.get_status_display())
                tag.append(temp)
        return mark_safe("".join(tag))


def candidate_handler(request, action, select_pk):
    dic = {"ensure": 1, "refuse": 2}
    obj = models.Select.objects.filter(pk=select_pk)
    if obj and action in dic.keys():
        obj.update(status=dic.get(action, 3))
    return redirect("/company/")


class Position(View):
    def get(self, request):
        obj_list = models.Position.objects.all().prefetch_related('company_set')
        print(obj_list)
        html = []
        count = 1
        for obj in obj_list:
            temp = "<tr>"
            temp += "<td>{}</td>".format(count)
            temp += "<td>{}</td>".format(obj.positionName)
            company_list = [company.companyName for company in obj.company_set.all()]
            temp += "<td>{}</td>".format(",".join(company_list))
            temp += "<td><a href='/delete/position/{}/' class='btn btn-danger'><span class='glyphicon glyphicon-trash'></span></a></td></tr>".format(obj.pk)
            count += 1
            html.append(temp)
        html = mark_safe("".join(html))
        return render(request, 'position.html', {"table_value": html})


def companyDetail(request, pk):
    company_obj = models.Company.objects.filter(pk=pk).first()
    if company_obj:
        html = ["<div class='every-position'>{}</div>".format(obj.positionName) for obj in company_obj.position.all()]
        return render(request, 'preview_company.html', {"company": company_obj, "position_html": mark_safe("".join(html))})
    return redirect("/candidate_index/")


def candidateDetail(request, pk):
    obj = models.Candidate.objects.filter(pk=pk).select_related("user").first()
    bio = json.loads(obj.bio)
    return render(request, 'preview_candidate.html', {"obj": obj, "bio": bio})


# def get_data(request, table_name):
#     # print(table_name)
#     table_name = table_name.title()
#     table = getattr(models, table_name)
#     obj_list = table.objects.all()
#     temp = {}
#     i = 1
#     for obj in obj_list:
#         temp[i] = [obj.pk, obj.user.username]
#     return HttpResponse('ok')
