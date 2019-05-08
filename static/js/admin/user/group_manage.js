// 1. 获取按钮
$("#btn-add-group").click(function () {
    group_add_or_edit(this);
});


$("#btn-edit-group").click(function () {
    group_add_or_edit(this);
});


function group_add_or_edit(_this) {
    let groupName = $("#group-name").val();
    if (!groupName.trim()){
        swal({
            title: "角色名不能为空！",
            text: '',
            type: "error",
            showCancelButton: false,
            showConfirmButton: false,
            timer: 1500
        });
        return;
    }

    // 判断是否选择权限
    let groupPermissions = $("#group-permissions").val();
    // console.log(groupPermissions);    // ["431", "432", "433"]
    // console.log(typeof (groupPermissions));   // object
    if (groupPermissions == null) {
        swal({
            title: "请分配权限！",
            text: '',
            type: "error",
            showCancelButton: false,
            showConfirmButton: false,
            timer: 1500
        });
        return;
    }

    // 获取groupsId存在表示更新 不存在表示发表
    let groupId = $(_this).data("id") ? $(_this).data("id") : 0;

    let url = groupId ? '/admin/group/' + groupId + '/' : '/admin/group/add/';

    let data = {
        "name": groupName,
        "group_permissions": groupPermissions
    };

    $.ajax({
        url: url,
        data: JSON.stringify(data),
        type: groupId ? "PUT" : "POST",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (res) {
            if (res["code"] === 2) {
                if (groupId){
                        swal({
                            title: "角色修改成功",
                            text: '即将跳转到角色管理页',
                            type: "success",
                            showCancelButton: false,
                            showConfirmButton: false,
                            timer: 1500
                        }, function () {
                            setTimeout(function () {
                                window.location.href = "/admin/group/";
                            },1000);
                        });
                    }else {
                        swal({
                          title: "角色【" + groupName + "】" + "创建成功",
                          text: "即将跳转到角色管理页",
                          type: 'success',
                          showCancelButton: false,
                          showConfirmButton: false,
                          timer: 1500
                        },function () {
                            setTimeout(function () {
                                window.location.href = "/admin/group";
                            },1000);
                        });
                    }
                }else {
                swal({
                    title: res["msg"],
                    text: '',
                    type: "error",
                    showCancelButton: false,
                    showConfirmButton: false,
                    timer: 1500
                });
            }
        },
        error: function (err) {
            swal({
                    title: "服务器错误，请稍后重试！",
                    text: '',
                    type: "error",
                    showCancelButton: false,
                    showConfirmButton: false,
                    timer: 1500
                });
        }
    });
}


// 删除
$(".btn-del").click(function () {
    let _this = this;
    let groupId = $(_this).parent().parent().data("id") ? $(_this).parent().parent().data("id") : '';
    let groupName = $(_this).parent().parent().data("name") ? $(_this).parent().parent().data("name") : '';

    //  获取用户个数
    let num_users = $(_this).parent().parent().find("td:nth-child(3)").html();
    //  判断组成员是否为空
    if (num_users > '0'){
        swal({
            title: "组成员不为空，无法删除！",
            text: '',
            type: "error",
            showCancelButton: false,
            showConfirmButton: false,
            timer: 1500
        });
        return;
    }

    swal({
          title: "您确定要删除【" + groupName + "】角色吗？",
          text: '',
          showCancelButton: true,
          showConfirmButton: true,
          type: "error",
          confirmButtonText: "确认删除",
          cancelButtonText: "取消删除"
        }, function () {
        $.ajax({
                url: "/admin/group/" + groupId + "/",   // url尾部需要添加/
                method: "DELETE",
                dataType: "json",
                success: function success(res) {
                    // console.log(res);
                    if (res["code"] === 2) {
                        swal({
                            title: "角色删除成功",
                            text: '',
                            type: "success",
                            showCancelButton: false,
                            showConfirmButton: false,
                            timer: 1500
                        });
                        $(_this).parent().parent().remove();
                    } else {
                        swal({
                          title: res["msg"],
                          text: '',
                          type: "error",
                          showCancelButton: false,
                          showConfirmButton: false,
                          timer: 1500
                        });
                    }
                },
                error: function error(err) {
                    swal({
                        title: "服务器错误，请稍后重试！",
                        text: '',
                        type: "error",
                        showCancelButton: false,
                        showConfirmButton: false,
                        timer: 1500
                    });
                }
            });
    });
});
