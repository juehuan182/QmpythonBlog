$(function(){
        $('.sidebar-menu li:not(.treeview) > a').on('click', function(){
            console.log(this.href);
            var $parent = $(this).parent().addClass('active');
            $parent.siblings('.treeview.active').find('> a').trigger('click');
            $parent.siblings().removeClass('active').find('li').removeClass('active');
        });
        $('.sidebar-menu a').each(function(){
            if(this.href === window.location.href){
                $(this).parent().addClass('active')
                        .closest('.treeview-menu').addClass('.menu-open')
                        .closest('.treeview').addClass('active');
            }
        });


    });
