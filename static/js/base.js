
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
    console.log(new Date(time));
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
        console.log(Y + M + D + h + m);
        return Y + M + D + h + m;
    }
}

//获取class->tag-cloud-link
var tags_cloud = document.getElementsByClassName("tag-cloud-link");
var colors = ['#036564', '#EB6841', '#3FB8AF', '#FE4365', '#FC9D9A', '#EDC951', '#C8C8A9', '#83AF9B'];
for (var i = 0; i < tags_cloud.length; i++) {

    temp = i % colors.length;
    tags_cloud[i].style.background = colors[temp];
}
