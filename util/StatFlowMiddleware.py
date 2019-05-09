from user.models import Access
from datetime import timedelta
from django.utils import timezone #引入timezone模块


class StatFlowMiddleware:
    '''流量统计'''
    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request):
        #获取IP
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']

        # 这段代码其实就是执行我们的view视图
        response = self.get_response(request)

        now_time = timezone.now()
        # dt_s = now_time.date()
        # s_year = dt_s.year
        # s_month = dt_s.month
        # s_day = dt_s.day
        # s = datetime(s_year,s_month,s_day,0,0,0)
        # dt_e = (dt_s + timedelta(days=1))
        # e_year = dt_e.year
        # e_month = dt_e.month
        # e_day = dt_e.day
        # e = datetime(e_year,e_month,e_day,0,0,0)

        # 获取今天零点
        zeroToday = now_time - timedelta(hours=now_time.hour, minutes=now_time.minute, seconds=now_time.second,
                                         microseconds=now_time.microsecond)
        # 获取今天23:59:59
        lastToday = zeroToday + timedelta(hours=23, minutes=59, seconds=59)
        visit_exists = Access.objects.filter(access_ip=ip, access_time__range=[zeroToday, lastToday]).exists()

        #执行view后执行
        if response.status_code == 200:
            if not visit_exists:
                Access.objects.create(access_ip=ip, access_url=request.path, access_time=now_time)

        return  response

