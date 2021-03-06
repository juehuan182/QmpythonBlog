//获取轮播图片元素
let bannerLeftLi = document.querySelectorAll("ul.banner-left-list>li.banner-left-item");
let bannerLeftLiLen = bannerLeftLi.length;

//轮播标题
let bannerLeftTitleLi = document.querySelectorAll("div.banner-left-item-info>p.banner-left-item-title");

//获取左右两个耳朵控制元素
let bannerLeftControlDirectionLi = document.querySelectorAll("ul.banner-left-control-direction>li");
let bannerLeftControlDirectionLen = bannerLeftControlDirectionLi.length;

//获取下面点
let bannerLeftControlLi = document.querySelectorAll("ul.banner-left-control-list>li");
let bannerLeftControlLiLen = bannerLeftControlLi.length;

//初始化
let index = 0; //记录当前位置
bannerLeftLi[0].classList.add("show");
bannerLeftTitleLi[0].classList.add("title-show");
bannerLeftControlLi[0].classList.add("on");

//左右耳朵控制图片切换
for (let i = 0; i < bannerLeftControlDirectionLen; i++) {
    if (i) { //如果为右边耳朵
        bannerLeftControlDirectionLi[i].onclick = function () {
            //清除上一个位置样式
            bannerLeftLi[index].classList.remove("show"); ////点击右耳朵时，将当前清了
            bannerLeftTitleLi[index].classList.remove("title-show");

            bannerLeftControlLi[index].classList.remove("on"); //与上同步
            index++;
            /*向前切换，+1*/

            index %= bannerLeftLiLen; //注意因为li有限，不能无限制加，按li的长为周期,过了一周期又回到原点,需要通过求余

            bannerLeftLi[index].classList.add("show"); //将切换当前的show出来
            bannerLeftTitleLi[index].classList.add("title-show");
            bannerLeftControlLi[index].classList.add("on");
        }
    } else { //左边耳朵
        bannerLeftControlDirectionLi[i].onclick = function () {
            //清除上一个位置样式
            bannerLeftLi[index].classList.remove("show"); ////点击右耳朵时，将当前清了
            bannerLeftTitleLi[index].classList.remove("title-show");
            bannerLeftControlLi[index].classList.remove("on"); //与上同步

            index--; //每点击一次左边位置-1
            if (index < 0) index = bannerLeftLiLen - 1; //如果是第一个减掉之后为负数，则不存在，按周期算到原点之后，再从尾来。

            bannerLeftLi[index].classList.add("show"); //将切换当前的show出来
            bannerLeftTitleLi[index].classList.add("title-show");
            bannerLeftControlLi[index].classList.add("on");
        }
    }
}

/*下面点控制*/
for (let j = 0; j < bannerLeftControlLi; j++) {
    //注意这里在外面给每个设置对应属性值，不能放到事件函数里面，因为函数里面只有点击的时候才触发的
    bannerLeftControlLi[j].setAttribute("current-position", j); //不规范（自定义）的标签属性：getAttribute，setAttribute，removeAttribute
    bannerLeftControlLi[j].onclick = function () {
        //清除上一个位置样式
        bannerLeftLi[index].classList.remove("show"); ////点击右耳朵时，将当前清了
        bannerLeftTitleLi[index].classList.remove("title-show");
        bannerLeftControlLi[index].classList.remove("on"); //与上同步

        index = this.getAttribute("current-position");

        bannerLeftLi[index].classList.add("show"); //将切换当前的show出来
        bannerLeftTitleLi[index].classList.add("title-show");
        bannerLeftControlLi[index].classList.add("on");
    }
}

//自动轮播,顺序与点击右耳切换思路一样

autoSlide(); //首次加载完调用一次

let timer = setInterval(autoSlide, 2000);

