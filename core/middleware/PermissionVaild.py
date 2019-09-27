from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from core import models
import re


class PermissionVaild(MiddlewareMixin):
    permission_url = ['/login/', '/register/']
    company_permission = ['company', 'ensure', 'refuse', 'logout', 'candidate']
    candidate_permission = ['logout', 'api', 'candidate_index', 'detail']
    role_dict = {2: candidate_permission, 3: company_permission}
    role_response = {2: "/candidate_index/", 3: "/company/"}

    def process_request(self, request):
        if request.path_info in self.permission_url:
            return
        pk = request.session.get("user")
        user = models.User.objects.filter(pk=pk).first()
        request.user = user
        if user and user.userrole in self.role_dict.keys():
            # print(user.userrole)
            for reg in self.role_dict[user.userrole]:
                if re.search(reg, request.path_info):
                    return
            else:
                response = redirect(self.role_response[user.userrole])
        elif not user:
            response = redirect('/login/')
        else:
            return
        return response
