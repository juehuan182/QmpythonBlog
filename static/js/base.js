
// 实现移动端菜单下拉效果

// let spanBtn = document.querySelector("·navbar-toggle>nav>ul>li>span");
//
// spanBtn.addEventListener("touchstart", function (e) {
//     e.preventDefault();
//     console.log('click');
// });
//
// $(".mnav>.navbar-toggle>nav>ul>li>span").click(function () {
//
//     console.log('click');
//     // 改变箭头方向，旋转180°
//     $(this).children.css('transform', 'rotate(180deg)');
//     // 显示子菜单
//     $(this).nextSibling.show();
//
// });


$(".mnav > .navbar-toggle > nav > ul > li > span").on("touchstart", function (e) {
    // console.log('touchstart');
    // 改变箭头方向，旋转180°
    if ($(this).children().hasClass("rotate")){
        $(this).children().removeClass("rotate");
    }else {
        $(this).children().addClass("rotate");
    }

    // 显示子菜单
    $(this).next().toggle();
});


// 移动端点击设置切换显示
$(".user-oper").on("touchstart", function (e) {
    $(this).parent().next().toggle();

});


var urlstr = location.href;
var urlstatus = false;
$(".nav > ul > li > a").each(function () {
    // a标签的href值如果能在当前url中存在，且当前href不为/即不是首页，那么高亮
    if ((urlstr).indexOf($(this).attr('href')) > -1 && $(this).attr('href') != '/') {
        $(this).addClass('active');
        urlstatus = true;

    } else {
        $(this).removeClass('active');
    }
});

if (!urlstatus) {
    $(".nav > ul > li > a").eq(0).addClass('active');
}


// 扩展js的功能，可以使用字符串拼接功能
String.prototype.format = function () {
    var args = arguments;
    return this.replace(/\{(\d+)\}/g, function (s, i) {
        return args[i];
    });
};

/************************搜索功能************************/

// 打开搜索页面
let searchButton = document.querySelector('.show-search-box');
searchButton.onclick = function () {
    let searchBox = document.getElementById("search-box");
    searchBox.classList.add('active');
};

// 关闭搜索页面
let closeBox = document.querySelector(".close-search-box");
closeBox.onclick = function () {
    let searchBox = document.getElementById("search-box");
    searchBox.classList.remove('active');
};

// 搜索结果
function searchArticle(keywordObj) {
    var searchKeyValue = keywordObj.value.trim();

    if (searchKeyValue.length === 0) {
        message.showError('请输入要搜索的内容');
        return;
    }
    console.log(searchKeyValue);
    // window.open("/articles/?q=" + searchKeyValue); //打开一个新的浏览器窗口
    window.location.href="/articles/search?q=" + searchKeyValue;
}

let searchBtn = document.querySelector(".btn-search");
searchBtn.onclick = function () {
    let keywordObj = document.querySelector('.search-input .search-keyword');
    searchArticle(keywordObj);
};

function PcSearchArticle(){
    var obj = document.querySelector('.search-bar > .search-keyword');
    searchArticle(obj);

}

function McSearchArticle(){
    var obj = document.querySelector('.m-search-bar > .search-keyword');
    searchArticle(obj);
}


//回到顶部
function goTop() {
    var timer = setInterval(function () {
        var oTop = document.body.scrollTop || document.documentElement.scrollTop;

        if (oTop > 0) {
            document.body.scrollTop = document.documentElement.scrollTop = oTop - 50;

        } else {
            clearInterval(timer);
        }

    }, 10);
}


// 值长度范围
function strLen() {

}

// js获取url传递参数，js获取url？号后面的参数
function getQueryString(name) {
    var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i");
    var r = window.location.search.substr(1).match(reg);
    if (r != null) return decodeURI(r[2]);
    return null;
}


