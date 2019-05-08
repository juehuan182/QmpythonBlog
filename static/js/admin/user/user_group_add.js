$("#select-user").on('shown.bs.select', function (e) {
    //获取下拉select里的输入框,提示一下搜索下拉
    $(this).prev().find("input").attr('placeholder',"请输入用户名搜索");
    //绑定一下键盘输入
    $(this).prev().find('input').keyup(function () {
        //为select里的输入框绑定id,方便获取
        $(this).prev().find("input").attr('id',"username");
        var username = $(this).val();
        var dataParams = {
            'username':username
        };
        setTimeout(function () {//延时1秒
            	accountlist('#select-user',dataParams);
        	},500);

    })
});

function accountlist(obj,dataParams){
        $(obj).empty();
        $.ajax({
            url:'/admin/group/user/', //查询url
            type: "POST",
            data:JSON.stringify(dataParams),
            async:false,
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(res){
                if (res['code'] ===2) {
                    var html = '';
                    $.each(res['data']['account_list'],function (index,account) {
                        $(obj).append('<option value="' + account.id + '">' + account.username + '</option>');
                    });
                }else {
                    $(obj).append('<option value="">' + res['msg'] + '</option>');
                    // $(obj).html('<option value="">' + res['msg'] + '</option>');
                    // // $(".no-results").html(res['msg']);
                }
                //刷新select
                $(obj).selectpicker('refresh');
                $(obj).selectpicker('render');
            }
        });
    }


// 创建组员
$("#btn-add-groupUser").click(function (){
    add_edit_groupUser(this);

});
// 更新
$("#btn-edit-groupUser").click(function () {
    add_edit_groupUser(this);
});



function add_edit_groupUser(_this) {
    let userId = $("#select-user").val();
    if (!userId.trim() || userId=== '0'){
        swal({
            title: "请选择用户",
            text: '',
            type: "error",
            showCancelButton: false,
            showConfirmButton: false,
            timer: 1500
        });
        return;
    }

    let groupIds = $("#select-group").val();
    // console.log(groupId); //["1", "3"]

    if (!groupIds){ //null
        swal({
            title: "请选择角色",
            text: '',
            type: "error",
            showCancelButton: false,
            showConfirmButton: false,
            timer: 1500
        });
        return;
    }

    let dataParams = {
        'userId': userId,
        'groupIds': groupIds
    };

    let user_instanceId = $(_this).data('id');

    $.ajax({
        url:  user_instanceId ? '/admin/user_group_edit/' + user_instanceId + "/" : '/admin/user_group/add/',
        type: user_instanceId ? 'PUT' : 'POST',
        data: JSON.stringify(dataParams),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (res) {
            if (res['code'] ===2 ){
                // console.log(res['data']['username'], res['data']['groupsname']);
                if(user_instanceId){
                     swal({
                        title: "用户【" + res['data']['username'] + "】" + " 修改角色【" + res['data']['groupsname'] + "】成功",
                        text: '',
                        type: "success",
                        showCancelButton: false,
                        showConfirmButton: false,
                        timer: 2000
                    }, function () {
                         window.location.href = '/admin/user_group/';
                     });

                }else{
                     swal({
                        title: "用户【" + res['data']['username'] + "】" + " 添加角色【" + res['data']['groupsname'] + "】成功",
                        text: '',
                        type: "success",
                        showCancelButton: false,
                        showConfirmButton: false,
                        timer: 2000
                    }, function () {
                          window.location.href = '/admin/user_group/';
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

};
