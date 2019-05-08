

//是否手机号
function isMobile(phone) {

    var telReg = /^[1][3,4,5,7,8][0-9]{9}$/;     //以1为开头；第二位可为3,4,5,7,8中的任意一位；最后以0-9的9个整数结尾

    if (telReg.test(phone)) {
        return true;
    } else {
        console.log('false');
        return false;
    }
}


//是否QQ
function isQQ(qq) {
    var qqReg = /^[1-9]\d{4,11}$/;   //首位不能是0 ^[1-9] [5,12]位的数字

    if (qqReg.test(qq)) {
        return true;
    } else {
        return false;
    }
}


//验证是否是邮箱
function isEmail(email) {

    var mailReg = /^(\w-*\.*)+@(\w-?)+(\.\w{2,})+$/;   //由字母、数字、下划线、短线“-”、点号“.”组成@为一个域名，域名由字母、数字、短线“-”、域名后缀组成

    if (mailReg.test(email)) {
        return true;
    } else {
        return false;
    }

}


//必须包含至少一位数字和一位字母
function checkPassWord(password) {
    var passwordReg = /^(?![^a-zA-Z]+$)(?!\D+$)/;

    if (!(/^\w{6,16}$/).test(password)) {
        return false;
    }

    if (passwordReg.test(password)) {
        return true;
    } else {
        return false;
    }
}

//检验是否含网址url
function isUrl(url) {// 验证url
    var strRegex = "^((https|http|ftp|rtsp|mms)?://)"
        + "?(([0-9a-zA-Z_!~*'().&=+$%-]+: )?[0-9a-zA-Z_!~*'().&=+$%-]+@)?" // ftp的user@
        + "(([0-9]{1,3}\.){3}[0-9]{1,3}" // IP形式的URL- 199.194.52.184
        + "|" // 允许IP和DOMAIN（域名）
        + "([0-9a-zA-Z_!~*'()-]+\.)*" // 域名- www.
        + "([0-9a-zA-Z][0-9a-zA-Z-]{0,61})?[0-9a-zA-Z]\." // 二级域名
        + "[a-zA-Z]{2,6})" // first level domain- .com or .museum
        + "(:[0-9]{1,4})?" // 端口- :80
        + "((/?)|" // a slash isn't required if there is no file name
        + "(/[0-9a-zA-Z_!~*'().;?:@&=+$,%#-]+)+/?)$";
    var urlRegex = new RegExp(strRegex);

    if (urlRegex.test(url)) {
        return true;
    } else {
        return false;
    }
}

//检验是否带有<script>,防止攻击XSS攻击 参考https://www.cnblogs.com/caizhenbo/p/6836390.html

function safeStr(str) {
    return str.replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

//new_content=；中文;english&article_id=8&parent_id=
//因为传参的时候如果是英文分号;就会隔开为分割，后面的就会截取掉了，所以这里要替换掉；
//&这是用来连接各参数的，如果前面加&就会出现传参&参数值，这样就会使前面的值为空值，而这个值当做另外的参数去了。