/*======= 日期格式化 =======*/
function dateFormat(time) {
    //console.log(new Date(time));
    // 获取当前的时间戳
    var timeNow = Date.now();
    // 获取发表文章的时间戳
    var TimeStamp = new Date(time).getTime();

    // 转为秒
    var second = (timeNow - TimeStamp) / 1000;
    if (second < 60) {
        return '刚刚'
    } else if (second >= 60 && second < 60 * 60) {
        var minute = Math.floor(second / 60);
        return minute + "分钟前";
    } else if (second >= 60 * 60 && second < 60 * 60 * 24) {
        var hour = Math.floor(second / 60 / 60);
        return hour + "小时前";
        // } else if (second >= 60 * 60 * 24 && second < 60 * 60 * 24 * 30) {
        //     var day = Math.floor(second / 60 / 60 / 24);
        //     return day + "天前";
    } else {
        var date = new Date(TimeStamp);
        var Y = date.getFullYear() + '-';
        var M = (date.getMonth() + 1 < 10 ? '0' + (date.getMonth() + 1) : date.getMonth() + 1) + '-';
        var D = (date.getDate() < 10 ? '0' + (date.getDate()) : date.getDate()) + ' ';
        var h = (date.getHours() < 10 ? '0' + date.getHours() : date.getHours()) + ':';
        var m = (date.getMinutes() < 10 ? '0' + date.getMinutes() : date.getMinutes());
        //console.log(Y + M + D + h + m);
        return Y + M + D + h + m;
    }
}

//获取class->tag-cloud-link
var tags_cloud = document.getElementsByClassName("tag-cloud-link");
var colors = ['#036564', '#EB6841', '#3FB8AF', '#FE4365', '#FC9D9A', '#EDC951','#e77f67', '#f3a683', '#778beb', '#596275', '#f5cd79', '#20bf6b', '#C8C8A9', '#83AF9B'];
for (var i = 0; i < tags_cloud.length; i++) {

    temp = i % colors.length;
    tags_cloud[i].style.background = colors[temp];
}


//统计网站运行时间
function webRunning_time() {
    var startTime = new Date("2018-11-01 00:49:00");
    /*网站开始运行时间*/
    var nowTime = new Date();
    /*获取系统当前时间*/
    var millisecondInterval = (nowTime.getTime() - startTime.getTime());
    /*两个时间差毫秒数*/
    var e_yearsold = millisecondInterval / (12 * 30 * 24 * 60 * 60 * 1000);
    /*年*/
    var yearsold = Math.floor(e_yearsold);
    /*向下取整*/
    var e_monthsold = (e_yearsold - yearsold) * 12;
    /*将求整之后的余数求月*/
    var monthsold = Math.floor(e_monthsold);
    /*月*/
    var e_daysold = (e_monthsold - monthsold) * 30;
    var daysold = Math.floor(e_daysold);
    /*日*/
    var e_hrsold = (e_daysold - daysold) * 24;
    var hrsold = Math.floor(e_hrsold);
    /*时*/
    var e_minsold = (e_hrsold - hrsold) * 60;
    var minsold = Math.floor((e_hrsold - hrsold) * 60);
    /*分*/
    var seconds = Math.floor((e_minsold - minsold) * 60);
    /*秒*/
    var runTimes = document.querySelector(".site-statistics .runTime");


    if (yearsold === 0) {
        yearsold = '';
    }else {
        yearsold = yearsold + "年";
    }

    if (monthsold === 0) {
        monthsold = '';

    }else{
        monthsold = monthsold + "月";
    }

    if (daysold === 0) {
        daysold = '';
    }else {
        daysold = hrsold + "小时";
    }


    runTimes.innerHTML = "<span>" + yearsold + monthsold + daysold + hrsold + "小时" + minsold + "分" + seconds + "秒" +  "</span>";

}

webRunning_time();
/*刚开始先调用这个函数*/
setInterval(webRunning_time, 1000); //隔1秒一直不停地 在执行*/