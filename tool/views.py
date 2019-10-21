from django.views import View
from django.http import JsonResponse  # 用于返回JSON数据
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

import subprocess

import logging


logger = logging.getLogger('qmpython')

class CompileView(View):

    sys_modules = ['os', 'sys', 'platform', 'socket', 'CGIHTTPServer', 'BaseHTTPServer', 'queue', 'asyncio'
                   'cgi', 'commands', 'urllib', 'multiprocessing', 'subprocess', 'threading']

    def get(self, request):
        return render(request, 'tool/online_compile.html')

    def post(self, request):
        code = request.POST.get('code')
        output = self.run_code(code)

        return JsonResponse({'output': output})


    def run_code(self, code):
        try:
            for sys_module in self.sys_modules:
                # 判断code里面是否有系统模块,以免危害计算机
                if sys_module in code:
                    raise RuntimeError("module '{}' is not allowed to import".format(sys_module))

            # python编译器位置
            import sys
            import os

            EXEC = os.path.join(os.path.dirname(sys.executable), 'python3.5')

            # logger.info('编译器：{}'.format(EXEC))
            # logger.info('输入的代码为：{}'.format(code))

            # 执行一个进程并捕获输出结果
            # 加上 universal_newlines=True 参数，加上这个参数之后，subprocess 会自动为我们将输出解码为字符串
            output = subprocess.check_output([EXEC, '-c', code],
                                             universal_newlines=True,
                                             stderr=subprocess.STDOUT,
                                             timeout=30)

        except subprocess.CalledProcessError as e:
            output = e.output   # e.output是subprocess模块中错误信息标准输出
            logger.error('输入代码有误：{}'.format(output))


        except subprocess.TimeoutExpired as e:
            output = str(e)
            import re
            output = re.findall('timed out after (.*?) seconds', output)
            output = 'timed out after {} seconds'.format(''.join(output))
            logger.error('代码编译超时：{}'.format(output))


        except RuntimeError as e:
            output = str(e)
            logger.error('不允许导入的模块：{}'.format(output))


        except Exception as e:
            output = str(e)


        return output


    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(CompileView, self).dispatch(*args, **kwargs)