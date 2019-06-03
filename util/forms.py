class FormMixin:
    def get_error(self):
        if hasattr(self, 'errors'):  #hasattr() 函数用于判断对象是否包含对应的属性。
            #json格式的数据
            errors_json = self.errors.get_json_data().values()
            # print(error_json) #<QuerySet [{'id': 1, 'name': '首页'}, {'id': 2, 'name': 'python入门'}, {'id': 3, 'name': 'python web'}]>
            err_msg_list = []
            for item in errors_json:
                err_msg_list.append(item[0].get('message'))

            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串
            return err_msg_str
        return None

