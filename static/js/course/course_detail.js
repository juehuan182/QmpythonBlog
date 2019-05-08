// 动态获取

var course_data = document.querySelector(".course-data");
var sVideoUrl = course_data.getAttribute("data-video-url");
var sCoverUrl = course_data.getAttribute("data-cover-url");

var player = cyberplayer("course-video").setup({
    width: '100%', // 高度
    height: 650,  // 宽度
    file: sVideoUrl, // 地址
    image: sCoverUrl,  // 预览图
    autostart: false,  // 是否自动播放
    stretching: "uniform", // 缩放方式，缩放方式分为：1.none:不缩放；2.uniform:添加黑边缩放；3. exactfit:改变宽高比缩到最大；4.fill:剪切并缩放到最大（默认方式为uniform）
    repeat: false,
    volume: 70, // 音量 0 -100
    controls: true,  // 控制条显示
    tokenEncrypt: true,
    ak: 'bb63b5e8f7624bc89999fc23d5471371'  // Access Key ID
});

// 播放前准备
player.on('beforePlay', (e) => {
    // 判断文件是否加密
    if(!/m3u8/.test(e.file)){
      return false;
    }
    $.get({
      "url": "/course/token/",
      "data": {
        "video_url": videoUrl,
      },
      "success": res => {
        let token = res['token'];
        player.setToken(e.file, token)
      },
      "error": err => {
        console.log(err);
        console.log(err.status + "====" + err.statusText);

      }
    });
  });
