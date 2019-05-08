var notificationcenterTab = document.querySelectorAll("div.notificationcenter-tab>div");
var contentDiv = document.querySelectorAll(".content>div");
var index = 0;
notificationcenterTab[index].classList.add("tabPaneSelected");
contentDiv[index].style.display = "block";

for (var i=0; i<notificationcenterTab.length;i++){

    notificationcenterTab[i].setAttribute("selected", i);

    notificationcenterTab[i].onclick = function () {
        notificationcenterTab[index].classList.remove("tabPaneSelected");
        contentDiv[index].style.display = "none";

        index = this.getAttribute("selected");

        contentDiv[index].style.display = "block";
        notificationcenterTab[index].classList.add("tabPaneSelected");

    }
}

