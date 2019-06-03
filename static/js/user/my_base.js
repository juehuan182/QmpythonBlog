var urlstr = location.href;
var urlstatus = false;
$("ul.user-menu > li > a").each(function () {
    // a标签的href值如果能在当前url中存在，那么高亮
    if ((urlstr).indexOf($(this).attr('href')) > -1 ) {
        $(this).parent().addClass('active');
        urlstatus = true;

    } else {
        $(this).parent().removeClass('active');
    }
});

if (!urlstatus) {
    $("ul.user-menu > li").eq(0).addClass('active');
}