function autoSlide() {
    //清除上一个位置样式
    bannerLeftLi[index].classList.remove("show"); ////点击右耳朵时，将当前清了
    bannerLeftTitleLi[index].classList.remove("title-show");
    bannerLeftControlLi[index].classList.remove("on"); //与上同步
    index++;
    /*向前切换，+1*/

    index %= bannerLeftLiLen; //注意因为li有限，不能无限制加，按li的长为周期,过了一周期又回到原点,需要通过求余

    bannerLeftLi[index].classList.add("show"); //将切换当前的show出来
    bannerLeftTitleLi[index].classList.add("title-show");
    bannerLeftControlLi[index].classList.add("on");
}


//当鼠标滑入区域时，不让切换，所以要清除定时器
let homeBannerLeftDiv = document.querySelector("div.home-banner-left");

homeBannerLeftDiv.onmouseenter = function () {
    clearInterval(timer);
};

homeBannerLeftDiv.onmouseleave = function () {
    timer = setInterval(autoSlide, 2000);
};


//加载更多
let moreBtn = document.querySelector(".btn-more");
let articleList = document.querySelector(".article-list");
moreBtn.onclick =  function () {
    //添加一个loading
    moreBtn.innerText = "正在加载";

    //获取绑定在按钮上的页码
    let page = this.getAttribute("data-page");
    //打印值
    //console.log('当前第几页'+page);

    //创建异步对象
    let xhr = new XMLHttpRequest();

    xhr.open('GET','/articles/?page='+ page);

    xhr.send();

    //注册回调函数
    xhr.onreadystatechange = function (ev) {
        if (xhr.readyState == 4 && xhr.status == 200){

            //console.log(typeof (xhr.responseText)); //string
            let res = JSON.parse(xhr.responseText); //object,将一个 JSON 字符串转换为对象

            //获取文章列表
            let articles = res['article_list'];
            if (articles.length > 0){
                //遍历
                articles.forEach(function (one_article) {
                    let articleStr =' <article class="excerpt clearfix">\n' +
                        '    <a href=\"/articles/detail-{0}\.html\">\n' +
                        '        <img src=\"{1}\"/>\n' +
                        '    </a>\n' +
                        '    <div class=\"article-category\">\n' +
                        '        <a href=\"/categories/category-{2}\.html\" target=\"_blank\">\n' +
                        '            {3}\n' +
                        '        </a>\n' +
                        '    </div>\n' +
                        '    <div class=\"right-text\">\n' +
                        '        <div class=\"header\">\n' +
                        '            <h2><a href=\"/articles/detail-{0}\.html\">{4}</a></h2>\n' +
                        '        </div>\n' +
                        '        <p class=\"note\">\n' +
                        '            {5}...\n' +
                        '        </p>\n' +
                        '        <div class=\"meta\">\n' +
                        '            <span class=\"auth\"><i class=\"icon-yonghu1 iconfont\"></i>{6}</span>\n' +
                        '            <span class=\"dtime\"><i class=\"icon-shijian iconfont\"></i>{7}</span>\n' +
                        '            <span class=\"viewnum\"><i class=\"icon-liulan iconfont\"></i>阅读({8})</span>\n' +
                        '            <span class=\"like\"><i class=\"icon-xihuan iconfont\"></i>赞({9})</span>\n' +
                        '        </div>\n' +
                        '    </div>\n' +
                        '</article>';

                    // 格式化发布时间 2018-10-25T23:46:50.882384
                    public_time = dateFormat(one_article.create_time);
                    // console.log(public_time);
                    articleStr = articleStr.format(one_article.id, one_article.cover_img,one_article.category_id, one_article.category__name,
                        one_article.title, one_article.description, one_article.author__username, public_time, one_article.read_num,
                        one_article.like_num);

                    articleList.innerHTML += articleStr;

                });
                moreBtn.innerText = "点击查看更多";
            }else {
                moreBtn.innerText = "我虽放荡，但我也是有底线的！";
            }

            // 点一次 page +1 并绑定到data-page 上
            page++;
            moreBtn.setAttribute("data-page",page);
        }

    };
};






