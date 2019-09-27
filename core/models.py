from django.db import models
import datetime
# Create your models here.


class User(models.Model):
    username = models.CharField(max_length=32, null=False, verbose_name='真实姓名')
    account = models.CharField(max_length=32,null=False, unique=True,verbose_name='账号')
    password = models.CharField(max_length=32, null=False,verbose_name='密码')
    userrole_chocies = (
        (1, '管理员'),
        (2, '应聘者'),
        (3, '公司')
    )
    userrole = models.SmallIntegerField(choices=userrole_chocies, null=False, default=2,verbose_name='角色')

    def __str__(self):
        return self.username


class Candidate(models.Model):
    """
    应聘者表
    """
    user = models.OneToOneField(to='User', on_delete=models.CASCADE, limit_choices_to={'userrole': 2})
    gender_choices = ((1, '男'), (2, '女'))
    gender = models.SmallIntegerField(choices=gender_choices, default=1)
    birthday = models.IntegerField(default=32, null=True)
    tel = models.CharField(max_length=11, default='11111111111', null=True)
    email = models.CharField(max_length=32, default='123@qq.com', null=True)
    finishEdu = models.DateField(default=datetime.date(2012, 2, 2), null=True)
    bio = models.CharField(max_length=1024,null=True, verbose_name='简历')
    # foreign key: User


class Position(models.Model):
    positionName = models.CharField(max_length=20,null=False)


class Company(models.Model):
    user = models.OneToOneField(to='User', on_delete=models.CASCADE)
    companyName = models.CharField(max_length=20,null=False)
    position = models.ManyToManyField(to='Position', through='Provide', through_fields=('company', 'position'))
    city = models.CharField(max_length=32, null=True, default='北京')
    desc = models.CharField(max_length=1024, null=True, default='暂无简介')
    head = models.FileField(default='/static/images/default.jpeg')
    size_choices = (
        (1, '1-99人'),
        (2, '100人以上'),
        (3, '500人以上'),
        (4, '1000人以上'),
        (5, '5000人以上'),
        (6, '10000人以上'),
    )
    size = models.SmallIntegerField(choices=size_choices, null=True, default=6)
    type_choices = (
        (1, '互联网'),
        (2, '电子商务'),
        (3, '广告营销'),
        (4, '生活服务'),
        (5, '金融证券'),
    )
    type = models.SmallIntegerField(choices=type_choices, null=True, default=1)
    # foreign key: User

    def __str__(self):
        return self.companyName


class Provide(models.Model):
    """
    职位中间表
    """
    company = models.ForeignKey(to='Company', on_delete=models.CASCADE)
    position = models.ForeignKey(to='Position', on_delete=models.CASCADE)
    candidate = models.ManyToManyField(to='Candidate')
    # foreign key: Company ; Position


class Select(models.Model):
    """
    记录表
    """
    provide = models.ForeignKey(to='Provide', on_delete=models.CASCADE)
    candidate = models.ForeignKey(to='Candidate', on_delete=models.CASCADE)
    status_choices = (
        (1, '通过'),
        (2, '未通过'),
        (3, '待审核')
    )
    status = models.SmallIntegerField(choices=status_choices, default=3, null=False)
    # foreign key: Candidate ; Provide

    class Meta:
        unique_together = ("provide", "candidate")
