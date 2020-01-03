'use root';


function Appendzero(obj){
  // console.log(obj)
  if (obj<10){
    return "0" + obj;
  }else{
    return obj;
  }
}


const QINIU = {
  'upload': function (args) {
    let domain = args['domain'];
    let up_token_url = args['uptoken_url'];
    let browser_btn = args['browse_btn'];

    let params = {
      browse_button: browser_btn, //上传选择的点选按钮，**必需**
      runtimes: 'html5,flash,html4', //上传模式，依次退化
      max_file_size: '200mb', //文件最大允许的尺寸
      chunk_size: '4mb', //分块上传时，每片的大小
      uptoken_url: up_token_url, //ajax请求token的url
      domain: domain, //bucket 域名，下载资源时用到，**必需**
      get_new_uptoken: false, //是否每次上传文件都要从业务服务器获取token
      auto_start: true, //如果设置了true,只要选择了图片,就会自动上传
      unique_names: false, //当值为true时会为每个上传的文件生成一个唯一的文件名,为false，上传后文件的key是本地的文件名
      save_key: false,
      multi_selection: false, // 多个选择上传内容
      // filters: {
      //   // 过滤  选择文件的类型,指定上传文件的类型，记住对象要用,隔开
      //   mime_types: [
      //     {title: 'Image files', extensions: 'jpg,gif,png,bmp,jepg,tiff'},
      //     {title: 'Doc files', extensions: 'doc,txt,pdf'},
      //
      //   ]
      // },
      init: {
        'FileUploaded': function (up, file, info) {
          // 每个文件上传成功后，处理相关的事情
          // 其中 info 是文件上传成功后，服务端返回的json，形式如
          // {
          //    "hash": "Fh8xVqod2MQ1mocfI4S4KpRL6D98",
          //    "key": "gogopher.jpg"
          //  }
          // 参考http://developer.qiniu.com/doc/v6/api/overview/up/response/simple-response.html
          if (args['success']) {
            let success = args['success'];
            success(up, file, info);
          }
        },
        'Error': function (up, err, errTip) {
          // 上传出错时，处理相关的事情
          if (args['error']) {
            let error = args['error'];
            error(up, err, errTip);
          }
        },
        'UploadProgress': function (up, file) {
          // 每个文件上传时，处理相关的事情
          if (args['progress']) {
            args['progress'](up, file);
          }
        },
        'UploadComplete': function () {
          // 队列文件处理完毕后，处理相关的事情
          if (args['complete']) {
            args['complete']();
          }
        },
        'Key': function(up, file) {
          // 若想在前端对每个文件的key进行个性化处理，可以配置该函数
         // 该配置必须要在 unique_names: false , save_key: false 时才生效
         //key就是上传的文件路径
         //    console.log(up,file);
            var key = "";
            //获取年月日时分秒
            var date = new Date();
            var year = date.getFullYear();
            var month = date.getMonth()+1;
            var day = date.getDate();
            var hour = date.getHours();
            var minute = date.getMinutes();
            var second = date.getSeconds();
            key = "qmpython/" + year + Appendzero(month) + Appendzero(day) + Appendzero(hour) + Appendzero(minute) + "/" + file.name;
            return key
        }
      }
    };
    // 把args中的参数放到params中去
    for (let key in args) {
      params[key] = args[key];
    }
    return Qiniu.uploader(params);
  }
};
